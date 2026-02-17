#!/usr/bin/env python3
"""
Sentinel Vision Skill - Person Detection with YOLO
Engineer #2: Computer Vision Lead

Captures images, runs YOLOv8-nano on MX130 GPU, detects persons with temporal filtering.
Returns JSON to OpenClaw via STDIO.
"""

import sys
import json
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
import os

try:
    from ultralytics import YOLO as _YOLO
    import torch
    _USE_ULTRALYTICS = True
except ImportError:
    _USE_ULTRALYTICS = False

try:
    import onnxruntime as ort
    _USE_ORT = True
except ImportError:
    _USE_ORT = False

if not _USE_ULTRALYTICS and not _USE_ORT:
    print(json.dumps({"error": "neither ultralytics nor onnxruntime installed", "person_present": False}))
    sys.exit(1)


class TemporalFilter:
    """Anti-flicker: require N consecutive high-confidence detections"""

    def __init__(self, threshold=0.85, consecutive=3):
        self.threshold = threshold
        self.consecutive = consecutive
        self.buffer = []

    def update(self, confidence):
        """Add new detection, return True if threshold met"""
        self.buffer.append(confidence > self.threshold)
        if len(self.buffer) > self.consecutive:
            self.buffer.pop(0)
        return len(self.buffer) == self.consecutive and all(self.buffer)

    def reset(self):
        """Clear buffer"""
        self.buffer = []


class VisionSkill:
    def __init__(self, config=None):
        self.config = config or {}

        # Paths
        self.model_path = os.path.expanduser(
            self.config.get("model_path", "~/sentinel/models/yolov8n.onnx")
        )
        self.capture_base = os.path.expanduser(
            self.config.get("capture_base", "~/sentinel_captures")
        )

        # Detection parameters
        self.confidence_threshold = self.config.get("confidence_threshold", 0.85)
        self.temporal_frames = self.config.get("temporal_frames", 3)

        # Camera
        self.camera_device = self.config.get("camera_device", 0)
        self.resolution = self.config.get("resolution", [1280, 720])

        # Initialize temporal filter
        self.filter = TemporalFilter(
            threshold=self.confidence_threshold,
            consecutive=self.temporal_frames
        )

        # Load YOLO model — prefer ultralytics+torch (GPU-compatible on sm_50)
        self.session = None   # ort session (fallback only)
        self.yolo = None      # ultralytics model
        self._load_model()

    def _load_model(self):
        """Load YOLO model. Prefers ultralytics .pt (torch GPU), falls back to onnxruntime CPU."""
        pt_path = os.path.expanduser("~/sentinel/models/yolov8n.pt")
        onnx_path = self.model_path

        if _USE_ULTRALYTICS and os.path.exists(pt_path):
            device = "0" if torch.cuda.is_available() else "cpu"
            self.yolo = _YOLO(pt_path)
            # Warm up so device is confirmed
            dummy = np.zeros((640, 640, 3), dtype=np.uint8)
            self.yolo.predict(dummy, device=device, verbose=False)
            self._device = device
            print(f"[DEBUG] YOLO loaded via ultralytics on device={device}", file=sys.stderr)
        elif _USE_ORT and os.path.exists(onnx_path):
            self.session = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
            print(f"[DEBUG] YOLO loaded via onnxruntime CPU", file=sys.stderr)
        else:
            raise FileNotFoundError("No YOLO model found (checked yolov8n.pt and yolov8n.onnx)")

    def capture_image(self):
        """Capture image from camera with timestamp"""
        cap = cv2.VideoCapture(self.camera_device)

        if not cap.isOpened():
            return None, "Camera failed to open"

        # Set resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])

        ret, frame = cap.read()
        cap.release()

        if not ret:
            return None, "Failed to capture frame"

        # Generate timestamped path
        timestamp = datetime.now()
        date_folder = timestamp.strftime("%Y-%m-%d")
        filename = timestamp.strftime("%H-%M-%S.jpg")

        # Create directory
        save_dir = Path(self.capture_base) / date_folder
        save_dir.mkdir(parents=True, exist_ok=True)

        # Save with timestamp in EXIF (via OpenCV comment)
        save_path = save_dir / filename
        cv2.imwrite(str(save_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 85])

        return str(save_path), None

    def detect_person(self, image_path):
        """Run YOLO inference, detect persons (class 0)"""
        img = cv2.imread(image_path)
        if img is None:
            return 0.0, "Failed to read image"

        if self.yolo is not None:
            # ultralytics path (torch, GPU on sm_50)
            results = self.yolo.predict(img, device=self._device, verbose=False)
            max_confidence = 0.0
            boxes = results[0].boxes
            if boxes is not None and len(boxes):
                for cls, conf in zip(boxes.cls.cpu().numpy(), boxes.conf.cpu().numpy()):
                    if int(cls) == 0 and float(conf) > max_confidence:
                        max_confidence = float(conf)
            return max_confidence, None

        # onnxruntime fallback (CPU)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_batch = np.expand_dims(
            cv2.resize(img_rgb, (640, 640)).astype(np.float32).transpose(2, 0, 1) / 255.0,
            axis=0,
        )
        outputs = self.session.run(None, {self.session.get_inputs()[0].name: img_batch})
        detections = outputs[0][0].T
        max_confidence = 0.0
        for det in detections:
            class_confidences = det[4:]
            class_id = int(np.argmax(class_confidences))
            confidence = float(class_confidences[class_id])
            if class_id == 0 and confidence > max_confidence:
                max_confidence = confidence
        return max_confidence, None

    def cleanup_old_captures(self):
        """Delete captures older than retention_days"""
        retention_days = self.config.get("retention_days", 7)
        cutoff = datetime.now().timestamp() - (retention_days * 24 * 3600)

        capture_path = Path(self.capture_base)
        if not capture_path.exists():
            return

        for day_folder in capture_path.iterdir():
            if not day_folder.is_dir():
                continue

            # Check if folder is older than cutoff
            try:
                folder_time = datetime.strptime(day_folder.name, "%Y-%m-%d").timestamp()
                if folder_time < cutoff:
                    # Delete entire day folder
                    for img_file in day_folder.glob("*.jpg"):
                        img_file.unlink()
                    day_folder.rmdir()
                    print(f"[DEBUG] Deleted old captures: {day_folder.name}", file=sys.stderr)
            except ValueError:
                # Not a valid date folder, skip
                continue

    def execute(self, context=None):
        """Main execution: capture -> detect -> filter -> return JSON"""
        context = context or {}

        # Capture image
        image_path, error = self.capture_image()
        if error:
            return {
                "error": error,
                "person_present": False,
                "confidence": 0.0,
                "image_path": None,
                "timestamp": datetime.now().isoformat()
            }

        # Detect person
        confidence, error = self.detect_person(image_path)
        if error:
            return {
                "error": error,
                "person_present": False,
                "confidence": 0.0,
                "image_path": image_path,
                "timestamp": datetime.now().isoformat()
            }

        # Temporal filtering
        person_present = self.filter.update(confidence)

        # Cleanup old captures
        self.cleanup_old_captures()

        return {
            "person_present": person_present,
            "confidence": float(confidence),
            "image_path": image_path,
            "timestamp": datetime.now().isoformat(),
            "trigger_conversation": person_present
        }


def main():
    """STDIO interface for OpenClaw"""
    # Read config from stdin if provided
    try:
        if not sys.stdin.isatty():
            context = json.load(sys.stdin)
        else:
            context = {}
    except json.JSONDecodeError:
        context = {}

    # Load configuration
    config = {
        "model_path": context.get("model_path", "~/sentinel/models/yolov8n.pt"),
        "capture_base": context.get("capture_base", "~/sentinel_captures"),
        "confidence_threshold": context.get("confidence_threshold", 0.85),
        "temporal_frames": context.get("temporal_frames", 3),
        "camera_device": context.get("camera_device", 0),
        "resolution": context.get("resolution", [1280, 720]),
        "retention_days": context.get("retention_days", 7),
    }

    # Execute vision skill
    try:
        skill = VisionSkill(config)
        result = skill.execute(context)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({
            "error": str(e),
            "person_present": False,
            "confidence": 0.0,
            "timestamp": datetime.now().isoformat()
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()
