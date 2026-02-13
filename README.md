# 🛡️ Sentinel V8

> **Privacy-First AI Assistant with Voice, Vision & Chat**
> Run your own AI assistant entirely on your hardware. No cloud required.

[![Version](https://img.shields.io/badge/version-8.0.0-blue.svg)](https://github.com/aidgoc/sentinel/releases/tag/v8.0.0)
[![Platform](https://img.shields.io/badge/platform-Linux-green.svg)]()
[![Python](https://img.shields.io/badge/python-3.11+-yellow.svg)]()
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

---

## ✨ What is Sentinel?

Sentinel is a **100% local AI assistant** that combines:
- 🧠 **Local LLM** (Ollama with Qwen 2.5)
- 🎤 **Voice Input** (Whisper speech-to-text)
- 🔊 **Voice Output** (Piper text-to-speech)
- 👁️ **Computer Vision** (YOLOv8 person detection)
- 💬 **Dual Interface** (Telegram bot + local CLI)
- 🧠 **Persistent Memory** (SQLite with vector embeddings)

**Everything runs on your device. Your data never leaves your machine.**

---

## 🎯 Features

### Core Capabilities
- ✅ **Text Chat** - Conversational AI powered by local LLM
- ✅ **Voice Conversations** - Speak and listen using Whisper + Piper
- ✅ **Vision Detection** - Real-time person detection via webcam
- ✅ **Memory System** - Persistent conversation history with vector search
- ✅ **Telegram Integration** - Control via Telegram bot (optional)
- ✅ **Local CLI** - Full-featured command-line interface

### Privacy & Security
- 🔐 **100% Local Processing** - No cloud APIs required
- 🔒 **Encrypted Storage** - Sensitive data protected
- 🚫 **No Telemetry** - Zero tracking or analytics
- ⚡ **Offline Capable** - Works without internet (Telegram optional)

---

## 📋 System Requirements

### Minimum Hardware
- **CPU**: 4 cores (Intel i5 or equivalent)
- **RAM**: 8GB (12GB recommended)
- **Storage**: 10GB free space
- **GPU**: Optional (NVIDIA with CUDA 7.0+)

### Software Requirements
- **OS**: Linux (Ubuntu 20.04+, Debian 11+, or similar)
- **Python**: 3.11 or higher
- **Optional**: Webcam for vision features
- **Optional**: Microphone for voice input

### Tested On
- ✅ Ubuntu 22.04 LTS
- ✅ Debian 12
- ✅ Pop!_OS 22.04
- ✅ HP Pavilion x360 (i7-8550U, 12GB RAM, MX130)

---

## 🚀 Quick Start

### One-Line Installation

```bash
curl -fsSL https://raw.githubusercontent.com/aidgoc/sentinel/master/install.sh | bash
```

### Manual Installation

```bash
# Clone repository
git clone https://github.com/aidgoc/sentinel.git
cd sentinel

# Run installer
chmod +x install.sh
./install.sh

# Configure (add your Telegram bot token)
nano .env

# Start local CLI
./cli
```

---

## 📖 Usage

### Local CLI Interface

Start the interactive menu:

```bash
cd ~/sentinel
./cli
```

**Menu Options:**
1. 💬 **Chat with LLM** - Text-based conversation
2. 🎤 **Voice Chat** - Speak and listen
3. 📸 **Capture Image** - Vision detection
4. 📊 **System Status** - Health check
5. 🧠 **View History** - Chat logs
6. ⚙️ **Settings** - Configuration
7. ❌ **Exit**

### Telegram Bot

**Setup:**
1. Get bot token from [@BotFather](https://t.me/botfather)
2. Add token to `~/sentinel/.env`
3. Start bot: `cd ~/sentinel && ./start_bot.sh`

**Commands:**
- `/chat` - Start conversation
- `/voicereply` - Toggle audio responses
- `/wake` - Trigger vision capture
- `/status` - System health
- `/memory` - View chat history

**Voice Messages:**
- Send voice notes in Telegram
- Bot transcribes with Whisper
- Responds with text or audio

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│          SENTINEL V8 ARCHITECTURE           │
├─────────────────────────────────────────────┤
│                                             │
│  ┌───────────┐         ┌────────────┐      │
│  │ Telegram  │◄────────┤   Local    │      │
│  │    Bot    │         │    CLI     │      │
│  └─────┬─────┘         └──────┬─────┘      │
│        │                      │             │
│        └──────────┬───────────┘             │
│                   │                         │
│         ┌─────────▼─────────┐               │
│         │  Core Controller  │               │
│         └─────────┬─────────┘               │
│                   │                         │
│    ┌──────────────┼──────────────┐          │
│    │              │              │          │
│ ┌──▼──┐      ┌───▼────┐    ┌───▼───┐       │
│ │ LLM │      │ Vision │    │ Voice │       │
│ │Ollam│      │ YOLO   │    │Whisper│       │
│ └──┬──┘      └───┬────┘    │ Piper │       │
│    │             │          └───┬───┘       │
│    │             │              │           │
│    └─────────────┼──────────────┘           │
│                  │                          │
│            ┌─────▼──────┐                   │
│            │   SQLite   │                   │
│            │   Memory   │                   │
│            └────────────┘                   │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 📦 Components

### AI Models
| Component | Model | Size | Purpose |
|-----------|-------|------|---------|
| **LLM** | Qwen 2.5 (3B) | 1.9GB | Conversation |
| **STT** | Whisper base.en | 140MB | Speech-to-text |
| **TTS** | Piper lessac-medium | 61MB | Text-to-speech |
| **Vision** | YOLOv8-nano | 6MB | Person detection |
| **Embeddings** | MiniLM-L6-v2 | 90MB | Vector search |

### Skills
- `conversation_skill.py` - LLM chat with memory
- `vision_skill.py` - Image capture + YOLO detection
- `voice_chat.py` - Voice input/output handler
- `telegram_bot.py` - Telegram integration
- `sentinel_cli.py` - Local CLI interface

---

## ⚙️ Configuration

### Environment Variables

Edit `~/sentinel/.env`:

```bash
# Required for Telegram bot
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Optional: Cloud LLM fallback
# ANTHROPIC_API_KEY=your_api_key_here
```

### Config File

Edit `~/sentinel/config/sentinel.yaml`:

```yaml
llm:
  provider: "ollama"
  model: "qwen2.5:3b"
  temperature: 0.7

vision:
  confidence_threshold: 0.85
  temporal_frames: 3

conversation:
  questions:
    - "What task are you performing?"
    - "Are safety protocols confirmed?"
    - "Do you require tool access?"
```

---

## 🧪 Testing

### Quick System Test

```bash
cd ~/sentinel
./cli
# Select: 4 (System Status)
```

### Test Individual Components

```bash
# Activate environment
source ~/sentinel/.venv/bin/activate

# Test Ollama
curl http://localhost:11434/api/tags

# Test vision
python3 ~/sentinel/skills/vision_skill.py

# Test conversation
echo '{"session_id":"test","trigger_conversation":true}' | \
  python3 ~/sentinel/skills/conversation_skill.py
```

---

## 🔧 Troubleshooting

### Ollama Not Starting
```bash
# Start manually
ollama serve

# Or via systemd
sudo systemctl start ollama
```

### Python Dependencies
```bash
cd ~/sentinel
source .venv/bin/activate
pip install -r requirements.txt
```

### Camera Not Working
```bash
# Check camera
v4l2-ctl --list-devices

# Test with OpenCV
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAIL')"
```

### Voice Not Working
```bash
# Test microphone
arecord -d 3 test.wav && aplay test.wav

# Force CPU mode (if CUDA issues)
export CUDA_VISIBLE_DEVICES=""
```

---

## 📚 Documentation

- **[Quick Start Guide](QUICK_START.md)** - Get started in 5 minutes
- **[Voice & CLI Guide](VOICE_TELEGRAM_GUIDE.md)** - Complete voice features guide
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment
- **[Command Reference](COMMAND_REFERENCE.md)** - All commands

---

## 🛣️ Roadmap

### V8 (Current) ✅
- ✅ Local LLM integration
- ✅ Voice input/output
- ✅ Telegram bot with voice messages
- ✅ Local CLI interface
- ✅ Vision detection
- ✅ Persistent memory

### Future Versions
- [ ] Multi-camera support
- [ ] Custom wake word detection
- [ ] Web dashboard
- [ ] Mobile app (React Native)
- [ ] Docker deployment
- [ ] Kubernetes support
- [ ] Plugin system

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open pull request

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

- **[Ollama](https://ollama.ai)** - Local LLM serving
- **[OpenAI Whisper](https://github.com/openai/whisper)** - Speech recognition
- **[Piper TTS](https://github.com/rhasspy/piper)** - Text-to-speech
- **[Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)** - Object detection
- **[Sentence Transformers](https://www.sbert.net/)** - Embeddings

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/aidgoc/sentinel/issues)
- **Discussions**: [GitHub Discussions](https://github.com/aidgoc/sentinel/discussions)
- **Email**: support@sentinel.local

---

## ⭐ Star History

If you find Sentinel useful, please star the repository!

---

**Built with ❤️ for privacy and security**

**Sentinel V8** - Your personal AI assistant, running entirely on your hardware.

🛡️ **Stay private. Stay secure. Stay in control.**
