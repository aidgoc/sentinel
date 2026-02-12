# 🚀 SENTINEL - QUICK START (Super Easy!)

## Just type `ltl` - That's it!

Your Telegram bot token is already configured. Just run:

```bash
ltl
```

That's literally all you need! 🎉

---

## What `ltl` does:

### Start Telegram Bot (Default)
```bash
ltl
# or
ltl bot
# or
ltl telegram
```

This starts the Telegram bot. Then open Telegram and:
1. Search for your bot (use the username @BotFather gave you)
2. Send `/start`
3. Send `/wake` to trigger a capture!

---

## Other Super Easy Commands

### Take a Photo Right Now
```bash
ltl vision
```
Captures image, runs YOLO detection, shows results.

### Check if Everything Works
```bash
ltl status
```
Shows health of all components.

### Run Tests
```bash
ltl test
```
Validates vision, Ollama, and packages.

### See Recent Captures
```bash
ltl logs
```
Lists today's captured images.

### Start a Conversation
```bash
ltl chat
```
Triggers the 3-question safety protocol.

### Get Help
```bash
ltl help
```
Shows all commands.

---

## 📱 Using Telegram

After running `ltl`, your bot is live. Open Telegram:

**Available Commands:**
- `/start` - Initialize bot and see welcome message
- `/wake` - Take photo immediately, get results + image
- `/status` - Check Sentinel system health
- `/memory` - View conversation history
- `/help` - Show commands

**Interactive Flow:**
1. Send `/wake`
2. Bot captures photo
3. If person detected → asks 3 safety questions
4. Answer each question
5. Bot stores conversation in database

---

## 🎯 Quickest Test

Open **2 terminals**:

**Terminal 1:**
```bash
ltl
```
(Starts bot, leave it running)

**Terminal 2:**
Open Telegram app, send `/wake` to your bot.

Watch Terminal 1 - you'll see the bot processing your command!

---

## 🔧 Troubleshooting

### "ltl: command not found"
```bash
# Reload your shell
source ~/.bashrc

# Or use full path
~/sentinel/ltl
```

### "Ollama offline"
```bash
# Start Ollama
ollama serve &

# Then try ltl again
ltl status
```

### "Camera not found"
Check if `/dev/video0` exists:
```bash
ls -l /dev/video0
```

If not, plug in a webcam or use a virtual camera.

---

## 📊 What's Happening Behind the Scenes

When you type `ltl`:

1. ✅ Loads your Telegram token from `~/.sentinel_env`
2. ✅ Activates Python virtual environment
3. ✅ Sets CPU mode (MX130 compatibility)
4. ✅ Starts `skills/telegram_bot.py`
5. ✅ Connects to Telegram API
6. ✅ Waits for your commands

It's **completely automated** - no manual setup needed!

---

## 🎁 Pro Tips

### Run in Background
```bash
ltl &
```
Runs bot in background. To stop:
```bash
pkill -f telegram_bot.py
```

### Auto-start on Boot
```bash
# Add to ~/.bashrc
echo "ltl &" >> ~/.bashrc
```

### Check Bot Logs
```bash
# If running in background
ps aux | grep telegram_bot
```

---

## 🆘 Need Help?

```bash
# Full documentation
cat ~/sentinel/README.md

# Deployment guide
cat ~/sentinel/DEPLOYMENT.md

# System status
cat ~/sentinel/FINAL_STATUS.md

# Or just ask ltl
ltl help
```

---

## ✨ That's It!

**Literally just type:**
```bash
ltl
```

**Then use Telegram to control your ambient intelligence agent! 🛡️**

No configuration.
No manual setup.
No hassle.

Just `ltl` and you're running! 🚀
