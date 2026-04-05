"""
Master Proctor Flask API — EduSecure
=====================================

Pipeline:
  1. YOLO-Pose (head/shoulder orientation) + MediaPipe (gaze, head pose)
  2. YOLOv12l (mobile/cheat-sheet detection)
  3. State Machine labels behavior: Writing | Looking Around | Using Phone | Suspicious | Normal
  4. If "Suspicious" for >3s, Gemini 1.5/2.0 Flash verifies the scene (async, non-blocking)

Deployment:
  - Binds to 0.0.0.0:PORT (default 8000)
  - Uses torch.no_grad() for inference
  - Headless: no cv2.imshow, only cv2.imencode for web streaming
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import os
import time
import threading
import torch

from eye_movement_opencv import process_eye_movement
from head_pose_opencv import process_head_pose
from mobile_detection import process_mobile_detection
from gemini_analysis import analyze_frame_with_gemini

# Optional: YOLO-Pose for body-level gesture analysis
try:
    from pose_detection import process_pose_detection
    POSE_AVAILABLE = True
    print("[Pose] YOLO-Pose detection loaded")
except ImportError:
    POSE_AVAILABLE = False
    print("[Pose] pose_detection not available, skipping body pose analysis")

# Set static_folder to the dist folder of the React/Vite app
app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
CORS(app)  # Enable CORS for all routes

# ── Global variables for calibration ──────────────────────────────
calibrated_angles = None
calibration_start_time = None
calibration_samples = []
calibration_done = False

# ── State Machine for behavior classification ─────────────────────
# Tracks suspicious behavior duration to decide when to trigger Gemini
_behavior_state = {
    'current': 'Normal',
    'suspicious_start': None,       # When suspicious behavior began
    'gemini_triggered': False,      # Whether Gemini has been asked for this episode
    'last_gemini_trigger': 0,       # Timestamp of last Gemini trigger
}
_behavior_lock = threading.Lock()

SUSPICIOUS_THRESHOLD_SECONDS = 3  # How long before triggering Gemini
GEMINI_RETRIGGER_COOLDOWN = 10    # Min seconds between Gemini triggers


def classify_behavior(head_direction, gaze_direction, mobile_detected, pose_alerts=None):
    """
    State machine: classify the student's behavior based on all detections.
    
    Returns one of:
      'Writing'       — Head down, focused, no issues
      'Looking Around' — Head/gaze off-screen
      'Using Phone'   — Mobile detected
      'Suspicious'    — Multiple signals combined
      'Normal'        — Everything looks fine
    """
    if pose_alerts is None:
        pose_alerts = []

    # Priority 1: Phone detected → immediate flag
    if mobile_detected:
        return 'Using Phone'

    # Count how many things are "off"
    issues = 0

    is_looking_away_head = head_direction not in ('Looking at Screen', 'Looking Down')
    is_looking_away_gaze = gaze_direction not in ('Looking Center', 'Looking at Screen')
    has_pose_alert = any(a in pose_alerts for a in ['HEAD_TURNED', 'LEANING'])

    if is_looking_away_head:
        issues += 1
    if is_looking_away_gaze:
        issues += 1
    if has_pose_alert:
        issues += 1

    # Priority 2: Multiple issues → suspicious
    if issues >= 2:
        return 'Suspicious'

    # Priority 3: Head turned significantly
    if is_looking_away_head and head_direction in ('Looking Left', 'Looking Right'):
        return 'Looking Around'

    # Priority 4: Head down + gaze center → likely writing
    if head_direction == 'Looking Down' and not is_looking_away_gaze:
        return 'Writing'

    # Default
    return 'Normal'


def should_trigger_gemini(behavior_state):
    """
    Check if we should send a frame to Gemini based on the state machine.
    Only triggers if suspicious behavior persists for >3 seconds.
    """
    global _behavior_state

    current_time = time.time()

    with _behavior_lock:
        # Reset if behavior goes back to normal
        if behavior_state in ('Normal', 'Writing'):
            _behavior_state['suspicious_start'] = None
            _behavior_state['gemini_triggered'] = False
            return False

        # Start timing suspicious behavior
        if _behavior_state['suspicious_start'] is None:
            _behavior_state['suspicious_start'] = current_time
            return False

        elapsed = current_time - _behavior_state['suspicious_start']
        cooldown_elapsed = current_time - _behavior_state['last_gemini_trigger']

        # Trigger Gemini if suspicious for >3s and cooldown has passed
        if elapsed >= SUSPICIOUS_THRESHOLD_SECONDS and cooldown_elapsed >= GEMINI_RETRIGGER_COOLDOWN:
            _behavior_state['gemini_triggered'] = True
            _behavior_state['last_gemini_trigger'] = current_time
            _behavior_state['suspicious_start'] = None  # Reset for next episode
            return True

        return False


@app.route('/detect_base64', methods=['POST'])
def detect_base64():
    global calibrated_angles, calibration_start_time, calibration_samples, calibration_done
    
    try:
        # Get base64 image data from request
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        image_data = base64.b64decode(data['image'])
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Could not decode image'}), 400
        
        current_time = time.time()
        
        if calibration_start_time is None:
            calibration_start_time = current_time
            calibration_samples = []
            calibration_done = False
            
        # Still in calibration period
        if not calibration_done and current_time - calibration_start_time <= 5:
            _, angles = process_head_pose(frame, None)
            if angles and isinstance(angles, (tuple, list)) and len(angles) == 3:
                calibration_samples.append(angles)
                
            remaining = max(0, 5 - (current_time - calibration_start_time))
            sample_count = len(calibration_samples)
            
            return jsonify({
                'status': 'calibrating',
                'message': f'Calibrating... Keep your head straight ({int(remaining)}s, {sample_count} samples)',
                'head_direction': 'Looking at Screen',
                'gaze_direction': 'Looking Center',
                'mobile_detected': False,
                'behavior_state': 'Calibrating',
                'gemini': {'available': False}
            })
        
        # Finalize calibration once
        if not calibration_done:
            calibration_done = True
            if len(calibration_samples) > 0:
                avg_pitch = float(np.median([s[0] for s in calibration_samples]))
                avg_yaw = float(np.median([s[1] for s in calibration_samples]))
                avg_roll = float(np.median([s[2] for s in calibration_samples]))
                calibrated_angles = (avg_pitch, avg_yaw, avg_roll)
                print(f"Calibration complete! Samples: {len(calibration_samples)}, "
                      f"Baseline: pitch={avg_pitch:.1f}, yaw={avg_yaw:.1f}, roll={avg_roll:.1f}")
            else:
                calibrated_angles = (0.0, 0.0, 0.0)
                print("Calibration: no samples collected, using zero baseline")
        
        # ── Run all detections with no_grad for memory efficiency ──
        with torch.no_grad():
            frame, gaze_direction = process_eye_movement(frame)
            frame, head_direction = process_head_pose(frame, calibrated_angles)
            frame, mobile_detected, mobile_boxes = process_mobile_detection(frame)
        
        # Safety: ensure head_direction is a string
        if not isinstance(head_direction, str):
            head_direction = "Looking at Screen"
        
        # ── Optional: YOLO-Pose body analysis ──
        pose_alerts = []
        person_count = 0
        pose_boxes = []
        if POSE_AVAILABLE:
            try:
                with torch.no_grad():
                    _, pose_alerts, person_count, pose_boxes = process_pose_detection(frame)
            except Exception as e:
                print(f"[Pose] Error: {e}")
        
        # ── State Machine: classify behavior ──
        behavior_state = classify_behavior(
            head_direction, gaze_direction, mobile_detected, pose_alerts
        )
        
        # ── Gemini: trigger if suspicious for >3s ──
        # Build detection context for Gemini
        detection_context = {
            'head_direction': head_direction,
            'gaze_direction': gaze_direction,
            'mobile_detected': mobile_detected,
            'behavior_state': behavior_state,
            'pose_alerts': pose_alerts,
        }
        
        # Always try to get cached Gemini result; trigger new analysis if warranted
        force_gemini = should_trigger_gemini(behavior_state)
        
        # Call Gemini (non-blocking): always returns cached or triggers new
        if force_gemini or behavior_state in ('Using Phone', 'Suspicious'):
            gemini_result = analyze_frame_with_gemini(frame, detection_context)
        else:
            # Still return cached result if available
            gemini_result = analyze_frame_with_gemini(frame, detection_context)
        
        # Clean up CUDA cache periodically
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        # Return detection results
        return jsonify({
            'status': 'detecting',
            'head_direction': head_direction,
            'gaze_direction': gaze_direction,
            'mobile_detected': mobile_detected,
            'mobile_boxes': mobile_boxes,
            'calibrated': calibrated_angles is not None,
            'behavior_state': behavior_state,
            'pose_alerts': pose_alerts,
            'person_count': person_count,
            'gemini': {
                'risk': gemini_result.get('risk', 'N/A'),
                'summary': gemini_result.get('summary', ''),
                'gestures': gemini_result.get('gestures', 'None detected'),
                'integrity_score': gemini_result.get('integrity_score'),
                'status_label': gemini_result.get('status_label', 'N/A'),
                'available': gemini_result.get('available', False),
            }
        })
        
    except Exception as e:
        print(f"Error in detection: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/reset_calibration', methods=['POST'])
def reset_calibration():
    global calibrated_angles, calibration_start_time, calibration_samples, calibration_done
    calibrated_angles = None
    calibration_start_time = None
    calibration_samples = []
    calibration_done = False
    
    # Also reset the behavior state machine
    with _behavior_lock:
        _behavior_state['current'] = 'Normal'
        _behavior_state['suspicious_start'] = None
        _behavior_state['gemini_triggered'] = False
    
    return jsonify({'status': 'calibration_reset'})

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Master Proctor API is running',
        'features': {
            'pose_detection': POSE_AVAILABLE,
            'gemini_api': bool(os.environ.get('GEMINI_API_KEY')),
        }
    })

# Serve React App
@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def serve_static(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return app.send_static_file(path)
    else:
        return app.send_static_file('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting Master Proctor API Server on port {port}...")
    print(f"  YOLO-Pose: {'Enabled' if POSE_AVAILABLE else 'Disabled'}")
    print(f"  Gemini API: {'Enabled' if os.environ.get('GEMINI_API_KEY') else 'Disabled (set GEMINI_API_KEY)'}")
    app.run(host='0.0.0.0', port=port, debug=True)
