import cv2
import numpy as np
import os
import mediapipe as mp

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

# Key landmark indices for iris and eye corners
# MediaPipe face landmarker with 478 landmarks (468 face + 10 iris)
LEFT_IRIS_CENTER = 468
RIGHT_IRIS_CENTER = 473

LEFT_EYE_INNER = 133
LEFT_EYE_OUTER = 33
RIGHT_EYE_INNER = 362
RIGHT_EYE_OUTER = 263

LEFT_EYE_TOP = 159
LEFT_EYE_BOTTOM = 145
RIGHT_EYE_TOP = 386
RIGHT_EYE_BOTTOM = 374


def get_point(landmarks, idx, w, h):
    """Convert normalized landmark to pixel coordinates."""
    lm = landmarks[idx]
    return (lm.x * w, lm.y * h)


def compute_gaze_ratio(iris, inner, outer, top, bottom):
    """Compute horizontal and vertical gaze ratios from iris position."""
    eye_width = np.sqrt((outer[0] - inner[0])**2 + (outer[1] - inner[1])**2)
    iris_to_outer = np.sqrt((iris[0] - outer[0])**2 + (iris[1] - outer[1])**2)
    h_ratio = iris_to_outer / eye_width if eye_width > 0 else 0.5

    eye_height = np.sqrt((top[0] - bottom[0])**2 + (top[1] - bottom[1])**2)
    iris_to_top = np.sqrt((iris[0] - top[0])**2 + (iris[1] - top[1])**2)
    v_ratio = iris_to_top / eye_height if eye_height > 0 else 0.5

    return h_ratio, v_ratio


def process_eye_movement(frame):
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    result = landmarker.detect(mp_image)
    gaze_direction = "Looking Center"

    if result.face_landmarks:
        landmarks = result.face_landmarks[0]

        # Check if we have iris landmarks (478 total)
        if len(landmarks) >= 478:
            left_iris = get_point(landmarks, LEFT_IRIS_CENTER, w, h)
            right_iris = get_point(landmarks, RIGHT_IRIS_CENTER, w, h)

            left_inner = get_point(landmarks, LEFT_EYE_INNER, w, h)
            left_outer = get_point(landmarks, LEFT_EYE_OUTER, w, h)
            right_inner = get_point(landmarks, RIGHT_EYE_INNER, w, h)
            right_outer = get_point(landmarks, RIGHT_EYE_OUTER, w, h)

            left_top = get_point(landmarks, LEFT_EYE_TOP, w, h)
            left_bottom = get_point(landmarks, LEFT_EYE_BOTTOM, w, h)
            right_top = get_point(landmarks, RIGHT_EYE_TOP, w, h)
            right_bottom = get_point(landmarks, RIGHT_EYE_BOTTOM, w, h)

            left_h, left_v = compute_gaze_ratio(left_iris, left_inner, left_outer, left_top, left_bottom)
            right_h, right_v = compute_gaze_ratio(right_iris, right_inner, right_outer, right_top, right_bottom)

            avg_h = (left_h + right_h) / 2
            avg_v = (left_v + right_v) / 2

            # Gaze thresholds
            if avg_h < 0.35:
                gaze_direction = "Looking Right"
            elif avg_h > 0.65:
                gaze_direction = "Looking Left"
            elif avg_v < 0.30:
                gaze_direction = "Looking Up"
            elif avg_v > 0.65:
                gaze_direction = "Looking Down"
            else:
                gaze_direction = "Looking Center"
        else:
            # Fallback: use nose tip position relative to face center
            nose = landmarks[1]
            left_cheek = landmarks[234]
            right_cheek = landmarks[454]
            face_center_x = (left_cheek.x + right_cheek.x) / 2
            offset = nose.x - face_center_x

            if offset < -0.02:
                gaze_direction = "Looking Right"
            elif offset > 0.02:
                gaze_direction = "Looking Left"
            else:
                gaze_direction = "Looking Center"

    return frame, gaze_direction
