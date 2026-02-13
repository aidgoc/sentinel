#!/bin/bash
# Sentinel Telegram Bot Startup Script

cd /home/harshwardhan/sentinel

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Activate virtual environment
source .venv/bin/activate

# Force CPU usage to avoid CUDA issues with MX130
export CUDA_VISIBLE_DEVICES=""

# Start the bot
echo "🛡️ Starting Sentinel Telegram Bot..."
python3 skills/telegram_bot.py
