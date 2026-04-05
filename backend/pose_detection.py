import cv2
import numpy as np
import os
import torch
from ultralytics import YOLO

# Standard COCO model for high-accuracy standard object detection
cache_dir = os.environ.get("RENDER_DISK_PATH", os.environ.get("TMPDIR", "/tmp"))
if os.name == "nt": # Windows fallback
    cache_dir = os.path.dirname(os.path.abspath(__file__))

# Load extra-large YOLO Pose model (~110MB)
pose_model_path = os.path.join(cache_dir, 'yolo11x-pose.pt')
pose_model = YOLO(pose_model_path)
device = "cuda" if torch.cuda.is_available() else "cpu"
pose_model.to(device)

# ── COCO Keypoint indices ──────────────────────────────────────────
NOSE = 0
LEFT_EYE = 1
RIGHT_EYE = 2
LEFT_EAR = 3
RIGHT_EAR = 4
LEFT_SHOULDER = 5
RIGHT_SHOULDER = 6
LEFT_ELBOW = 7
RIGHT_ELBOW = 8
LEFT_WRIST = 9
RIGHT_WRIST = 10
LEFT_HIP = 11
RIGHT_HIP = 12

# Skeleton connections for drawing
SKELETON_CONNECTIONS = [
    (NOSE, LEFT_EYE), (NOSE, RIGHT_EYE),
    (LEFT_EYE, LEFT_EAR), (RIGHT_EYE, RIGHT_EAR),
    (LEFT_SHOULDER, RIGHT_SHOULDER),
    (LEFT_SHOULDER, LEFT_ELBOW), (LEFT_ELBOW, LEFT_WRIST),
    (RIGHT_SHOULDER, RIGHT_ELBOW), (RIGHT_ELBOW, RIGHT_WRIST),
    (LEFT_SHOULDER, LEFT_HIP), (RIGHT_SHOULDER, RIGHT_HIP),
    (LEFT_HIP, RIGHT_HIP),
]

# Colors
COLOR_SAFE = (0, 200, 100)       # Green
COLOR_WARNING = (0, 180, 255)    # Orange
COLOR_DANGER = (0, 0, 255)       # Red
COLOR_SKELETON = (200, 200, 200) # Light gray


def _is_valid(kp, min_conf=0.4):
    """Check if a keypoint is valid (detected with sufficient confidence)."""
    return len(kp) >= 3 and kp[2] > min_conf


def analyze_single_pose(kps):
    """Analyze one person's keypoints for suspicious exam behavior.
    
    Returns a list of alert strings.
    """
    alerts = []
    
    nose = kps[NOSE]
    l_shoulder = kps[LEFT_SHOULDER]
    r_shoulder = kps[RIGHT_SHOULDER]
    l_ear = kps[LEFT_EAR]
    r_ear = kps[RIGHT_EAR]
    l_wrist = kps[LEFT_WRIST]
    r_wrist = kps[RIGHT_WRIST]
    l_elbow = kps[LEFT_ELBOW]
    r_elbow = kps[RIGHT_ELBOW]

    # ── 1. Head Turn Detection ─────────────────────────────────────
    if _is_valid(nose) and _is_valid(l_shoulder) and _is_valid(r_shoulder):
        shoulder_cx = (l_shoulder[0] + r_shoulder[0]) / 2
        shoulder_w = abs(l_shoulder[0] - r_shoulder[0])
        if shoulder_w > 0:
            turn_ratio = abs(nose[0] - shoulder_cx) / shoulder_w
            if turn_ratio > 0.55:
                alerts.append("HEAD_TURNED")

    # ── 2. Looking Down (hidden notes / phone in lap) ──────────────
    if _is_valid(nose) and _is_valid(l_shoulder) and _is_valid(r_shoulder):
        shoulder_cy = (l_shoulder[1] + r_shoulder[1]) / 2
        shoulder_w = abs(l_shoulder[0] - r_shoulder[0])
        if shoulder_w > 0:
            down_ratio = (nose[1] - shoulder_cy) / shoulder_w
            if down_ratio > 0.7:
                alerts.append("LOOKING_DOWN")

    # ── 3. Body Leaning (toward neighbor) ──────────────────────────
    if _is_valid(l_shoulder) and _is_valid(r_shoulder):
        shoulder_angle = np.degrees(np.arctan2(
            r_shoulder[1] - l_shoulder[1],
            r_shoulder[0] - l_shoulder[0]
        ))
        if abs(shoulder_angle) > 18:
            alerts.append("LEANING")

    # ── 4. Hand Raised (passing notes / signaling) ─────────────────
    if _is_valid(l_wrist) and _is_valid(l_shoulder):
        if l_wrist[1] < l_shoulder[1] - 40:
            alerts.append("HAND_RAISED_L")
    if _is_valid(r_wrist) and _is_valid(r_shoulder):
        if r_wrist[1] < r_shoulder[1] - 40:
            alerts.append("HAND_RAISED_R")

    # ── 5. Ear visibility asymmetry (extreme head turn) ────────────
    if _is_valid(l_ear) and _is_valid(r_ear):
        ear_conf_diff = abs(l_ear[2] - r_ear[2])
        if ear_conf_diff > 0.4:
            if "HEAD_TURNED" not in alerts:
                alerts.append("HEAD_TURNED")

    return alerts


def process_pose_detection(frame):
    """Run YOLO Pose on the frame, annotate, and return alerts.
    
    Returns:
        frame:        Annotated frame with skeletons and bounding boxes
        all_alerts:   List of alert strings across all detected persons
        person_count: Number of persons detected
        pose_boxes:   List of normalized bounding boxes for each person
    """
    results = pose_model(frame, verbose=False, conf=0.3)
    h, w = frame.shape[:2]
    all_alerts = []
    person_count = 0
    pose_boxes = []

    for result in results:
        if result.keypoints is None:
            continue

        keypoints_data = result.keypoints.data.cpu().numpy()
        boxes = result.boxes

        for i, kps in enumerate(keypoints_data):
            person_count += 1

            # Analyze pose
            alerts = analyze_single_pose(kps)
            all_alerts.extend(alerts)

            # Choose color based on alert severity
            if alerts:
                color = COLOR_DANGER if any(a in alerts for a in ["HEAD_TURNED", "LEANING"]) else COLOR_WARNING
            else:
                color = COLOR_SAFE

            # Draw bounding box
            if boxes is not None and i < len(boxes):
                box = boxes[i]
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = box.conf[0].item()

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                label = f"P{person_count}"
                if alerts:
                    label += f" {'|'.join(alerts)}"
                cv2.putText(frame, label, (x1, y1 - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)

                pose_boxes.append({
                    'x1': x1 / w, 'y1': y1 / h,
                    'x2': x2 / w, 'y2': y2 / h,
                    'conf': round(conf, 2),
                    'alerts': alerts
                })

            # Draw skeleton
            for (pt1_idx, pt2_idx) in SKELETON_CONNECTIONS:
                if pt1_idx < len(kps) and pt2_idx < len(kps):
                    pt1, pt2 = kps[pt1_idx], kps[pt2_idx]
                    if _is_valid(pt1) and _is_valid(pt2):
                        cv2.line(frame,
                                 (int(pt1[0]), int(pt1[1])),
                                 (int(pt2[0]), int(pt2[1])),
                                 color, 2)

            # Draw keypoints
            for kp in kps:
                if _is_valid(kp):
                    cv2.circle(frame, (int(kp[0]), int(kp[1])), 3, color, -1)

    return frame, all_alerts, person_count, pose_boxes
