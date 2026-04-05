import cv2
import os
import torch
from ultralytics import YOLO

# Standard COCO model for high-accuracy standard object detection
# We use an official ultralytics model instead of the flawed custom one
cache_dir = os.environ.get("RENDER_DISK_PATH", os.environ.get("TMPDIR", "/tmp"))
if os.name == "nt": # Windows fallback
    cache_dir = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(cache_dir, 'yolo11x.pt')
model = YOLO(model_path) # Will auto-download ~100MB weight if not present
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

def process_mobile_detection(frame):
    results = model(frame, verbose=False)
    mobile_detected = False
    boxes = []
    h, w = frame.shape[:2]

    # In standard COCO models, class 67 is 'cell phone'.
    for result in results:
        for box in result.boxes:
            conf = box.conf[0].item()
            cls = int(box.cls[0].item())

            if conf < 0.35 or cls != 67:  # Cell phone class index is 67
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            label = f"Mobile ({conf:.2f})"

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            mobile_detected = True
            # Return normalized coordinates (0-1) so frontend can scale to any size
            boxes.append({
                'x1': x1 / w,
                'y1': y1 / h,
                'x2': x2 / w,
                'y2': y2 / h,
                'conf': round(conf, 2),
                'label': label
            })

    return frame, mobile_detected, boxes

