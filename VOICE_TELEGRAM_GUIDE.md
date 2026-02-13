# 🎤 Sentinel Voice & CLI Guide

## 🆕 New Features Added

### 1. Voice Messages in Telegram ✅
Your Telegram bot now supports **voice messages**! Speak to it and get text/audio responses.

### 2. Local CLI Interface ✅
Full command-line interface with **all Telegram features** running locally.

---

## 📱 Telegram Voice Features

### How to Use Voice Messages:

1. **Start chat mode:**
   ```
   Send: /chat
   ```

2. **Send a voice message:**
   - Tap and hold the microphone icon in Telegram
   - Speak your message
   - Release to send
   - Bot will:
     - ✅ Download your voice note
     - ✅ Transcribe it with Whisper
     - ✅ Show you what it heard
     - ✅ Process with local LLM
     - ✅ Reply with text

3. **Enable audio responses (optional):**
   ```
   Send: /voicereply
   ```
   - Now the bot will also send voice replies using Piper TTS!
   - Send `/voicereply` again to disable

4. **Stop chatting:**
   ```
   Send: /endchat
   ```

### Example Telegram Workflow:

```
You: /chat
Bot: 💬 Chat mode activated!
     🎤 Voice messages supported

You: [Send voice: "What's the weather like?"]
Bot: 📝 You said: "What's the weather like?"
     🤖 I don't have access to current weather data...

You: /voicereply
Bot: 🔊 Voice replies enabled!

You: [Send voice: "Tell me a joke"]
Bot: 📝 You said: "Tell me a joke"
     🤖 Why did the programmer quit...
     [Also sends audio voice message]
```

---

## 💻 Local CLI Interface

### Starting the CLI:

**Method 1 (Simple):**
```bash
cd ~/sentinel
./cli
```

**Method 2 (Manual):**
```bash
cd ~/sentinel
source .venv/bin/activate
python3 sentinel_cli.py
```

### CLI Features:

```
🛡️  SENTINEL - Local Command-Line Interface

📋 MAIN MENU:
  1. 💬 Chat with LLM (text)
  2. 🎤 Voice Chat (speak & listen)
  3. 📸 Capture Image & Detect Person
  4. 📊 System Status
  5. 🧠 View Chat History
  6. ⚙️  Settings
  7. ❌ Exit
```

### Detailed Feature Guide:

#### 1. Text Chat 💬
- Type messages to chat with local LLM
- Same conversational AI as Telegram
- Type `exit` to return to menu
- Chat history maintained across session

```
You: Hello!
🤖 Sentinel: Hi! How can I help you today?

You: What can you do?
🤖 Sentinel: I can chat, process images, and help with tasks...
```

#### 2. Voice Chat 🎤
- Press ENTER to record 5 seconds of audio
- Whisper transcribes your speech
- LLM processes and responds
- Piper speaks the response (if enabled)
- Type `exit` to quit voice mode

```
[Press ENTER to speak, or type 'exit']
[Press ENTER]
🎤 Listening for 5 seconds... (speak now)
🔄 Transcribing...
📝 You said: "Tell me about AI"
🤖 Sentinel: Artificial Intelligence is...
🔊 Speaking...
```

#### 3. Vision Capture 📸
- Captures image from webcam
- Runs YOLO person detection
- Shows confidence score
- Option to display captured image

```
✅ Capture complete!
   Person detected: Yes ✓
   Confidence: 92.45%
   Image saved: ~/sentinel_captures/2026-02-13/11-25-30.jpg

Display image? (y/n): y
```

#### 4. System Status 📊
- Shows Ollama status
- Whisper availability
- Piper availability
- Memory/CPU usage
- Database statistics

```
Ollama: ✅ Running
Whisper (STT): ✅ Available
Piper (TTS): ✅ Available
OpenCV (Vision): ✅ Available

Memory: 45.2% (5.4GB / 12.0GB)
CPU: 23%

Memory DB: ✅ Exists
DB Size: 24.3 KB
```

#### 5. View Chat History 🧠
- Shows last 20 conversations from SQLite
- Includes both CLI and Telegram chats
- Displays session ID and timestamps

```
Showing last 5 messages:

[2026-02-13 11:05:42] USER: What is AI?
[2026-02-13 11:05:43] ASSISTANT: Artificial Intelligence...
```

#### 6. Settings ⚙️
- Toggle voice replies on/off
- Reset chat history
- View current settings

```
Voice replies: 🔊 Enabled
Chat mode: ✅ Active

Toggle Options:
  1. Toggle voice replies
  2. Reset chat history
  3. Back to main menu
```

---

## 🔄 Comparison: Telegram vs CLI

| Feature | Telegram | CLI |
|---------|----------|-----|
| Text Chat | ✅ | ✅ |
| Voice Input | ✅ (voice notes) | ✅ (microphone) |
| Voice Output | ✅ (optional) | ✅ (optional) |
| Vision Capture | ✅ | ✅ |
| System Status | ✅ `/status` | ✅ Menu option |
| Chat History | ✅ `/memory` | ✅ Menu option |
| Settings | ✅ Commands | ✅ Menu option |
| Remote Access | ✅ (anywhere) | ❌ (local only) |
| Privacy | ⚠️ (via Telegram) | ✅ (fully local) |

---

## 🚀 Quick Start Examples

### Scenario 1: Voice chat on Telegram
```
1. Open Telegram → find your Sentinel bot
2. Send: /chat
3. Tap microphone, speak: "Tell me about quantum computing"
4. Bot transcribes and responds
5. Send: /voicereply (to enable audio responses)
6. Continue voice conversation!
```

### Scenario 2: Private voice chat locally
```
1. Open terminal
2. Run: cd ~/sentinel && ./cli
3. Select: 2 (Voice Chat)
4. Press ENTER and speak
5. Listen to Piper's audio response
6. Continue conversation
7. Type 'exit' when done
```

### Scenario 3: Vision monitoring from Telegram
```
1. Send: /wake
2. Bot captures image and analyzes
3. Receive photo + detection results
4. If person detected → safety questions start
```

### Scenario 4: Check system locally
```
1. Run: cd ~/sentinel && ./cli
2. Select: 4 (System Status)
3. View all system metrics
4. Press Enter to return
```

---

## 🛠️ Troubleshooting

### Voice messages not working in Telegram:
```bash
# Check if bot is running
ps aux | grep telegram_bot

# Check logs
tail -f ~/sentinel/logs/telegram_bot.log

# Restart bot
cd ~/sentinel && ./start_bot.sh
```

### CLI not launching:
```bash
# Activate environment
cd ~/sentinel
source .venv/bin/activate

# Check dependencies
pip list | grep -E "whisper|piper|ollama"

# Run directly
python3 sentinel_cli.py
```

### Voice input/output not working:
```bash
# Test microphone
arecord -d 3 test.wav && aplay test.wav

# Check Whisper
python3 -c "import whisper; print('Whisper OK')"

# Check Piper
python3 -c "from src.piper_tts import PiperTTSService; print('Piper OK')"
```

### Ollama not responding:
```bash
# Check if running
curl http://localhost:11434/api/tags

# Start if needed
ollama serve

# Test model
ollama run qwen2.5:3b "Hello"
```

---

## 📊 Resource Usage

| Component | Memory | Notes |
|-----------|--------|-------|
| Telegram Bot | ~50MB | Running in background |
| CLI (idle) | ~30MB | Minimal footprint |
| Whisper (loaded) | ~500MB | Loaded on first use |
| Piper (loaded) | ~100MB | Loaded on first use |
| Ollama | ~2GB | qwen2.5:3b model |
| **Total Active** | ~2.7GB | All components running |

---

## 🎯 Best Practices

1. **For remote access:** Use Telegram bot
2. **For privacy:** Use local CLI
3. **For voice conversations:** CLI provides better audio quality
4. **For monitoring:** Telegram provides mobile access
5. **For debugging:** CLI shows real-time status

---

## 📝 Tips & Tricks

### Telegram Tips:
- Use `/voicereply` only when you want audio responses (saves bandwidth)
- Send voice messages in quiet environment for better transcription
- Keep voice messages under 30 seconds for faster processing

### CLI Tips:
- Voice chat works best in a quiet room
- Speak clearly and wait for transcription before speaking again
- Use text chat if you need to copy/paste code or long text
- Press Ctrl+C to exit any mode safely

### General:
- Chat history is shared between Telegram and CLI
- All processing happens locally (except Telegram API)
- Voice models are loaded on first use (may take a moment)
- CUDA is disabled to avoid compatibility issues

---

## 🔒 Security Notes

- ✅ All AI processing runs locally on your machine
- ✅ Voice data never sent to cloud (except via Telegram infrastructure)
- ✅ Ollama, Whisper, and Piper are 100% offline
- ✅ Telegram bot token stored securely in `.env` (permissions: 600)
- ⚠️ Voice messages sent via Telegram are encrypted but pass through Telegram servers

---

## 📚 Command Reference

### Telegram Commands:
```
/start      - Show welcome message
/chat       - Start chat mode
/voicereply - Toggle audio responses
/endchat    - Stop chat mode
/wake       - Trigger vision capture
/status     - System health check
/memory     - View conversation history
/help       - Show commands
```

### CLI Shortcuts:
```
./cli                    - Launch CLI
./start_bot.sh          - Start Telegram bot
kill $(cat /tmp/sentinel_bot.pid)  - Stop bot
```

---

## 🎉 You're All Set!

Both Telegram voice and local CLI are fully operational. Choose the interface that suits your needs:

- **On the go?** → Use Telegram
- **At home?** → Use CLI for better privacy
- **Need voice?** → Both support it!
- **Need vision?** → Both can capture and analyze

Enjoy your fully-featured Sentinel system! 🛡️
