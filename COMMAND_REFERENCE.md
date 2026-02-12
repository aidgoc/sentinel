# 🛡️ SENTINEL - COMPLETE COMMAND REFERENCE

**Your go-to guide for all Sentinel commands, locations, and troubleshooting.**

---

## 📋 TABLE OF CONTENTS

1. [Quick Start Commands](#quick-start-commands)
2. [Data Storage Locations](#data-storage-locations)
3. [Useful Commands](#useful-commands)
4. [Configuration Files](#configuration-files)
5. [Maintenance & Cleanup](#maintenance--cleanup)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Usage](#advanced-usage)

---

## 🚀 QUICK START COMMANDS

### Basic Operations

```bash
# Start Telegram bot (default)
ltl

# Text conversation (keyboard)
ltl chat

# Voice conversation (microphone)
ltl voice

# Take a photo right now
ltl vision

# Check system status
ltl status

# Run tests
ltl test

# View recent captures
ltl logs

# Show help
ltl help
```

### Three Ways to Interact

| Mode | Command | Input | Output | Vision Trigger |
|------|---------|-------|--------|----------------|
| **Text** | `ltl chat` | Keyboard | Text | Type `see` |
| **Voice** | `ltl voice` | Microphone | Speech | Say "show me" |
| **Telegram** | `ltl` | Phone app | Messages | `/wake` |

---

## 📁 DATA STORAGE LOCATIONS

### 1. Images (Camera Captures)

**Location:**
```bash
~/sentinel_captures/YYYY-MM-DD/
```

**Example Structure:**
```
/home/harshwardhan/sentinel_captures/
├── 2026-02-12/
│   ├── 2026-02-12T14-30-45Z.jpg
│   ├── 2026-02-12T15-22-10Z.jpg
│   └── 2026-02-12T16-45-33Z.jpg
├── 2026-02-13/
│   └── 2026-02-13T09-15-20Z.jpg
```

**Features:**
- Organized by date (one folder per day)
- ISO 8601 timestamps in filenames
- JPG format for compatibility
- 7-day auto-rotation (old images cleaned up)

### 2. Database (Conversations & Memory)

**Location:**
```bash
~/.openclaw-sentinel/sentinel_memory.db
```

**Contains:**
- Conversation history (Q&A pairs)
- Vector embeddings for RAG
- Temporal state (3-frame person detection buffer)
- Interaction timestamps
- Safety protocol responses

### 3. Configuration Files

```bash
~/.sentinel_env                      # Credentials (600 permissions)
~/sentinel/config/sentinel.yaml      # System configuration
~/.bashrc                            # Path configuration for ltl
```

### 4. Models (AI Models)

```bash
~/sentinel/models/yolov8n.onnx       # YOLO detection (~12MB)
~/.cache/whisper/                    # Whisper models (~150MB)
~/.local/share/piper/                # Piper voice models (~60MB)
~/.ollama/models/                    # Ollama models (qwen2.5:3b ~1.9GB)
```

### 5. Logs

```bash
~/sentinel/logs/                     # Application logs (if enabled)
```

---

## 🔍 USEFUL COMMANDS

### Viewing Images

```bash
# See all images from today
ls ~/sentinel_captures/$(date +%Y-%m-%d)/

# See images from specific date
ls ~/sentinel_captures/2026-02-12/

# View most recent image
ls -t ~/sentinel_captures/$(date +%Y-%m-%d)/*.jpg | head -1

# Open most recent image
xdg-open $(ls -t ~/sentinel_captures/$(date +%Y-%m-%d)/*.jpg | head -1)

# Count images from today
ls ~/sentinel_captures/$(date +%Y-%m-%d)/*.jpg 2>/dev/null | wc -l

# Count all images
find ~/sentinel_captures -name "*.jpg" | wc -l

# Show images from last 7 days
find ~/sentinel_captures -name "*.jpg" -mtime -7
```

### Checking System Status

```bash
# Full system status
ltl status

# Check if Ollama is running
curl -s http://localhost:11434/api/tags

# List loaded Ollama models
ollama list

# Check camera availability
ls -l /dev/video0

# Check database size
du -h ~/.openclaw-sentinel/sentinel_memory.db

# Check total storage used
du -sh ~/sentinel_captures
du -sh ~/.openclaw-sentinel
du -sh ~/sentinel

# Check free disk space
df -h ~

# Check memory usage
free -h
```

### Database Operations

```bash
# Check database exists
ls -lh ~/.openclaw-sentinel/sentinel_memory.db

# View database size
du -h ~/.openclaw-sentinel/sentinel_memory.db

# Backup database
cp ~/.openclaw-sentinel/sentinel_memory.db ~/sentinel_backup_$(date +%Y%m%d).db

# Query database (requires sqlite3)
sqlite3 ~/.openclaw-sentinel/sentinel_memory.db "SELECT * FROM conversations LIMIT 10;"

# Count conversations
sqlite3 ~/.openclaw-sentinel/sentinel_memory.db "SELECT COUNT(*) FROM conversations;"
```

### Telegram Bot

```bash
# Start bot
ltl

# Start bot in background
ltl &

# Check if bot is running
ps aux | grep telegram_bot

# Stop bot
pkill -f telegram_bot.py

# View bot token (secure - only you can see)
grep TELEGRAM_BOT_TOKEN ~/.sentinel_env
```

---

## ⚙️ CONFIGURATION FILES

### ~/.sentinel_env (Credentials)

**Location:** `/home/harshwardhan/.sentinel_env`

**View (secure):**
```bash
cat ~/.sentinel_env
```

**Edit:**
```bash
nano ~/.sentinel_env
```

**Contents:**
```bash
export TELEGRAM_BOT_TOKEN="your_token_here"
export ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}"
export CUDA_VISIBLE_DEVICES=""  # Force CPU mode for MX130
export SENTINEL_HOME="$HOME/sentinel"
```

### ~/sentinel/config/sentinel.yaml (System Config)

**Location:** `/home/harshwardhan/sentinel/config/sentinel.yaml`

**View:**
```bash
cat ~/sentinel/config/sentinel.yaml
```

**Edit:**
```bash
nano ~/sentinel/config/sentinel.yaml
```

**Key Settings:**
```yaml
llm:
  provider: "ollama"
  model: "qwen2.5:3b"

vision:
  detector:
    model_path: "models/yolov8n.onnx"
    confidence_threshold: 0.85
    temporal_frames: 3

captures:
  base_dir: "~/sentinel_captures"
  retention_days: 7
```

---

## 🗑️ MAINTENANCE & CLEANUP

### Delete Old Captures

```bash
# Delete captures older than 7 days
find ~/sentinel_captures -type d -mtime +7 -exec rm -rf {} \;

# Delete captures older than 30 days
find ~/sentinel_captures -type d -mtime +30 -exec rm -rf {} \;

# Delete all captures (careful!)
rm -rf ~/sentinel_captures/*

# Delete specific date
rm -rf ~/sentinel_captures/2026-02-10
```

### Database Maintenance

```bash
# Backup database before cleanup
cp ~/.openclaw-sentinel/sentinel_memory.db ~/sentinel_db_backup.db

# Reset database (will be recreated)
rm ~/.openclaw-sentinel/sentinel_memory.db

# Vacuum database (compress)
sqlite3 ~/.openclaw-sentinel/sentinel_memory.db "VACUUM;"
```

### Model Cache Cleanup

```bash
# Clear Whisper cache
rm -rf ~/.cache/whisper/*

# Remove unused Ollama models
ollama rm <model_name>

# List Ollama models to see what can be removed
ollama list
```

### Logs Cleanup

```bash
# Clear application logs (if any)
rm -rf ~/sentinel/logs/*
```

---

## 🐛 TROUBLESHOOTING

### "ltl: command not found"

```bash
# Reload shell configuration
source ~/.bashrc

# Or use full path
~/sentinel/ltl

# Check if ltl exists
ls -l ~/.local/bin/ltl

# Re-create symlink if missing
ln -sf ~/sentinel/ltl ~/.local/bin/ltl
```

### "Ollama offline"

```bash
# Check if Ollama is running
curl -s http://localhost:11434/api/tags

# Start Ollama
ollama serve &

# Check Ollama status
ps aux | grep ollama

# Test Ollama
ollama run qwen2.5:3b "Hello"
```

### "Camera not found"

```bash
# Check camera device
ls -l /dev/video0

# List all video devices
ls -l /dev/video*

# Test camera with OpenCV
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK!' if cap.isOpened() else 'Camera failed'); cap.release()"
```

### "Microphone not found" (Voice Mode)

```bash
# List audio devices
python3 -c "import sounddevice; print(sounddevice.query_devices())"

# Test recording
python3 -c "import sounddevice as sd; import numpy as np; print('Recording...'); audio = sd.rec(16000, samplerate=16000, channels=1); sd.wait(); print('Done!')"

# Check ALSA devices
arecord -l
```

### "Piper voice not found"

```bash
# Check if voice files exist
ls ~/.local/share/piper/

# Should see:
# en_US-lessac-medium.onnx
# en_US-lessac-medium.onnx.json

# If missing, copy from local-talking-llm
cp ~/local-talking-llm/.local/share/piper/* ~/.local/share/piper/
```

### "Telegram bot not responding"

```bash
# Check bot is running
ps aux | grep telegram_bot

# Check token is correct
grep TELEGRAM_BOT_TOKEN ~/.sentinel_env

# Restart bot
pkill -f telegram_bot.py
ltl

# Check for errors
ltl 2>&1 | grep -i error
```

### "CUDA error" or GPU issues

```bash
# Check CUDA is disabled (for MX130)
echo $CUDA_VISIBLE_DEVICES
# Should output: (empty) or nothing

# Ensure CPU mode is set
grep CUDA_VISIBLE_DEVICES ~/.sentinel_env
# Should show: export CUDA_VISIBLE_DEVICES=""

# If not set, add it
echo 'export CUDA_VISIBLE_DEVICES=""' >> ~/.sentinel_env
source ~/.sentinel_env
```

### Python Dependencies Missing

```bash
# Activate virtual environment
source ~/sentinel/.venv/bin/activate

# Reinstall dependencies
cd ~/sentinel
pip install -r requirements.txt

# Test imports
python3 -c "import cv2, onnxruntime, ollama, telegram, whisper"
```

---

## 🔧 ADVANCED USAGE

### Running Bot in Background

```bash
# Start in background
ltl &

# Check it's running
jobs

# View output
tail -f ~/.sentinel_bot.log  # if logging is enabled

# Stop background bot
pkill -f telegram_bot.py
```

### Auto-start on Boot

```bash
# Add to ~/.bashrc (manual start on login)
echo "ltl &" >> ~/.bashrc

# Or create systemd service (auto-start on boot)
nano ~/.config/systemd/user/sentinel.service
```

**Systemd service example:**
```ini
[Unit]
Description=Sentinel Telegram Bot
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/harshwardhan/sentinel
ExecStart=/home/harshwardhan/sentinel/.venv/bin/python3 /home/harshwardhan/sentinel/skills/telegram_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

**Enable service:**
```bash
systemctl --user enable sentinel.service
systemctl --user start sentinel.service
systemctl --user status sentinel.service
```

### Custom Whisper Model

```bash
# Use faster model (less accurate)
ltl voice --whisper-model tiny.en

# Use better model (slower)
ltl voice --whisper-model small.en

# Default (balanced)
ltl voice --whisper-model base.en
```

### Custom LLM Model

```bash
# Use different Ollama model
ltl chat --model gemma3

# Or edit config
nano ~/sentinel/config/sentinel.yaml
# Change: model: "gemma3"
```

### Export Conversation History

```bash
# Export to JSON
sqlite3 ~/.openclaw-sentinel/sentinel_memory.db "SELECT * FROM conversations" | python3 -m json.tool > conversations.json

# Export to CSV
sqlite3 -header -csv ~/.openclaw-sentinel/sentinel_memory.db "SELECT * FROM conversations" > conversations.csv
```

### Performance Monitoring

```bash
# Monitor CPU usage
top -p $(pgrep -f telegram_bot)

# Monitor memory
ps aux | grep telegram_bot | awk '{print $6}'

# Monitor disk I/O
iotop -p $(pgrep -f telegram_bot)

# Check capture rate
watch -n 1 'ls ~/sentinel_captures/$(date +%Y-%m-%d)/*.jpg 2>/dev/null | wc -l'
```

### Testing Individual Components

```bash
# Test vision skill
cd ~/sentinel
echo '{}' | python3 skills/vision_skill.py | python3 -m json.tool

# Test conversation skill
echo '{"question_id": "test", "response": "yes"}' | python3 skills/conversation_skill.py

# Test cloud fallback
python3 -c "from skills.cloud_fallback import CloudFallback; cf = CloudFallback(); print(cf.query_with_fallback('Hello'))"

# Test voice chat (text mode)
cd ~/sentinel
python3 skills/voice_chat.py
```

---

## 📚 DOCUMENTATION FILES

All documentation is in `~/sentinel/`:

```bash
# Read quick start
cat ~/sentinel/QUICK_START.md

# Read voice guide
cat ~/sentinel/VOICE_GUIDE.md

# Read deployment guide
cat ~/sentinel/DEPLOYMENT.md

# Read final status
cat ~/sentinel/FINAL_STATUS.md

# Read this reference
cat ~/sentinel/COMMAND_REFERENCE.md

# Read main README
cat ~/sentinel/README.md
```

---

## 🎯 COMMON WORKFLOWS

### Daily Usage Workflow

```bash
# Morning: Start the bot
ltl &

# Check today's captures
ltl logs

# Test voice mode
ltl voice

# Evening: Check status
ltl status

# Stop bot
pkill -f telegram_bot.py
```

### Weekly Maintenance

```bash
# Backup database
cp ~/.openclaw-sentinel/sentinel_memory.db ~/backups/sentinel_$(date +%Y%m%d).db

# Clean old captures (older than 7 days)
find ~/sentinel_captures -type d -mtime +7 -exec rm -rf {} \;

# Check disk usage
du -sh ~/sentinel_captures
du -sh ~/.openclaw-sentinel

# Vacuum database
sqlite3 ~/.openclaw-sentinel/sentinel_memory.db "VACUUM;"
```

### Debugging Workflow

```bash
# 1. Check system status
ltl status

# 2. Test each component
ltl test

# 3. Check logs
ltl logs

# 4. Test vision
ltl vision

# 5. Test chat
ltl chat

# 6. Test voice
ltl voice

# 7. Check for errors
journalctl --user -u sentinel.service  # if using systemd
```

---

## 🔐 SECURITY NOTES

### File Permissions

```bash
# Ensure credentials are secure
chmod 600 ~/.sentinel_env

# Verify
ls -l ~/.sentinel_env
# Should show: -rw------- (only you can read/write)
```

### Backup Important Data

```bash
# Backup everything important
mkdir -p ~/sentinel_backups/$(date +%Y%m%d)
cp ~/.sentinel_env ~/sentinel_backups/$(date +%Y%m%d)/
cp ~/.openclaw-sentinel/sentinel_memory.db ~/sentinel_backups/$(date +%Y%m%d)/
cp -r ~/sentinel_captures/$(date +%Y-%m-%d) ~/sentinel_backups/$(date +%Y%m%d)/
```

### Secure Token Storage

```bash
# Never commit .sentinel_env to git
echo ".sentinel_env" >> ~/sentinel/.gitignore

# Never share your token
# Keep ~/.sentinel_env permissions at 600
```

---

## 📞 QUICK HELP

**Need help?**
```bash
ltl help
```

**Can't remember a command?**
```bash
cat ~/sentinel/COMMAND_REFERENCE.md | grep -A 3 "what you're looking for"
```

**Something broken?**
```bash
ltl test
ltl status
```

**Want to start fresh?**
```bash
# Reset everything (careful!)
rm -rf ~/.openclaw-sentinel
rm -rf ~/sentinel_captures
# Then run: ltl
```

---

## 🎉 THAT'S IT!

You now have a complete reference for all Sentinel commands!

**Bookmark this file:**
```bash
cat ~/sentinel/COMMAND_REFERENCE.md
```

**Quick access:**
```bash
alias sentinel-help='cat ~/sentinel/COMMAND_REFERENCE.md | less'
# Add to ~/.bashrc for permanent alias
```

🛡️ **Sentinel - Your Local Ambient Intelligence Agent**
