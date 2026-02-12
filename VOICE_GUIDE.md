# 🎤 SENTINEL VOICE GUIDE

## 🎯 THREE WAYS TO TALK TO SENTINEL

### 1. 💬 **Text Chat** (Keyboard)
```bash
ltl chat
```

Then type naturally:
```
You: Hello Sentinel
🤖 Sentinel: Hello! How can I help you?

You: What's the weather like?
🤖 Sentinel: I can check the weather for you...

You: see
🤖 Sentinel: I see [describes what camera sees]

You: exit
```

**Features:**
- ✅ Full conversation (not just safety questions!)
- ✅ Vision on demand (type "see")
- ✅ Uses Moondream for vision analysis
- ✅ Context-aware (remembers conversation)

---

### 2. 🎤 **Voice Chat** (Microphone)
```bash
ltl voice
```

Then speak naturally:
```
🎤 Listening for 5s...
[You speak: "Hello Sentinel"]

🔊 Speaking: Hello! How can I help you?

🎤 Listening for 5s...
[You speak: "Show me what you see"]

📸 Capturing image...
🔍 Analyzing with Moondream...
🔊 Speaking: I see a desk with a laptop and some books.

[Say "goodbye" to exit]
```

**Features:**
- ✅ Whisper STT (speech-to-text)
- ✅ Piper TTS (text-to-speech)
- ✅ Hands-free operation
- ✅ Vision integration (say "show me", "what do you see")

---

### 3. 📱 **Telegram Bot** (Remote)
```bash
ltl
```

Then use Telegram:
```
/wake   → Takes photo, asks safety questions
/status → Shows system health
/memory → Shows conversation history
```

---

## 🎯 QUICK COMPARISON

| Mode | Command | Input | Output | Vision | Best For |
|------|---------|-------|--------|--------|----------|
| **Text** | `ltl chat` | Keyboard | Text | Type "see" | Quick queries |
| **Voice** | `ltl voice` | Microphone | Speech | Say "show me" | Hands-free |
| **Telegram** | `ltl` | Phone app | Messages + Images | `/wake` | Remote control |

---

## 🎤 VOICE MODE DETAILS

### What You Can Say:

**General Conversation:**
- "Hello Sentinel"
- "What's 2 plus 2?"
- "Tell me a joke"
- "What can you do?"

**Vision Requests:**
- "Show me what you see"
- "Look at this"
- "Take a picture"
- "What's in front of you?"
- "Describe the room"

**Exit:**
- "Goodbye"
- "Exit"
- "Quit"
- "Stop"

### How It Works:

```
1. Whisper records 5 seconds of audio
2. Transcribes to text
3. Sends to Ollama (qwen2.5:3b)
4. Gets response
5. Piper speaks response
6. Repeat
```

**Models Used:**
- **STT**: Whisper base.en (~150MB)
- **LLM**: qwen2.5:3b (1.9GB)
- **Vision**: Moondream (1.7GB)
- **TTS**: Piper en_US-lessac-medium (~60MB)

---

## 💬 TEXT MODE DETAILS

### What You Can Type:

**Conversation:**
- Type anything naturally
- Sentinel responds conversationally
- Remembers last 10 messages

**Vision:**
- Type: `see` or `look` or `camera`
- Sentinel captures photo and describes it

**Exit:**
- Type: `exit` or `quit` or `bye`

### Example Session:

```bash
$ ltl chat

🛡️ Sentinel Text Chat Active
Type 'exit' to quit, 'see' to use camera

You: hi
🤖 Sentinel: Hello! How can I help you today?

You: what models do you use?
🤖 Sentinel: I use qwen2.5:3b for chat and Moondream for vision. Would you like to know more?

You: see
📸 Capturing image...
🔍 Analyzing with Moondream...
🤖 Sentinel: I see a computer monitor displaying code, with a keyboard in front of it.

You: thanks, bye
🤖 Sentinel: Goodbye! Stay safe.
```

---

## 🔧 CONFIGURATION

### Change Whisper Model:

```bash
# Faster (less accurate)
ltl voice --whisper-model tiny.en

# Default (balanced)
ltl voice --whisper-model base.en

# Better (slower)
ltl voice --whisper-model small.en
```

### Change LLM Model:

```bash
# Use Gemma3 instead
ltl chat --model gemma3

# Or edit config/sentinel.yaml
llm:
  model: "gemma3"
```

### Adjust Listening Duration:

Edit `skills/voice_chat.py`:
```python
# Line ~85: Change duration
user_input = self.listen(duration=10)  # Listen for 10 seconds
```

---

## 🎯 VOICE REQUIREMENTS

### Hardware:
- ✅ Microphone (built-in or USB)
- ✅ Speakers or headphones
- ✅ Webcam (for vision features)

### Software:
- ✅ Whisper (base.en model) - **Auto-downloads on first run**
- ✅ Piper voice model - **Check if exists:**

```bash
ls ~/.local/share/piper/en_US-lessac-medium.onnx
```

If missing, download from your local-talking-llm:
```bash
cp ~/local-talking-llm/.local/share/piper/* ~/.local/share/piper/ 2>/dev/null || \
  echo "Download manually from: https://github.com/rhasspy/piper/releases"
```

---

## 🐛 TROUBLESHOOTING

### "Microphone not found"
```bash
# List audio devices
python3 -c "import sounddevice; print(sounddevice.query_devices())"

# Test recording
python3 -c "import sounddevice as sd; import numpy as np; print('Recording...'); audio = sd.rec(16000, samplerate=16000, channels=1); sd.wait(); print('Done!')"
```

### "Piper voice not found"
```bash
# Check if voice exists
ls ~/.local/share/piper/

# If missing, copy from local-talking-llm or download:
# https://github.com/rhasspy/piper/releases/download/v1.2.0/voice-en-us-lessac-medium.tar.gz
```

### "Whisper model downloading..."
First run downloads ~150MB model. This is normal. Wait for it to complete.

### "CUDA error" in voice mode
Voice uses CPU only (no GPU needed). If you see CUDA errors, they're safe to ignore.

---

## 🎁 PRO TIPS

### 1. Faster Voice Response
```bash
# Use tiny Whisper model (less accurate but instant)
ltl voice --whisper-model tiny.en
```

### 2. Background Noise
If Sentinel has trouble hearing you:
- Speak louder and clearer
- Move closer to microphone
- Reduce background noise
- Use a better microphone

### 3. Vision Quality
For better vision descriptions:
```bash
# Use better lighting
# Point camera at subject
# Say "show me what you see" clearly
```

### 4. Continuous Listening
Currently listens for 5 seconds at a time. To make it continuous, we'd need wake word detection (future feature).

---

## 📊 PERFORMANCE

**Voice Mode:**
- Recording: 5 seconds
- Transcription: ~2-3 seconds (base.en)
- LLM Response: ~1.5 seconds
- TTS: ~1 second
- **Total**: ~10 seconds per interaction

**Text Mode:**
- LLM Response: ~1.5 seconds
- **Total**: ~2 seconds per interaction

**Vision (Either Mode):**
- Capture: ~0.3 seconds
- Moondream Analysis: ~3-5 seconds
- **Total**: ~5 seconds

---

## 🚀 QUICK START

### Simplest Test (Text):
```bash
ltl chat
```
Type: `hi`

### Voice Test:
```bash
ltl voice
```
Say: `Hello Sentinel`

### Vision Test:
```bash
ltl chat
```
Type: `see`

**That's it! Enjoy your voice-enabled ambient intelligence agent!** 🎤🛡️
