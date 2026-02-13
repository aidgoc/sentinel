#!/usr/bin/env python3
"""
Sentinel CLI - Local Command-Line Interface
All Telegram features available locally with interactive menu
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Add paths
sys.path.insert(0, str(Path.home() / "local-talking-llm"))

# Imports
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    print("⚠ Warning: ollama-python not installed")
    OLLAMA_AVAILABLE = False

try:
    import whisper
    import sounddevice as sd
    import numpy as np
    WHISPER_AVAILABLE = True
except ImportError:
    print("⚠ Warning: Whisper/sounddevice not available - voice input disabled")
    WHISPER_AVAILABLE = False

try:
    from src.piper_tts import PiperTTSService
    import soundfile as sf
    PIPER_AVAILABLE = True
except ImportError:
    print("⚠ Warning: Piper TTS not available - voice output disabled")
    PIPER_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    print("⚠ Warning: OpenCV not available - vision disabled")
    CV2_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    print("⚠ Warning: psutil not available - status disabled")
    PSUTIL_AVAILABLE = False


class SentinelCLI:
    """Interactive CLI for Sentinel"""

    def __init__(self):
        self.sentinel_home = Path.home() / "sentinel"
        self.skills_path = self.sentinel_home / "skills"
        self.memory_db = Path.home() / ".openclaw-sentinel" / "sentinel_memory.db"

        # Conversation state
        self.chat_active = False
        self.voice_reply_enabled = False
        self.chat_history = [
            {"role": "system", "content": "You are Sentinel, a helpful AI assistant. Keep responses concise and friendly."}
        ]

        # Lazy-loaded models
        self.whisper_model = None
        self.piper_tts = None

    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name != 'nt' else 'cls')

    def print_header(self):
        """Print application header"""
        self.clear_screen()
        print("=" * 60)
        print("🛡️  SENTINEL - Local Command-Line Interface")
        print("=" * 60)
        print()

    def print_menu(self):
        """Print main menu"""
        print("\n📋 MAIN MENU:")
        print("─" * 60)
        print("  1. 💬 Chat with LLM (text)")
        print("  2. 🎤 Voice Chat (speak & listen)")
        print("  3. 📸 Capture Image & Detect Person")
        print("  4. 📊 System Status")
        print("  5. 🧠 View Chat History")
        print("  6. ⚙️  Settings")
        print("  7. ❌ Exit")
        print("─" * 60)

    def load_whisper(self):
        """Lazy load Whisper model"""
        if self.whisper_model is None and WHISPER_AVAILABLE:
            print("🔄 Loading Whisper model...")
            self.whisper_model = whisper.load_model("base.en", device="cpu")
            print("✓ Whisper loaded")
        return self.whisper_model

    def load_piper(self):
        """Lazy load Piper TTS"""
        if self.piper_tts is None and PIPER_AVAILABLE:
            print("🔄 Loading Piper TTS...")
            voice_path = os.path.expanduser("~/.local/share/piper/en_US-lessac-medium.onnx")
            self.piper_tts = PiperTTSService(voice_path)
            print("✓ Piper loaded")
        return self.piper_tts

    def speak(self, text):
        """Speak text using Piper TTS"""
        if not self.voice_reply_enabled or not PIPER_AVAILABLE:
            return

        try:
            tts = self.load_piper()
            if tts:
                print("🔊 Speaking...")
                sample_rate, audio = tts.synthesize(text)
                sd.play(audio, sample_rate)
                sd.wait()
        except Exception as e:
            print(f"⚠ TTS error: {e}")

    def listen(self, duration=5):
        """Record audio and transcribe"""
        if not WHISPER_AVAILABLE:
            print("❌ Whisper not available")
            return None

        try:
            model = self.load_whisper()
            if not model:
                return None

            sample_rate = 16000
            print(f"🎤 Listening for {duration} seconds... (speak now)")

            # Record
            audio = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype=np.float32
            )
            sd.wait()
            print("🔄 Transcribing...")

            # Transcribe
            audio = audio.flatten()
            result = model.transcribe(audio, language="en", fp16=False)
            text = result["text"].strip()

            if text:
                print(f"📝 You said: \"{text}\"")
            return text

        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    def chat_with_llm(self, user_input):
        """Send message to LLM and get response"""
        if not OLLAMA_AVAILABLE:
            print("❌ Ollama not available")
            return None

        try:
            self.chat_history.append({"role": "user", "content": user_input})

            response = ollama.chat(
                model="qwen2.5:3b",
                messages=self.chat_history
            )

            assistant_message = response["message"]["content"]
            self.chat_history.append({"role": "assistant", "content": assistant_message})

            # Keep last 10 messages
            if len(self.chat_history) > 11:
                self.chat_history = [self.chat_history[0]] + self.chat_history[-10:]

            return assistant_message

        except Exception as e:
            print(f"❌ LLM error: {e}")
            return None

    def text_chat(self):
        """Text-based chat mode"""
        self.print_header()
        print("💬 TEXT CHAT MODE")
        print("─" * 60)
        print("Chat with Sentinel using text. Type 'exit' to return to menu.\n")

        self.chat_active = True

        while self.chat_active:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'quit', 'back']:
                    print("👋 Exiting chat mode...")
                    self.chat_active = False
                    break

                # Get LLM response
                response = self.chat_with_llm(user_input)

                if response:
                    print(f"\n🤖 Sentinel: {response}\n")
                    self.speak(response)

            except KeyboardInterrupt:
                print("\n\n👋 Exiting chat mode...")
                self.chat_active = False
                break

    def voice_chat(self):
        """Voice-based chat mode"""
        self.print_header()
        print("🎤 VOICE CHAT MODE")
        print("─" * 60)

        if not WHISPER_AVAILABLE:
            print("❌ Whisper not available. Voice chat disabled.")
            input("\nPress Enter to continue...")
            return

        print("Speak to Sentinel! Press Enter to record, or type 'exit' to quit.\n")

        self.chat_active = True
        self.voice_reply_enabled = True

        while self.chat_active:
            try:
                command = input("\n[Press ENTER to speak, or type 'exit'] ").strip()

                if command.lower() in ['exit', 'quit', 'back']:
                    print("👋 Exiting voice chat...")
                    self.chat_active = False
                    self.voice_reply_enabled = False
                    break

                # Listen
                user_input = self.listen(duration=5)

                if not user_input:
                    print("⚠ No speech detected. Try again.")
                    continue

                # Get LLM response
                response = self.chat_with_llm(user_input)

                if response:
                    print(f"\n🤖 Sentinel: {response}\n")
                    self.speak(response)

            except KeyboardInterrupt:
                print("\n\n👋 Exiting voice chat...")
                self.chat_active = False
                self.voice_reply_enabled = False
                break

    def vision_capture(self):
        """Capture image and detect person"""
        self.print_header()
        print("📸 VISION CAPTURE")
        print("─" * 60)

        try:
            # Execute vision skill
            result = subprocess.run(
                ["python3", str(self.skills_path / "vision_skill.py")],
                capture_output=True,
                text=True,
                env={**os.environ, "CUDA_VISIBLE_DEVICES": ""}
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                person_present = data.get("person_present", False)
                confidence = data.get("confidence", 0.0)
                image_path = data.get("image_path")

                print(f"\n✅ Capture complete!")
                print(f"   Person detected: {'Yes ✓' if person_present else 'No ✗'}")
                print(f"   Confidence: {confidence:.2%}")
                print(f"   Image saved: {image_path}")

                if CV2_AVAILABLE and image_path and os.path.exists(image_path):
                    show = input("\nDisplay image? (y/n): ").lower()
                    if show == 'y':
                        img = cv2.imread(image_path)
                        cv2.imshow("Sentinel Capture", img)
                        print("Press any key in the image window to close...")
                        cv2.waitKey(0)
                        cv2.destroyAllWindows()

            else:
                print(f"❌ Vision skill failed:\n{result.stderr}")

        except Exception as e:
            print(f"❌ Error: {e}")

        input("\nPress Enter to continue...")

    def show_status(self):
        """Show system status"""
        self.print_header()
        print("📊 SYSTEM STATUS")
        print("─" * 60)

        # Ollama status
        ollama_status = "✅ Running" if os.system("curl -s http://localhost:11434/api/tags > /dev/null 2>&1") == 0 else "❌ Offline"
        print(f"Ollama: {ollama_status}")

        # Whisper
        whisper_status = "✅ Available" if WHISPER_AVAILABLE else "❌ Not available"
        print(f"Whisper (STT): {whisper_status}")

        # Piper
        piper_status = "✅ Available" if PIPER_AVAILABLE else "❌ Not available"
        print(f"Piper (TTS): {piper_status}")

        # OpenCV
        cv_status = "✅ Available" if CV2_AVAILABLE else "❌ Not available"
        print(f"OpenCV (Vision): {cv_status}")

        if PSUTIL_AVAILABLE:
            print()
            mem = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)
            print(f"Memory: {mem.percent}% ({mem.used / 1e9:.1f}GB / {mem.total / 1e9:.1f}GB)")
            print(f"CPU: {cpu}%")

        # Database
        print()
        db_status = "✅ Exists" if self.memory_db.exists() else "❌ Not found"
        print(f"Memory DB: {db_status}")
        if self.memory_db.exists():
            size = self.memory_db.stat().st_size / 1024
            print(f"DB Size: {size:.1f} KB")

        input("\nPress Enter to continue...")

    def view_history(self):
        """View chat history from database"""
        self.print_header()
        print("🧠 CHAT HISTORY")
        print("─" * 60)

        if not self.memory_db.exists():
            print("❌ Memory database not found")
            input("\nPress Enter to continue...")
            return

        try:
            import sqlite3
            conn = sqlite3.connect(self.memory_db)
            rows = conn.execute(
                "SELECT session_id, timestamp, role, content FROM conversations ORDER BY timestamp DESC LIMIT 20"
            ).fetchall()

            if not rows:
                print("ℹ️  No conversations recorded yet")
            else:
                print(f"\nShowing last {len(rows)} messages:\n")
                for row in rows:
                    session_id, timestamp, role, content = row
                    print(f"[{timestamp}] {role.upper()}: {content[:80]}...")
                    print()

            conn.close()

        except Exception as e:
            print(f"❌ Error: {e}")

        input("\nPress Enter to continue...")

    def settings(self):
        """Settings menu"""
        self.print_header()
        print("⚙️  SETTINGS")
        print("─" * 60)

        print(f"\nVoice replies: {'🔊 Enabled' if self.voice_reply_enabled else '🔇 Disabled'}")
        print(f"Chat mode: {'✅ Active' if self.chat_active else '❌ Inactive'}")

        print("\nToggle Options:")
        print("  1. Toggle voice replies")
        print("  2. Reset chat history")
        print("  3. Back to main menu")

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            self.voice_reply_enabled = not self.voice_reply_enabled
            status = "enabled" if self.voice_reply_enabled else "disabled"
            print(f"✓ Voice replies {status}")
            time.sleep(1)

        elif choice == "2":
            confirm = input("Reset chat history? (y/n): ").lower()
            if confirm == 'y':
                self.chat_history = [self.chat_history[0]]  # Keep system prompt
                print("✓ Chat history reset")
                time.sleep(1)

    def run(self):
        """Main application loop"""
        while True:
            self.print_header()
            self.print_menu()

            choice = input("\nSelect option (1-7): ").strip()

            if choice == "1":
                self.text_chat()
            elif choice == "2":
                self.voice_chat()
            elif choice == "3":
                self.vision_capture()
            elif choice == "4":
                self.show_status()
            elif choice == "5":
                self.view_history()
            elif choice == "6":
                self.settings()
            elif choice == "7":
                self.print_header()
                print("👋 Goodbye! Stay safe.\n")
                sys.exit(0)
            else:
                print("❌ Invalid option. Please try again.")
                time.sleep(1)


if __name__ == "__main__":
    # Force CPU usage
    os.environ["CUDA_VISIBLE_DEVICES"] = ""

    print("\n🛡️  Initializing Sentinel CLI...")
    time.sleep(1)

    cli = SentinelCLI()
    cli.run()
