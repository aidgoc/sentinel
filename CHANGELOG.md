# Changelog

All notable changes to Sentinel will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [8.0.0] - 2026-02-13

### 🎉 Major Release - Voice & CLI Features

This release transforms Sentinel into a full-featured, dual-interface AI assistant with comprehensive voice capabilities.

### ✨ Added

#### Voice Features
- **Voice Message Support in Telegram** - Send voice notes, get transcribed responses
- **Audio Responses** - Optional Piper TTS voice replies via `/voicereply` command
- **Voice Chat CLI** - Complete voice conversation mode in local interface
- **Whisper Integration** - High-quality speech-to-text transcription
- **Piper TTS Integration** - Natural-sounding voice synthesis

#### Local CLI Interface
- **Interactive Menu System** - Full-featured command-line interface
- **Text Chat Mode** - Conversational AI in terminal
- **Voice Chat Mode** - Speak and listen locally
- **Vision Capture** - Camera capture and person detection
- **System Status Dashboard** - Real-time health monitoring
- **Chat History Viewer** - Browse conversation logs
- **Settings Panel** - Configure voice, chat, and system options

#### Infrastructure
- **Automated Installation Script** - One-line installer for any Linux system
- **Dependency Management** - Automatic model downloads and setup
- **Enhanced Documentation** - Complete usage guides and troubleshooting
- **Startup Scripts** - Easy launchers for CLI and bot

### 🔧 Fixed

#### Compatibility
- **CPU-Only Mode for Whisper** - Resolved CUDA compatibility issues with MX130 GPU
- **CPU-Only Embeddings** - Fixed sentence-transformers CUDA errors
- **Environment Variables** - Proper handling in background processes
- **Model Loading** - Lazy loading for better performance

#### Stability
- **Memory Management** - Optimized for 12GB RAM systems
- **Error Handling** - Improved error messages and recovery
- **Process Management** - Better background task handling

### 📝 Changed

#### Core Improvements
- **Telegram Bot** - Enhanced with voice message handler
- **Conversation Skill** - CPU-optimized embeddings
- **Voice Chat** - CPU-optimized Whisper loading
- **Configuration** - Added `.env` template for secrets

#### User Experience
- **Documentation** - Comprehensive README, guides, and examples
- **Installation** - Streamlined setup process
- **Testing** - Added system health checks

### 🛡️ Security

- **Environment Secrets** - Sensitive data moved to `.env` (git-ignored)
- **File Permissions** - Secure storage for credentials (chmod 600)
- **Local Processing** - 100% on-device AI inference
- **No Telemetry** - Zero external tracking

### 📦 Components

#### AI Models
- Ollama with Qwen 2.5 (3B parameters)
- Whisper base.en (140MB)
- Piper lessac-medium (61MB)
- YOLOv8-nano (6MB)
- MiniLM-L6-v2 embeddings (90MB)

#### Skills
- `telegram_bot.py` - Telegram integration with voice
- `sentinel_cli.py` - Local CLI interface
- `conversation_skill.py` - LLM chat with memory
- `vision_skill.py` - Image capture and detection
- `voice_chat.py` - Voice input/output

#### Scripts
- `install.sh` - Automated installer
- `cli` - CLI launcher
- `start_bot.sh` - Bot launcher

### 📚 Documentation

- `README.md` - Complete project overview
- `VOICE_TELEGRAM_GUIDE.md` - Voice features guide
- `CHANGELOG.md` - Version history
- `VERSION` - Current version number

### 🎯 Features Working

✅ Local LLM (Ollama with qwen2.5:3b)
✅ Whisper speech-to-text (CPU mode)
✅ Piper text-to-speech
✅ Telegram bot with voice messages
✅ Audio responses (optional)
✅ Local CLI interface
✅ Voice chat in CLI
✅ SQLite chat history
✅ Vision capture & YOLO detection
✅ Persistent memory with vector search

### 🔗 Links

- **Repository**: https://github.com/aidgoc/sentinel
- **Release**: https://github.com/aidgoc/sentinel/releases/tag/v8.0.0
- **Installation**: `curl -fsSL https://raw.githubusercontent.com/aidgoc/sentinel/master/install.sh | bash`

### 👥 Contributors

- @harshwardhan - Development
- Claude Sonnet 4.5 - AI assistance

---

## [7.0.0] - 2026-02-12

### Added
- Initial Telegram bot implementation
- Basic conversation skill
- Vision skill with YOLO detection
- SQLite memory storage

### Fixed
- Database schema initialization
- Camera capture reliability

---

## Prior Versions

Earlier versions were development iterations. V8 is the first production-ready release.

---

## Release Notes Format

### Added
New features and capabilities

### Changed
Changes to existing functionality

### Deprecated
Features marked for removal

### Removed
Features that have been removed

### Fixed
Bug fixes and corrections

### Security
Security improvements and fixes

---

**Note**: This project follows semantic versioning:
- **Major** (8.x.x): Breaking changes or major new features
- **Minor** (x.0.x): New features, backwards compatible
- **Patch** (x.x.0): Bug fixes, backwards compatible
