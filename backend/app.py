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
  - Gracefully degrades when heavy ML models can't load (e.g., low-RAM servers)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import os
import time
import threading

# ── Check if we're in a low-memory environment ───────────────────
LOW_MEMORY_MODE = os.environ.get('LOW_MEMORY_MODE', '').lower() in ('1', 'true', 'yes')

# ── Try to import torch (optional for low-memory deployments) ────
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("[Init] PyTorch not available — running without local ML models")

# ── Try to import detection modules (graceful degradation) ───────
EYE_AVAILABLE = False
HEAD_AVAILABLE = False
MOBILE_AVAILABLE = False
POSE_AVAILABLE = False

if not LOW_MEMORY_MODE:
    try:
        from eye_movement_opencv import process_eye_movement
        EYE_AVAILABLE = True
        print("[Init] Eye movement detection loaded")
    except Exception as e:
        print(f"[Init] Eye movement not available: {e}")

    try:
        from head_pose_opencv import process_head_pose
        HEAD_AVAILABLE = True
        print("[Init] Head pose detection loaded")
    except Exception as e:
        print(f"[Init] Head pose not available: {e}")

    try:
        from mobile_detection import process_mobile_detection
        MOBILE_AVAILABLE = True
        print("[Init] Mobile detection loaded")
    except Exception as e:
        print(f"[Init] Mobile detection not available: {e}")

    try:
        from pose_detection import process_pose_detection
        POSE_AVAILABLE = True
        print("[Init] YOLO-Pose detection loaded")
    except Exception as e:
        print(f"[Init] Pose detection not available: {e}")
else:
    print("[Init] LOW_MEMORY_MODE enabled — skipping all local ML models")

# ── Gemini is always available (cloud API, no local RAM needed) ──
try:
    from gemini_analysis import analyze_frame_with_gemini
    GEMINI_AVAILABLE = True
    print("[Init] Gemini analysis loaded")
except Exception as e:
    GEMINI_AVAILABLE = False
    print(f"[Init] Gemini analysis not available: {e}")

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
        
        # ── If no local ML models, use Gemini-only mode ──────────
        if not (EYE_AVAILABLE or HEAD_AVAILABLE or MOBILE_AVAILABLE):
            # Gemini-only mode: send frame directly to Gemini for analysis
            detection_context = {
                'head_direction': 'Unknown',
                'gaze_direction': 'Unknown',
                'mobile_detected': False,
                'behavior_state': 'Unknown',
                'pose_alerts': [],
            }
            
            gemini_result = {'risk': 'N/A', 'summary': 'Local ML models not loaded', 
                           'gestures': 'N/A', 'integrity_score': None, 
                           'status_label': 'N/A', 'available': False}
            if GEMINI_AVAILABLE:
                gemini_result = analyze_frame_with_gemini(frame, detection_context)
            
            return jsonify({
                'status': 'detecting',
                'head_direction': 'N/A (cloud mode)',
                'gaze_direction': 'N/A (cloud mode)',
                'mobile_detected': False,
                'mobile_boxes': [],
                'calibrated': True,
                'behavior_state': gemini_result.get('status_label', 'Normal'),
                'pose_alerts': [],
                'person_count': 0,
                'mode': 'gemini-only',
                'gemini': {
                    'risk': gemini_result.get('risk', 'N/A'),
                    'summary': gemini_result.get('summary', ''),
                    'gestures': gemini_result.get('gestures', 'None detected'),
                    'integrity_score': gemini_result.get('integrity_score'),
                    'status_label': gemini_result.get('status_label', 'N/A'),
                    'available': gemini_result.get('available', False),
                }
            })
        
        # ── Full detection mode (local ML models available) ──────
        if calibration_start_time is None:
            calibration_start_time = current_time
            calibration_samples = []
            calibration_done = False
            
        # Still in calibration period
        if not calibration_done and current_time - calibration_start_time <= 5:
            if HEAD_AVAILABLE:
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
        
        # ── Run all available detections ──────────────────────────
        gaze_direction = "Looking Center"
        head_direction = "Looking at Screen"
        mobile_detected = False
        mobile_boxes = []
        
        use_no_grad = TORCH_AVAILABLE
        
        if use_no_grad:
            with torch.no_grad():
                if EYE_AVAILABLE:
                    frame, gaze_direction = process_eye_movement(frame)
                if HEAD_AVAILABLE:
                    frame, head_direction = process_head_pose(frame, calibrated_angles)
                if MOBILE_AVAILABLE:
                    frame, mobile_detected, mobile_boxes = process_mobile_detection(frame)
        else:
            if EYE_AVAILABLE:
                frame, gaze_direction = process_eye_movement(frame)
            if HEAD_AVAILABLE:
                frame, head_direction = process_head_pose(frame, calibrated_angles)
            if MOBILE_AVAILABLE:
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
                if use_no_grad:
                    with torch.no_grad():
                        _, pose_alerts, person_count, pose_boxes = process_pose_detection(frame)
                else:
                    _, pose_alerts, person_count, pose_boxes = process_pose_detection(frame)
            except Exception as e:
                print(f"[Pose] Error: {e}")
        
        # ── State Machine: classify behavior ──
        behavior_state = classify_behavior(
            head_direction, gaze_direction, mobile_detected, pose_alerts
        )
        
        # ── Gemini: trigger if suspicious for >3s ──
        detection_context = {
            'head_direction': head_direction,
            'gaze_direction': gaze_direction,
            'mobile_detected': mobile_detected,
            'behavior_state': behavior_state,
            'pose_alerts': pose_alerts,
        }
        
        force_gemini = should_trigger_gemini(behavior_state)
        
        gemini_result = {'risk': 'N/A', 'summary': '', 'gestures': 'None detected',
                        'integrity_score': None, 'status_label': 'N/A', 'available': False}
        if GEMINI_AVAILABLE:
            gemini_result = analyze_frame_with_gemini(frame, detection_context)
        
        # Clean up CUDA cache periodically
        if TORCH_AVAILABLE and torch.cuda.is_available():
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
            'eye_tracking': EYE_AVAILABLE,
            'head_pose': HEAD_AVAILABLE,
            'mobile_detection': MOBILE_AVAILABLE,
            'pose_detection': POSE_AVAILABLE,
            'gemini_api': GEMINI_AVAILABLE,
            'low_memory_mode': LOW_MEMORY_MODE,
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
    print(f"  Eye Tracking: {'Enabled' if EYE_AVAILABLE else 'Disabled'}")
    print(f"  Head Pose: {'Enabled' if HEAD_AVAILABLE else 'Disabled'}")
    print(f"  Mobile Detection: {'Enabled' if MOBILE_AVAILABLE else 'Disabled'}")
    print(f"  YOLO-Pose: {'Enabled' if POSE_AVAILABLE else 'Disabled'}")
    print(f"  Gemini API: {'Enabled' if GEMINI_AVAILABLE else 'Disabled (set GEMINI_API_KEY)'}")
    print(f"  Low Memory Mode: {'Yes' if LOW_MEMORY_MODE else 'No'}")
    app.run(host='0.0.0.0', port=port, debug=True)
