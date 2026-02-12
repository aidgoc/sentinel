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
    import onnxruntime as ort
except ImportError:
    print(json.dumps({"error": "onnxruntime not installed", "person_present": False}))
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

        # Load YOLO model (ONNX Runtime with CUDA)
        self.session = None
        self._load_model()

    def _load_model(self):
        """Load YOLO ONNX model with CUDA provider for MX130"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"YOLO model not found: {self.model_path}")

        # Try CUDA first (MX130), fallback to CPU
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']

        try:
            self.session = ort.InferenceSession(self.model_path, providers=providers)
            actual_provider = self.session.get_providers()[0]
            print(f"[DEBUG] YOLO loaded on {actual_provider}", file=sys.stderr)
        except Exception as e:
            print(f"[ERROR] Failed to load YOLO: {e}", file=sys.stderr)
            raise

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
        # Read and preprocess image
        img = cv2.imread(image_path)
        if img is None:
            return 0.0, "Failed to read image"

        # YOLOv8 expects 640x640 RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img_rgb, (640, 640))
        img_normalized = img_resized.astype(np.float32) / 255.0
        img_transposed = img_normalized.transpose(2, 0, 1)  # HWC -> CHW
        img_batch = np.expand_dims(img_transposed, axis=0)  # Add batch dimension

        # Inference
        input_name = self.session.get_inputs()[0].name
        outputs = self.session.run(None, {input_name: img_batch})

        # Parse detections (YOLOv8 output format)
        # outputs[0] shape: [1, 84, 8400] or similar
        detections = outputs[0][0]  # Remove batch dimension

        # Find person detections (class 0)
        max_confidence = 0.0

        # YOLOv8 format: [x, y, w, h, class0_conf, class1_conf, ...]
        # Transpose to [8400, 84]
        detections = detections.T

        for detection in detections:
            # Class confidences start at index 4
            class_confidences = detection[4:]
            class_id = np.argmax(class_confidences)
            confidence = class_confidences[class_id]

            if class_id == 0 and confidence > max_confidence:  # Person class
                max_confidence = float(confidence)

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
        "model_path": context.get("model_path", "~/sentinel/models/yolov8n.onnx"),
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
