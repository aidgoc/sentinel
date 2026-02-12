#!/usr/bin/env python3
"""
Sentinel Telegram Bot - Week 2 Integration
Handles Telegram commands and webhook for conversation replies
"""

import os
import sys
import json
import logging
import asyncio
from pathlib import Path

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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    await update.message.reply_text(
        f"🛡️ Sentinel Active\n\n"
        f"Hello {user.first_name}!\n\n"
        f"Available commands:\n"
        f"/wake - Trigger immediate capture\n"
        f"/status - System health\n"
        f"/memory - Search conversations\n"
        f"/stats - Performance metrics\n"
        f"/help - Show this message"
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


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user replies to safety questions"""
    user_id = update.effective_user.id
    user_text = update.message.text

    # Check if user has active session
    if user_id not in user_sessions:
        await update.message.reply_text(
            "ℹ️ No active conversation. Use /wake to start monitoring."
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


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help"""
    await start(update, context)


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
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("memory", memory_command))

    # Message handler for conversation replies
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start bot
    logger.info("🛡️ Sentinel Telegram Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
