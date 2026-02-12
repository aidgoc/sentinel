# 🍓 SENTINEL ON RASPBERRY PI

**Deploy your ambient intelligence agent on a Raspberry Pi or other single-board computers!**

---

## 🎯 TL;DR - Is It Possible?

**YES!** Sentinel is designed to be lightweight and CPU-only, making it perfect for Raspberry Pi.

### ✅ What Works Great
- **All models run on CPU** (already configured for this)
- **qwen2.5:3b LLM** (~1.9GB, runs fine on Pi 4/5)
- **Moondream vision** (designed for edge devices)
- **YOLOv8-nano** (only 12MB, very efficient)
- **Whisper STT** (base.en works well)
- **Piper TTS** (native ARM support)
- **Telegram bot** (minimal resources)

### ⚠️ What's Slower (But Still Works)
- **LLM inference:** ~3-5s per response (vs 1-2s on desktop)
- **Vision analysis:** ~8-10s (vs 3-5s on desktop)
- **Overall acceptable** for ambient intelligence use case

---

## 💻 RECOMMENDED HARDWARE

### Raspberry Pi Models

| Model | RAM | Recommended | Notes |
|-------|-----|-------------|-------|
| **Pi 5** | 8GB | ✅ **Best** | Fastest CPU, plenty of RAM |
| **Pi 5** | 4GB | ✅ **Great** | Good balance |
| **Pi 4** | 8GB | ✅ **Good** | Proven to work well |
| **Pi 4** | 4GB | ⚠️ **Minimal** | Works but tight on RAM |
| **Pi 4** | 2GB | ❌ **Too small** | Not enough RAM for models |
| **Pi 3** | Any | ❌ **Too slow** | CPU too weak for LLM |

### Other Single-Board Computers

**Also compatible:**
- **Orange Pi 5** (8GB+) - Excellent choice
- **Rock Pi 4** (4GB+) - Good performance
- **Odroid N2+** (4GB+) - Solid option
- **NVIDIA Jetson Nano** (4GB) - Has GPU but we use CPU mode

### Required Peripherals

```
✅ USB Webcam or Pi Camera Module v2/v3
✅ USB Microphone (for voice mode)
✅ Speakers or 3.5mm audio output (for TTS)
✅ MicroSD Card: 32GB+ (64GB recommended)
✅ Power Supply: Official Pi power adapter
✅ Internet: Ethernet or WiFi
```

**Optional:**
- Case with cooling fan (recommended for Pi 4/5)
- Heat sinks
- External SSD via USB 3.0 (faster than SD card)

---

## 📦 STORAGE REQUIREMENTS

### Disk Space Needed

```
Operating System (Raspberry Pi OS):  ~4 GB
Sentinel Code:                       ~50 MB
Python Dependencies:                ~500 MB
Models:
  - YOLOv8-nano:                     ~12 MB
  - qwen2.5:3b (Ollama):           ~1.9 GB
  - Moondream (Ollama):            ~1.7 GB
  - Whisper base.en:               ~150 MB
  - Piper TTS:                      ~60 MB
  - Embeddings:                    ~100 MB

Total: ~9 GB minimum
Recommended: 32GB+ SD card (leaves room for captures & database)
```

### Memory (RAM) Usage

```
Idle:                ~500 MB
YOLO Detection:      ~100 MB
qwen2.5:3b LLM:    ~2.5 GB
Moondream Vision:  ~2.0 GB
Whisper STT:       ~500 MB
Everything else:   ~400 MB

Peak (vision query): ~3.5 GB
Recommended: 4GB+ RAM
```

---

## 🚀 INSTALLATION GUIDE

### Step 1: Prepare Raspberry Pi

**Install Raspberry Pi OS (64-bit):**

```bash
# Use Raspberry Pi Imager to install:
# "Raspberry Pi OS (64-bit)" - NOT the 32-bit version!

# After booting, update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y \
    python3.11 python3.11-venv python3-pip \
    git curl wget \
    portaudio19-dev \
    ffmpeg \
    libopencv-dev \
    libsqlite3-dev \
    build-essential
```

### Step 2: Install Ollama (ARM64)

```bash
# Download and install Ollama for ARM
curl -fsSL https://ollama.ai/install.sh | sh

# Verify installation
ollama --version

# Pull models (this takes time on Pi)
ollama pull qwen2.5:3b    # ~1.9GB, takes 5-10 min on good connection
ollama pull moondream      # ~1.7GB, takes 5-10 min

# Test
ollama run qwen2.5:3b "Hello, are you working?"
```

### Step 3: Clone Sentinel

```bash
# Clone from GitHub
cd ~
git clone https://github.com/aidgoc/sentinel.git
cd sentinel

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Step 4: Install Python Dependencies

```bash
# Install requirements
pip install -r requirements.txt

# Install Whisper (may take time to build on ARM)
pip install openai-whisper

# If Whisper build fails, use prebuilt wheel:
pip install --no-build-isolation openai-whisper
```

### Step 5: Download Models

```bash
# Download YOLO model
cd ~/sentinel
python3 scripts/download_models.py

# Or manually:
cd ~/sentinel/models
wget https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.onnx
```

### Step 6: Install Piper TTS

```bash
# Create directory
mkdir -p ~/.local/share/piper

# Download ARM64 Piper voice
cd ~/.local/share/piper
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/voice-en-us-lessac-medium.tar.gz
tar -xzf voice-en-us-lessac-medium.tar.gz
rm voice-en-us-lessac-medium.tar.gz

# Verify
ls ~/.local/share/piper/
# Should see: en_US-lessac-medium.onnx and .json file
```

### Step 7: Configure Sentinel

```bash
# Create environment file
cat > ~/.sentinel_env << 'EOF'
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}"
export CUDA_VISIBLE_DEVICES=""
export SENTINEL_HOME="$HOME/sentinel"
EOF

# Secure it
chmod 600 ~/.sentinel_env

# Add to bashrc
echo "source ~/.sentinel_env" >> ~/.bashrc
source ~/.bashrc
```

### Step 8: Set Up ltl Command

```bash
# Add to PATH
mkdir -p ~/.local/bin
ln -sf ~/sentinel/ltl ~/.local/bin/ltl

# Add to PATH in bashrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Test
ltl help
```

### Step 9: Test Everything

```bash
# System status
ltl status

# Run tests
ltl test

# Test vision
ltl vision

# Test chat
ltl chat
# Type: hi
# Type: exit

# Test Telegram bot
ltl
# Then send /start in Telegram
```

---

## ⚡ PERFORMANCE OPTIMIZATION

### 1. Use Faster SD Card or SSD

```bash
# Boot from USB SSD instead of SD card for 2-3x speed improvement
# Tutorial: https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#usb-mass-storage-boot
```

### 2. Enable SWAP (for 4GB Pi)

```bash
# Increase swap to 4GB
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Change: CONF_SWAPSIZE=4096
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# Verify
free -h
```

### 3. Use Smaller Whisper Model

```bash
# Use tiny.en for faster (less accurate) transcription
ltl voice --whisper-model tiny.en
```

### 4. Optimize Ollama

```bash
# Edit Ollama service to limit CPU cores (optional)
sudo systemctl edit ollama

# Add:
[Service]
Environment="OLLAMA_NUM_THREADS=3"
Environment="OLLAMA_MAX_LOADED_MODELS=1"

sudo systemctl daemon-reload
sudo systemctl restart ollama
```

### 5. Overclock Pi (Advanced)

```bash
# Edit config for Pi 4/5
sudo nano /boot/config.txt

# Add (Pi 4):
over_voltage=6
arm_freq=2000

# Add (Pi 5):
over_voltage=6
arm_freq=2600

# Requires good cooling!
sudo reboot
```

---

## 🔋 AUTO-START ON BOOT

### Option 1: Systemd Service (Recommended)

```bash
# Create service file
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/sentinel.service << 'EOF'
[Unit]
Description=Sentinel Telegram Bot
After=network-online.target ollama.service
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/home/pi/sentinel
EnvironmentFile=/home/pi/.sentinel_env
ExecStart=/home/pi/sentinel/.venv/bin/python3 /home/pi/sentinel/skills/telegram_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF

# Replace 'pi' with your username if different
# Enable and start
systemctl --user enable sentinel.service
systemctl --user start sentinel.service

# Check status
systemctl --user status sentinel.service

# Enable lingering (run even when not logged in)
sudo loginctl enable-linger $USER
```

### Option 2: Cron (Simple)

```bash
# Edit crontab
crontab -e

# Add:
@reboot sleep 30 && /home/pi/.local/bin/ltl &

# Save and exit
```

---

## 📊 EXPECTED PERFORMANCE

### Raspberry Pi 5 (8GB)

```
Boot to ready:        ~45 seconds
YOLO detection:       ~200-300ms
LLM response:         ~2-3 seconds
Moondream vision:     ~5-7 seconds
Whisper transcribe:   ~3-4 seconds
Voice interaction:    ~12-15 seconds total
Memory usage:         ~3.5GB peak
```

### Raspberry Pi 4 (4GB)

```
Boot to ready:        ~60 seconds
YOLO detection:       ~300-500ms
LLM response:         ~4-6 seconds
Moondream vision:     ~8-12 seconds
Whisper transcribe:   ~5-7 seconds
Voice interaction:    ~20-25 seconds total
Memory usage:         ~3.5GB peak (uses swap)
```

### Battery Life (with UPS)

```
Pi 5 + UPS (10,000mAh): ~3-4 hours
Pi 4 + UPS (10,000mAh): ~4-5 hours
Idle power: ~5-7W
Active: ~8-12W
```

---

## 🐛 TROUBLESHOOTING

### "Out of memory" errors

```bash
# Increase swap
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# CONF_SWAPSIZE=4096
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# Limit Ollama models loaded
export OLLAMA_MAX_LOADED_MODELS=1
```

### "Illegal instruction" errors

```bash
# Make sure you're using ARM64 OS, not 32-bit
uname -m
# Should show: aarch64

# If shows armv7l, reinstall with 64-bit OS
```

### Slow performance

```bash
# Check CPU throttling
vcgencmd get_throttled
# 0x0 = good
# Other values = throttling due to heat/power

# Add cooling/better power supply
# Check temperature
vcgencmd measure_temp
# Should be < 80°C
```

### Camera not detected

```bash
# For Pi Camera Module
sudo raspi-config
# Interface Options -> Camera -> Enable

# Test
libcamera-hello

# For USB camera
ls /dev/video0
```

### Audio issues

```bash
# List audio devices
aplay -l
arecord -l

# Set default output
sudo nano /etc/asound.conf
# Set to headphone jack or HDMI

# Test
speaker-test -c 2
```

---

## 🏠 USE CASES FOR PI DEPLOYMENT

### 1. **Home Security Camera**
```bash
# Run Sentinel 24/7 as smart security camera
# Detects people, sends Telegram alerts
# Low power consumption
```

### 2. **Elderly Care Monitor**
```bash
# Voice interaction for elderly family members
# Remote monitoring via Telegram
# Fall detection with YOLO
```

### 3. **Smart Doorbell**
```bash
# Attach Pi + camera to door
# Telegram notifications when person detected
# Two-way voice communication
```

### 4. **Baby Monitor**
```bash
# Camera in baby's room
# Alerts when baby wakes up
# Voice chat to soothe remotely
```

### 5. **Workshop Assistant**
```bash
# Hands-free voice control in workshop
# Safety monitoring
# Tool tracking with vision
```

---

## 📦 PRE-CONFIGURED PI IMAGE (Optional)

### Create Your Own Image

```bash
# After setup, create image for easy deployment
sudo dd if=/dev/mmcblk0 of=sentinel-pi.img bs=4M status=progress
gzip sentinel-pi.img

# Flash to other Pi's:
gunzip -c sentinel-pi.img.gz | sudo dd of=/dev/mmcblk0 bs=4M status=progress
```

---

## 💰 COST BREAKDOWN

### Complete Setup Cost

```
Raspberry Pi 5 (8GB):        $80
Power Supply:                $12
MicroSD Card (64GB):         $10
USB Webcam:                  $15
USB Microphone:               $8
Case with Fan:               $15
──────────────────────────
Total:                      ~$140

Running cost (24/7):
Power (10W @ $0.12/kWh):    ~$1/month
Internet: Already have
──────────────────────────
Monthly:                     ~$1

Compare to cloud AI:
ChatGPT Plus:               $20/month
Cloud vision API:           $10-50/month
──────────────────────────
Cloud alternative:          $30-70/month

Payback period: ~3-5 months
```

---

## 🎯 CONCLUSION

**Sentinel on Raspberry Pi is:**
- ✅ **Feasible** - Designed for CPU-only operation
- ✅ **Affordable** - ~$140 one-time cost
- ✅ **Private** - All data stays on your Pi
- ✅ **Low power** - ~10W, runs 24/7 for ~$1/month
- ✅ **Portable** - Small form factor
- ⚠️ **Slower** - But acceptable for ambient intelligence
- ✅ **Perfect for** - Home automation, security, monitoring

**Recommended minimum:**
- Raspberry Pi 4 or 5 with 4GB+ RAM
- 32GB+ SD card (or USB SSD)
- Good cooling
- Stable power supply

**Start small, scale up:**
1. Test on desktop first
2. Deploy to Pi when ready
3. Run 24/7 as ambient intelligence

🍓 **Your privacy-first AI agent, now pocket-sized!** 🛡️
