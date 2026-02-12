# Models Directory

This directory contains AI models used by Sentinel. Models are not committed to git due to their large size.

## Required Models

### YOLOv8 Nano (Person Detection)

**File:** `yolov8n.onnx` (12.3 MB)

**Download:**
```bash
cd ~/sentinel/models
wget https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.onnx
```

Or use the setup script:
```bash
cd ~/sentinel
python3 scripts/download_models.py
```

## Model Locations

- **YOLO**: `~/sentinel/models/yolov8n.onnx`
- **Whisper**: Auto-downloads to `~/.cache/whisper/`
- **Piper TTS**: `~/.local/share/piper/`
- **Ollama**: `~/.ollama/models/`

## Verify Models

```bash
ltl status
```

This will show if all required models are present and loaded.
