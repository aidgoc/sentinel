#!/usr/bin/env python3
"""
Sentinel Telegram Bot - Week 2 Integration
Handles Telegram commands and webhook for conversation replies
"""

import os
import re
import sys
import json
import logging
import asyncio
from pathlib import Path

# DuckDuckGo search (no API key needed)
try:
    from ddgs import DDGS
    SEARCH_AVAILABLE = True
except ImportError:
    SEARCH_AVAILABLE = False

# Check if python-telegram-bot is available
try:
    from telegram import Update
    from telegram.ext import (
        Application,
        CommandHandler,
        MessageHandler,
        filters,
        ContextTypes,
    )
except ImportError:
    print("Error: python-telegram-bot not installed")
    print("Install: pip install python-telegram-bot")
    sys.exit(1)

# Check if ollama is available
try:
    import ollama
except ImportError:
    print("Error: ollama-python not installed")
    print("Install: pip install ollama")
    sys.exit(1)

# Voice processing imports
try:
    import whisper
    import numpy as np
    import soundfile as sf
    WHISPER_AVAILABLE = True
except ImportError:
    logger.warning("Whisper not available - voice messages will not work")
    WHISPER_AVAILABLE = False

try:
    sys.path.insert(0, str(Path.home() / "local-talking-llm"))
    from src.piper_tts import PiperTTSService
    PIPER_AVAILABLE = True
except ImportError:
    logger.warning("Piper TTS not available - voice responses disabled")
    PIPER_AVAILABLE = False

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USERS = os.getenv("TELEGRAM_ALLOWED_USERS", "").split(",")

# Sentinel paths
SENTINEL_HOME = Path.home() / "sentinel"
SKILLS_PATH = SENTINEL_HOME / "skills"
CAPTURES_PATH = Path.home() / "sentinel_captures"
MEMORY_DB = Path.home() / ".openclaw-sentinel" / "sentinel_memory.db"

# Conversation state (simple in-memory for demo)
user_sessions = {}

# Chat mode (for general LLM conversation)
chat_mode = {}

# Voice mode settings
voice_mode = {}

# Initialize Whisper model (lazy loading)
whisper_model = None

# Initialize Piper TTS (lazy loading)
piper_tts = None

def get_whisper_model():
    """Lazy load Whisper model"""
    global whisper_model
    if whisper_model is None and WHISPER_AVAILABLE:
        logger.info("Loading Whisper model...")
        whisper_model = whisper.load_model("base.en", device="cpu")
    return whisper_model

def get_piper_tts():
    """Lazy load Piper TTS"""
    global piper_tts
    if piper_tts is None and PIPER_AVAILABLE:
        logger.info("Loading Piper TTS...")
        voice_path = os.path.expanduser("~/.local/share/piper/en_US-lessac-medium.onnx")
        piper_tts = PiperTTSService(voice_path)
    return piper_tts


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    voice_status = "🎤 Voice messages supported" if WHISPER_AVAILABLE else ""

    await update.message.reply_text(
        f"🛡️ Sentinel Active\n\n"
        f"Hello {user.first_name}!\n\n"
        f"Available commands:\n"
        f"/wake - Trigger immediate capture\n"
        f"/chat - Start conversing with local LLM\n"
        f"/search <query> - Web search + LLM summary\n"
        f"/voicereply - Toggle audio responses\n"
        f"/endchat - Stop chat mode\n"
        f"/status - System health\n"
        f"/memory - Search conversations\n"
        f"/help - Show this message\n\n"
        f"{voice_status}"
    )


async def wake_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /wake - immediate vision capture"""
    await update.message.reply_text("🔍 Triggering vision capture...")

    # Execute vision skill
    import subprocess
    result = subprocess.run(
        ["python3", str(SKILLS_PATH / "vision_skill.py")],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            person_present = data.get("person_present", False)
            confidence = data.get("confidence", 0.0)
            image_path = data.get("image_path")

            response = f"✅ Capture complete\n\n"
            response += f"Person detected: {' Yes' if person_present else 'No'}\n"
            response += f"Confidence: {confidence:.2%}\n"

            if image_path and os.path.exists(image_path):
                # Send image to user
                with open(image_path, 'rb') as img:
                    await update.message.reply_photo(
                        photo=img,
                        caption=f"Detection: {'Person found' if person_present else 'No person'} ({confidence:.2%})"
                    )
            else:
                await update.message.reply_text(response)

            # If person detected, start conversation
            if person_present:
                await start_conversation(update, context)

        except json.JSONDecodeError:
            await update.message.reply_text(f"❌ Invalid response from vision skill\n{result.stdout}")
    else:
        await update.message.reply_text(f"❌ Vision skill failed\n{result.stderr}")


async def start_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start safety questioning protocol"""
    user_id = update.effective_user.id

    # Execute conversation skill
    import subprocess
    conv_input = {
        "session_id": f"telegram_{user_id}_{int(asyncio.get_event_loop().time())}",
        "trigger_conversation": True
    }

    result = subprocess.run(
        ["python3", str(SKILLS_PATH / "conversation_skill.py")],
        input=json.dumps(conv_input),
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            action = data.get("action")
            question = data.get("question")
            session_id = data.get("session_id")

            if action == "ask":
                # Store session for reply handling
                user_sessions[user_id] = {
                    "session_id": session_id,
                    "step": data.get("step", 1),
                    "awaiting_reply": True
                }

                await update.message.reply_text(
                    f"❓ Safety Protocol Question {data.get('step', 1)}/{data.get('total_steps', 3)}:\n\n"
                    f"{question}\n\n"
                    f"Please reply with your answer."
                )
        except json.JSONDecodeError:
            await update.message.reply_text(f"❌ Conversation error\n{result.stdout}")


async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /chat - enable general LLM conversation mode"""
    user_id = update.effective_user.id
    chat_mode[user_id] = {
        "active": True,
        "history": [
            {"role": "system", "content": "You are Sentinel, a helpful AI assistant. Keep responses concise and friendly."}
        ]
    }

    voice_status = "✓ Voice messages supported" if WHISPER_AVAILABLE else "✗ Voice not available"

    await update.message.reply_text(
        "💬 Chat mode activated!\n\n"
        "You can now chat with me using the local LLM (qwen2.5:3b).\n"
        f"{voice_status}\n\n"
        "Send text or voice messages!\n"
        "Use /voicereply to toggle audio responses.\n"
        "Send /endchat to stop chatting.\n\n"
        "What would you like to talk about?"
    )


async def voicereply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /voicereply - toggle audio responses"""
    user_id = update.effective_user.id

    if not PIPER_AVAILABLE:
        await update.message.reply_text("❌ Piper TTS is not available. Audio responses disabled.")
        return

    if user_id not in voice_mode:
        voice_mode[user_id] = True
        await update.message.reply_text("🔊 Voice replies enabled! I'll send audio responses.")
    else:
        del voice_mode[user_id]
        await update.message.reply_text("🔇 Voice replies disabled. Text only.")


async def endchat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /endchat - disable chat mode"""
    user_id = update.effective_user.id
    if user_id in chat_mode:
        del chat_mode[user_id]
        await update.message.reply_text(
            "👋 Chat mode ended. Use /chat to start again."
        )
    else:
        await update.message.reply_text(
            "ℹ️ Chat mode is not active."
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages - either for safety questions or general chat"""
    user_id = update.effective_user.id
    user_text = update.message.text

    # Check if in chat mode
    if user_id in chat_mode and chat_mode[user_id].get("active"):
        try:
            # Auto-search: if message looks like a search query, prepend results
            search_context = ""
            if SEARCH_AVAILABLE and SEARCH_INTENT_PATTERN.match(user_text):
                await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
                search_context = _ddg_search(user_text, max_results=3)

            # Build user content (with search context injected if available)
            user_content = user_text
            if search_context:
                user_content = (
                    f"{user_text}\n\n"
                    f"[Web search results for context:]\n{search_context}"
                )

            # Add user message to history
            chat_mode[user_id]["history"].append({"role": "user", "content": user_content})

            # Query Ollama
            response = ollama.chat(
                model="qwen2.5:3b",
                messages=chat_mode[user_id]["history"]
            )

            assistant_message = response["message"]["content"]

            # Add assistant response to history
            chat_mode[user_id]["history"].append({"role": "assistant", "content": assistant_message})

            # Keep only last 10 messages to avoid context overflow
            if len(chat_mode[user_id]["history"]) > 11:  # 1 system + 10 conversation
                chat_mode[user_id]["history"] = [chat_mode[user_id]["history"][0]] + chat_mode[user_id]["history"][-10:]

            await update.message.reply_text(assistant_message)

        except Exception as e:
            await update.message.reply_text(f"❌ Error chatting with LLM: {e}")

        return

    # Check if user has active safety question session
    if user_id not in user_sessions:
        await update.message.reply_text(
            "ℹ️ No active conversation. Use /wake to start monitoring or /chat to talk with me."
        )
        return

    session = user_sessions[user_id]

    if not session.get("awaiting_reply"):
        return

    # Send reply to conversation skill
    import subprocess
    conv_input = {
        "session_id": session["session_id"],
        "user_input": user_text,
        "step": session["step"]
    }

    result = subprocess.run(
        ["python3", str(SKILLS_PATH / "conversation_skill.py")],
        input=json.dumps(conv_input),
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            action = data.get("action")

            if action == "ask":
                # More questions
                session["step"] = data.get("step", session["step"] + 1)
                question = data.get("question")

                await update.message.reply_text(
                    f"❓ Question {data.get('step', 1)}/{data.get('total_steps', 3)}:\n\n"
                    f"{question}"
                )

            elif action == "complete":
                # Conversation complete
                await update.message.reply_text(
                    f"✅ Safety check complete!\n\n"
                    f"{data.get('summary', 'All questions answered.')}\n\n"
                    f"Returning to monitoring mode."
                )
                del user_sessions[user_id]

        except json.JSONDecodeError:
            await update.message.reply_text(f"❌ Error processing reply\n{result.stdout}")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status - system health"""
    import subprocess
    import psutil

    # Get system info
    mem = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=1)

    # Check Ollama
    ollama_status = "✅ Running" if os.system("curl -s http://localhost:11434/api/tags > /dev/null 2>&1") == 0 else "❌ Offline"

    # Check captures directory
    today = Path(CAPTURES_PATH / asyncio.get_event_loop().time().strftime("%Y-%m-%d"))
    capture_count = len(list(today.glob("*.jpg"))) if today.exists() else 0

    status_text = (
        f"📊 Sentinel Status\n\n"
        f"Memory: {mem.percent}% ({mem.used / 1e9:.1f}GB / {mem.total / 1e9:.1f}GB)\n"
        f"CPU: {cpu}%\n"
        f"Ollama: {ollama_status}\n"
        f"Captures today: {capture_count}\n"
        f"Database: {MEMORY_DB.name} ({'exists' if MEMORY_DB.exists() else 'not found'})"
    )

    await update.message.reply_text(status_text)


async def memory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /memory - search conversation history"""
    import sqlite3

    if not MEMORY_DB.exists():
        await update.message.reply_text("❌ Memory database not found")
        return

    conn = sqlite3.connect(MEMORY_DB)
    rows = conn.execute(
        "SELECT session_id, timestamp, role, content FROM conversations ORDER BY timestamp DESC LIMIT 10"
    ).fetchall()

    if not rows:
        await update.message.reply_text("ℹ️ No conversations recorded yet")
        return

    text = "🧠 Recent Conversations:\n\n"
    for row in rows:
        text += f"**{row[0]}** ({row[1]})\n{row[2]}: {row[3][:50]}...\n\n"

    await update.message.reply_text(text[:4000])  # Telegram limit


async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice messages from users"""
    user_id = update.effective_user.id

    if not WHISPER_AVAILABLE:
        await update.message.reply_text("❌ Whisper is not available. Voice messages not supported.")
        return

    # Check if in chat mode
    if user_id not in chat_mode or not chat_mode[user_id].get("active"):
        await update.message.reply_text(
            "ℹ️ Please start chat mode first with /chat to use voice messages."
        )
        return

    try:
        await update.message.reply_text("🎤 Processing your voice message...")

        # Download voice file
        voice_file = await update.message.voice.get_file()
        voice_path = f"/tmp/voice_{user_id}_{update.message.message_id}.ogg"
        await voice_file.download_to_drive(voice_path)

        # Transcribe with Whisper
        model = get_whisper_model()
        if model is None:
            await update.message.reply_text("❌ Failed to load Whisper model")
            return

        result = model.transcribe(voice_path, language="en", fp16=False)
        transcribed_text = result["text"].strip()

        # Clean up voice file
        os.remove(voice_path)

        if not transcribed_text:
            await update.message.reply_text("❌ Could not transcribe audio. Please try again.")
            return

        # Show transcription
        await update.message.reply_text(f"📝 You said: \"{transcribed_text}\"")

        # Process with LLM
        chat_mode[user_id]["history"].append({"role": "user", "content": transcribed_text})

        response = ollama.chat(
            model="qwen2.5:3b",
            messages=chat_mode[user_id]["history"]
        )

        assistant_message = response["message"]["content"]
        chat_mode[user_id]["history"].append({"role": "assistant", "content": assistant_message})

        # Keep only last 10 messages
        if len(chat_mode[user_id]["history"]) > 11:
            chat_mode[user_id]["history"] = [chat_mode[user_id]["history"][0]] + chat_mode[user_id]["history"][-10:]

        # Send text response
        await update.message.reply_text(assistant_message)

        # Send voice response if enabled
        if user_id in voice_mode and voice_mode[user_id]:
            tts = get_piper_tts()
            if tts:
                try:
                    sample_rate, audio = tts.synthesize(assistant_message)

                    # Save to file
                    audio_path = f"/tmp/response_{user_id}_{update.message.message_id}.wav"
                    sf.write(audio_path, audio, sample_rate)

                    # Send audio
                    with open(audio_path, 'rb') as audio_file:
                        await update.message.reply_voice(voice=audio_file)

                    # Clean up
                    os.remove(audio_path)

                except Exception as e:
                    logger.error(f"TTS error: {e}")

    except Exception as e:
        logger.error(f"Voice message error: {e}")
        await update.message.reply_text(f"❌ Error processing voice message: {e}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help"""
    await start(update, context)


# --- Search helpers ---

SEARCH_INTENT_PATTERN = re.compile(
    r"^(search( for)?|look up|find( out)?|google|what is|who is|when (is|was|did)|where is|how (do|does|can|to))\b",
    re.IGNORECASE,
)


def _ddg_search(query: str, max_results: int = 4) -> str:
    """Run DuckDuckGo search and return a compact formatted string."""
    if not SEARCH_AVAILABLE:
        return ""
    try:
        results = list(DDGS().text(query, max_results=max_results))
    except Exception:
        return ""
    if not results:
        return ""
    lines = []
    for i, r in enumerate(results, 1):
        title = r.get("title", "")
        body = r.get("body", "")[:200]
        url = r.get("href", "")
        lines.append(f"[{i}] {title}\n    {body}\n    {url}")
    return "\n\n".join(lines)


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/search <query> — DuckDuckGo + LLM summary"""
    if not SEARCH_AVAILABLE:
        await update.message.reply_text("❌ Search not available (ddgs not installed)")
        return

    query = " ".join(context.args) if context.args else ""
    if not query:
        await update.message.reply_text("Usage: /search <your query>")
        return

    await update.message.reply_text(f"🔍 Searching: {query}...")

    search_results = _ddg_search(query)
    if not search_results:
        await update.message.reply_text("❌ No results found.")
        return

    # Ask the LLM to summarise
    prompt = (
        f"Answer this question based on the web search results below. "
        f"Be concise (3-5 sentences max).\n\n"
        f"Question: {query}\n\n"
        f"Search results:\n{search_results}"
    )
    try:
        response = ollama.chat(
            model="qwen2.5:3b",
            messages=[
                {"role": "system", "content": "You are Sentinel, a helpful assistant. Summarise search results concisely."},
                {"role": "user", "content": prompt},
            ],
        )
        summary = response["message"]["content"]
    except Exception as e:
        # Fall back to raw results if LLM is unavailable
        summary = f"(LLM unavailable: {e})\n\n{search_results}"

    await update.message.reply_text(f"🔍 *{query}*\n\n{summary}", parse_mode="Markdown")


def main():
    """Start Telegram bot"""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
        sys.exit(1)

    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("wake", wake_command))
    application.add_handler(CommandHandler("chat", chat_command))
    application.add_handler(CommandHandler("voicereply", voicereply_command))
    application.add_handler(CommandHandler("endchat", endchat_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("memory", memory_command))
    application.add_handler(CommandHandler("search", search_command))

    # Voice message handler
    application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))

    # Message handler for conversation replies and chat
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start bot
    logger.info("🛡️ Sentinel Telegram Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
