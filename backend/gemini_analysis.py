"""
Gemini Vision API integration for intelligent cheating detection.

Uses Gemini 1.5 Flash (or 2.0 Flash) as a secondary verification "Judge."
When YOLO flags suspicious behavior, Gemini analyzes the full scene context
to reduce false positives and provide an Integrity Score (0–100).

Non-blocking: runs analysis in a background thread with a cooldown.
"""

import os
import re
import time
import threading
import cv2
import numpy as np

try:
    import google.generativeai as genai
    from PIL import Image
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# ── Configure Gemini ───────────────────────────────────────────────
_api_key = os.environ.get('GEMINI_API_KEY', '')
_gemini_model = None

if GEMINI_AVAILABLE and _api_key:
    genai.configure(api_key=_api_key)
    _gemini_model = genai.GenerativeModel(
        'gemini-2.0-flash',
        system_instruction=(
            "You are an Expert Exam Proctor AI. You will receive a video frame "
            "and a list of detections from YOLO (e.g., 'Person 1: Looking Around', "
            "'Object: Cell Phone'). Your task is to provide a final 'Integrity Score' "
            "from 0 to 100.\n\n"
            "Evaluation Criteria:\n"
            "- Writing (90-100): Head is down, hands are visible on the paper, no prohibited objects.\n"
            "- Suspicious (40-70): Frequent looking at neighbors, hands under the desk, "
            "or body angled away from the paper.\n"
            "- Cheating (0-30): Clear view of a mobile device, exchanging papers, "
            "or reading from a hidden 'cheat sheet'.\n\n"
            "IMPORTANT: Also detect hand gestures. If the student is making any unusual "
            "hand signals, pointing, waving, or using gestures to communicate with someone, "
            "flag that as suspicious.\n\n"
            "Output Format (EXACTLY 4 lines, nothing else):\n"
            "STATUS: [Writing|Suspicious|Cheating|Normal]\n"
            "CONFIDENCE: [0-100]%\n"
            "GESTURES: [None detected|Description of gesture]\n"
            "REASON: [Short 1-sentence explanation]"
        )
    )
    print(f"[Gemini] Configured with model gemini-2.0-flash (Expert Proctor mode)")
else:
    if not GEMINI_AVAILABLE:
        print("[Gemini] google-generativeai not installed — Gemini analysis disabled")
    elif not _api_key:
        print("[Gemini] GEMINI_API_KEY not set — Gemini analysis disabled")

# ── Analysis state ─────────────────────────────────────────────────
_cache = {
    'result': None,
    'timestamp': 0,
}
_cache_lock = threading.Lock()
_analysis_thread = None

ANALYSIS_COOLDOWN = 5  # seconds between API calls


def _status_to_risk(status: str) -> str:
    """Convert a STATUS label to a risk level."""
    status = status.upper().strip()
    if status in ('CHEATING',):
        return 'HIGH'
    elif status in ('SUSPICIOUS',):
        return 'MEDIUM'
    else:
        return 'LOW'


def _parse_response(text: str) -> dict:
    """Parse Gemini's structured proctor response into a dict."""
    result = {
        'risk': 'UNKNOWN',
        'summary': '',
        'details': '',
        'gestures': 'None detected',
        'integrity_score': None,
        'status_label': 'Normal',
        'available': True,
        'raw': text
    }

    for line in text.strip().split('\n'):
        line = line.strip()
        upper = line.upper()

        if upper.startswith('STATUS:'):
            label = line.split(':', 1)[1].strip()
            result['status_label'] = label
            result['risk'] = _status_to_risk(label)

        elif upper.startswith('CONFIDENCE:'):
            conf_str = line.split(':', 1)[1].strip().replace('%', '')
            try:
                score = int(re.search(r'\d+', conf_str).group())
                result['integrity_score'] = max(0, min(100, score))
            except (ValueError, AttributeError):
                result['integrity_score'] = None

        elif upper.startswith('GESTURES:') or upper.startswith('GESTURE:'):
            result['gestures'] = line.split(':', 1)[1].strip()

        elif upper.startswith('REASON:'):
            result['summary'] = line.split(':', 1)[1].strip()

        # Legacy fallback for old-format responses
        elif upper.startswith('RISK:'):
            risk_val = line.split(':', 1)[1].strip().upper()
            for level in ['HIGH', 'MEDIUM', 'LOW']:
                if level in risk_val:
                    result['risk'] = level
                    break

        elif upper.startswith('SUMMARY:'):
            if not result['summary']:
                result['summary'] = line.split(':', 1)[1].strip()

        elif upper.startswith('DETAILS:'):
            result['details'] = line.split(':', 1)[1].strip()

    return result


def _build_detection_context(detections: dict) -> str:
    """Build a text summary of current YOLO/OpenCV detections for Gemini."""
    lines = ["Current YOLO/OpenCV detections:"]

    head = detections.get('head_direction', 'Unknown')
    gaze = detections.get('gaze_direction', 'Unknown')
    mobile = detections.get('mobile_detected', False)
    behavior = detections.get('behavior_state', 'Unknown')
    pose_alerts = detections.get('pose_alerts', [])

    lines.append(f"- Head Direction: {head}")
    lines.append(f"- Gaze Direction: {gaze}")
    lines.append(f"- Mobile Phone Detected: {'Yes' if mobile else 'No'}")
    lines.append(f"- Behavior State: {behavior}")

    if pose_alerts:
        lines.append(f"- Pose Alerts: {', '.join(pose_alerts)}")

    return '\n'.join(lines)


def _run_analysis(frame_copy, detections: dict):
    """Internal: run Gemini analysis in background thread."""
    global _cache
    try:
        # Convert to PIL Image (resized for speed / token savings)
        rgb = cv2.cvtColor(frame_copy, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)

        max_dim = 512
        w, h = pil_img.size
        if max(w, h) > max_dim:
            scale = max_dim / max(w, h)
            pil_img = pil_img.resize((int(w * scale), int(h * scale)))

        # Build context string from current detections
        context = _build_detection_context(detections)

        prompt = (
            f"{context}\n\n"
            "Analyze this exam frame. Verify whether the detected behaviors are "
            "actually suspicious or could be normal behavior (e.g., stretching, "
            "thinking, adjusting glasses). Also check for any hand gestures or "
            "signals the student might be using to communicate.\n\n"
            "Provide your response in the exact format specified."
        )

        response = _gemini_model.generate_content(
            [prompt, pil_img],
            generation_config=genai.GenerationConfig(
                max_output_tokens=250,
                temperature=0.1,
            )
        )

        parsed = _parse_response(response.text)

        with _cache_lock:
            _cache['result'] = parsed
            _cache['timestamp'] = time.time()

        print(f"[Gemini] Proctor: STATUS={parsed['status_label']} | "
              f"RISK={parsed['risk']} | SCORE={parsed['integrity_score']} | "
              f"GESTURES={parsed['gestures']} | {parsed['summary']}")

    except Exception as e:
        error_result = {
            'risk': 'ERROR',
            'summary': f'Analysis failed: {str(e)[:80]}',
            'details': '',
            'gestures': 'N/A',
            'integrity_score': None,
            'status_label': 'Error',
            'available': True,
        }
        with _cache_lock:
            _cache['result'] = error_result
            _cache['timestamp'] = time.time()
        print(f"[Gemini] Error: {e}")


def analyze_frame_with_gemini(frame, detections: dict = None):
    """Request Gemini analysis of a frame. Non-blocking — runs in background thread.
    
    Args:
        frame: CV2 BGR image
        detections: dict with current YOLO/OpenCV detection results for context
    
    Returns the latest cached result immediately. Kicks off a new analysis
    if the cooldown has elapsed.
    """
    global _analysis_thread

    if detections is None:
        detections = {}

    if not GEMINI_AVAILABLE or _gemini_model is None:
        return {
            'risk': 'N/A',
            'summary': 'Gemini not configured',
            'details': 'Set GEMINI_API_KEY env var and install google-generativeai',
            'gestures': 'N/A',
            'integrity_score': None,
            'status_label': 'N/A',
            'available': False
        }

    current_time = time.time()

    with _cache_lock:
        elapsed = current_time - _cache['timestamp']
        cached = _cache['result']

    # If cooldown hasn't elapsed, return cached result
    if elapsed < ANALYSIS_COOLDOWN and cached is not None:
        return cached

    # If a thread is already running, return cached (or placeholder)
    if _analysis_thread is not None and _analysis_thread.is_alive():
        return cached or {
            'risk': 'LOADING',
            'summary': 'Analysis in progress...',
            'details': '',
            'gestures': 'Analyzing...',
            'integrity_score': None,
            'status_label': 'Loading',
            'available': True
        }

    # Kick off background analysis
    frame_copy = frame.copy()
    _analysis_thread = threading.Thread(
        target=_run_analysis,
        args=(frame_copy, detections),
        daemon=True
    )
    _analysis_thread.start()

    return cached or {
        'risk': 'LOADING',
        'summary': 'First analysis starting...',
        'details': '',
        'gestures': 'Analyzing...',
        'integrity_score': None,
        'status_label': 'Loading',
        'available': True
    }
