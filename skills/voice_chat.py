#!/usr/bin/env python3
"""
Sentinel Voice Chat - Full Conversational Mode
Integrates Whisper (STT), Piper (TTS), Moondream (Vision), and Ollama (Chat)
"""

import sys
import os
import json
import time
from pathlib import Path

# Add local-talking-llm to path for imports
sys.path.insert(0, str(Path.home() / "local-talking-llm"))

try:
    from src.piper_tts import PiperTTSService
    import sounddevice as sd
    import soundfile as sf
    import whisper
    import ollama
    import cv2
    import numpy as np
except ImportError as e:
    print(json.dumps({"error": f"Missing dependency: {e}"}))
    sys.exit(1)


class VoiceChat:
    """Full conversational voice interface for Sentinel"""

    def __init__(self, config=None):
        self.config = config or {}

        # Initialize components
        print("🎤 Initializing Voice Chat...", file=sys.stderr)

        # TTS (Piper)
        try:
            voice_path = os.path.expanduser("~/.local/share/piper/en_US-lessac-medium.onnx")
            self.tts = PiperTTSService(voice_path)
            print("✓ Piper TTS loaded", file=sys.stderr)
        except Exception as e:
            print(f"⚠ TTS unavailable: {e}", file=sys.stderr)
            self.tts = None

        # STT (Whisper)
        try:
            model_size = self.config.get("whisper_model", "base.en")
            print(f"Loading Whisper {model_size}...", file=sys.stderr)
            # Force CPU to avoid CUDA compatibility issues with MX130
            self.whisper = whisper.load_model(model_size, device='cpu')
            print("✓ Whisper loaded", file=sys.stderr)
        except Exception as e:
            print(f"⚠ Whisper unavailable: {e}", file=sys.stderr)
            self.whisper = None

        # LLM (Ollama)
        self.ollama_model = self.config.get("model", "qwen2.5:3b")

        # Vision (Moondream)
        self.vision_model = "moondream"

        # Conversation history
        self.messages = [
            {
                "role": "system",
                "content": "You are Sentinel, a helpful voice assistant. Keep responses concise (1-3 sentences)."
            }
        ]

    def speak(self, text: str):
        """Convert text to speech and play"""
        if not self.tts:
            print(f"🔇 TTS unavailable. Text: {text}", file=sys.stderr)
            return

        try:
            print(f"🔊 Speaking: {text}", file=sys.stderr)
            sample_rate, audio = self.tts.synthesize(text)

            # Play audio
            sd.play(audio, sample_rate)
            sd.wait()  # Wait until audio finishes

        except Exception as e:
            print(f"⚠ TTS error: {e}", file=sys.stderr)

    def listen(self, duration=5) -> str:
        """Record audio and transcribe with Whisper"""
        if not self.whisper:
            print("⚠ Whisper unavailable", file=sys.stderr)
            return ""

        try:
            sample_rate = 16000
            print(f"🎤 Listening for {duration}s...", file=sys.stderr)

            # Record audio
            audio = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype=np.float32
            )
            sd.wait()

            print("🔄 Transcribing...", file=sys.stderr)

            # Transcribe
            audio = audio.flatten()
            result = self.whisper.transcribe(audio, language="en", fp16=False)
            text = result["text"].strip()

            print(f"📝 You said: {text}", file=sys.stderr)
            return text

        except Exception as e:
            print(f"⚠ Listen error: {e}", file=sys.stderr)
            return ""

    def capture_and_describe(self) -> str:
        """Capture image and describe with Moondream"""
        try:
            print("📸 Capturing image...", file=sys.stderr)

            # Capture from camera
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()

            if not ret:
                return "I couldn't access the camera."

            # Save temporarily
            temp_path = "/tmp/sentinel_vision.jpg"
            cv2.imwrite(temp_path, frame)

            print("🔍 Analyzing with Moondream...", file=sys.stderr)

            # Use Ollama vision model (Moondream)
            with open(temp_path, 'rb') as f:
                image_data = f.read()

            response = ollama.chat(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": "Describe what you see in this image in one sentence.",
                        "images": [image_data]
                    }
                ]
            )

            description = response["message"]["content"]
            print(f"👁️ Vision: {description}", file=sys.stderr)

            return description

        except Exception as e:
            print(f"⚠ Vision error: {e}", file=sys.stderr)
            return "I couldn't analyze the image."

    def chat(self, user_input: str) -> str:
        """Get LLM response"""
        try:
            # Add user message
            self.messages.append({"role": "user", "content": user_input})

            # Get response from Ollama
            response = ollama.chat(
                model=self.ollama_model,
                messages=self.messages
            )

            assistant_message = response["message"]["content"]

            # Add to history
            self.messages.append({"role": "assistant", "content": assistant_message})

            # Keep last 10 messages
            if len(self.messages) > 11:  # 1 system + 10 conversation
                self.messages = [self.messages[0]] + self.messages[-10:]

            return assistant_message

        except Exception as e:
            print(f"⚠ Chat error: {e}", file=sys.stderr)
            return "I'm having trouble thinking right now."

    def conversation_loop(self):
        """Interactive voice conversation"""
        print("\n🛡️ Sentinel Voice Chat Active", file=sys.stderr)
        print("━" * 50, file=sys.stderr)

        # Greeting
        greeting = "Hello! I'm Sentinel. How can I help you?"
        self.speak(greeting)

        while True:
            # Listen
            user_input = self.listen(duration=5)

            if not user_input:
                continue

            # Check for exit
            if any(word in user_input.lower() for word in ["goodbye", "exit", "quit", "stop"]):
                farewell = "Goodbye! Stay safe."
                print(f"🔊 {farewell}", file=sys.stderr)
                self.speak(farewell)
                break

            # Check for vision request
            if any(word in user_input.lower() for word in ["see", "look", "camera", "photo", "picture", "show"]):
                description = self.capture_and_describe()
                response = f"I see {description}"
            else:
                # Normal chat
                response = self.chat(user_input)

            # Speak response
            print(f"🤖 Sentinel: {response}", file=sys.stderr)
            self.speak(response)

    def text_conversation_loop(self):
        """Text-based conversation (no voice)"""
        print("\n🛡️ Sentinel Text Chat Active", file=sys.stderr)
        print("Type 'exit' to quit, 'see' to use camera\n", file=sys.stderr)

        while True:
            # Get text input
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Check for exit
            if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                print("🤖 Sentinel: Goodbye! Stay safe.")
                break

            # Check for vision
            if user_input.lower() in ["see", "look", "camera", "photo", "vision"]:
                description = self.capture_and_describe()
                response = f"I see {description}"
            else:
                # Normal chat
                response = self.chat(user_input)

            print(f"🤖 Sentinel: {response}\n")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Sentinel Voice Chat")
    parser.add_argument("--voice", action="store_true", help="Use voice mode (default: text)")
    parser.add_argument("--model", default="qwen2.5:3b", help="Ollama model")
    parser.add_argument("--whisper-model", default="base.en", help="Whisper model size")

    args = parser.parse_args()

    config = {
        "model": args.model,
        "whisper_model": args.whisper_model
    }

    chat = VoiceChat(config)

    if args.voice:
        chat.conversation_loop()
    else:
        chat.text_conversation_loop()


if __name__ == "__main__":
    main()
