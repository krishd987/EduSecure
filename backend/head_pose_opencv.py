import cv2
import numpy as np
import math
import os
import mediapipe as mp
from collections import deque

# Initialize MediaPipe Face Landmarker (Tasks API)
BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "face_landmarker.task")

options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.IMAGE,
    output_face_blendshapes=False,
    output_facial_transformation_matrixes=False,
    num_faces=1,
    min_face_detection_confidence=0.5,
    min_face_presence_confidence=0.5,
    min_tracking_confidence=0.5
)

landmarker = FaceLandmarker.create_from_options(options)

# 3D model points for solvePnP (generic face model)
model_points_3d = np.array([
    (0.0, 0.0, 0.0),        # Nose tip (landmark 1)
    (0.0, -63.6, -12.5),    # Chin (landmark 152)
    (-43.3, 32.7, -26.0),   # Left eye outer corner (landmark 33)
    (43.3, 32.7, -26.0),    # Right eye outer corner (landmark 263)
    (-28.9, -28.9, -24.1),  # Left mouth corner (landmark 61)
    (28.9, -28.9, -24.1)    # Right mouth corner (landmark 291)
], dtype=np.float64)

# MediaPipe landmark indices corresponding to the 3D model points
POSE_LANDMARK_INDICES = [1, 152, 33, 263, 61, 291]

# Smoothing
ANGLE_HISTORY_SIZE = 5
yaw_history = deque(maxlen=ANGLE_HISTORY_SIZE)
pitch_history = deque(maxlen=ANGLE_HISTORY_SIZE)
roll_history = deque(maxlen=ANGLE_HISTORY_SIZE)

previous_state = "Looking at Screen"


def get_head_pose_angles(image_points, frame_shape):
    h, w = frame_shape[:2]
    focal_length = w
    center = (w / 2, h / 2)

    camera_matrix = np.array([
        [focal_length, 0, center[0]],
        [0, focal_length, center[1]],
        [0, 0, 1]
    ], dtype=np.float64)

    dist_coeffs = np.zeros((4, 1))

    success, rotation_vector, translation_vector = cv2.solvePnP(
        model_points_3d, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
    )
    if not success:
        return None

    rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
    sy = math.sqrt(rotation_matrix[0, 0]**2 + rotation_matrix[1, 0]**2)
    singular = sy < 1e-6

    if not singular:
        pitch = math.atan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
        yaw = math.atan2(-rotation_matrix[2, 0], sy)
        roll = math.atan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
    else:
        pitch = math.atan2(-rotation_matrix[1, 2], rotation_matrix[1, 1])
        yaw = math.atan2(-rotation_matrix[2, 0], sy)
        roll = 0

    return np.degrees(pitch), np.degrees(yaw), np.degrees(roll)


def smooth_angle(history, new_angle):
    history.append(new_angle)
    return np.mean(history)


def process_head_pose(frame, calibrated_angles=None):
    global previous_state

    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    result = landmarker.detect(mp_image)
    head_direction = "Looking at Screen"

    if result.face_landmarks:
        landmarks = result.face_landmarks[0]

        # Extract the 6 key points in pixel coordinates
        image_points = np.array([
            (landmarks[idx].x * w, landmarks[idx].y * h)
            for idx in POSE_LANDMARK_INDICES
        ], dtype=np.float64)

        angles = get_head_pose_angles(image_points, frame.shape)
        if angles is None:
            return frame, head_direction

        pitch = smooth_angle(pitch_history, angles[0])
        yaw = smooth_angle(yaw_history, angles[1])
        roll = smooth_angle(roll_history, angles[2])

        # Calibrating: return raw angles
        if calibrated_angles is None:
            return frame, (pitch, yaw, roll)

        if not isinstance(calibrated_angles, (tuple, list, np.ndarray)) or len(calibrated_angles) != 3:
            return frame, "Looking at Screen"

        if isinstance(calibrated_angles, np.ndarray):
            calibrated_angles = tuple(calibrated_angles)

        pitch_offset, yaw_offset, roll_offset = calibrated_angles

        # Compute relative angles from calibrated baseline
        rel_yaw = yaw - yaw_offset
        rel_pitch = pitch - pitch_offset
        rel_roll = roll - roll_offset

        # Single unified thresholds — NO dead zones
        YAW_THRESHOLD = 12      # degrees from center to trigger left/right
        PITCH_THRESHOLD = 10    # degrees from center to trigger up/down
        ROLL_THRESHOLD = 10     # degrees from center to trigger tilted

        # Debug logging (visible in Flask console)
        print(f"[HEAD] yaw={rel_yaw:+.1f}  pitch={rel_pitch:+.1f}  roll={rel_roll:+.1f}")

        # Determine head direction — check largest deviation first
        if abs(rel_yaw) > abs(rel_pitch) and abs(rel_yaw) > YAW_THRESHOLD:
            # Yaw is dominant deviation
            if rel_yaw < -YAW_THRESHOLD:
                current_state = "Looking Left"
            else:
                current_state = "Looking Right"
        elif abs(rel_pitch) > PITCH_THRESHOLD:
            # Pitch is dominant deviation (inverted: positive pitch = looking down)
            if rel_pitch > PITCH_THRESHOLD:
                current_state = "Looking Down"
            elif rel_pitch < -PITCH_THRESHOLD:
                current_state = "Looking Up"
            else:
                current_state = "Looking at Screen"
        elif abs(rel_roll) > ROLL_THRESHOLD:
            current_state = "Tilted"
        else:
            current_state = "Looking at Screen"

        previous_state = current_state
        head_direction = current_state

    return frame, head_direction

