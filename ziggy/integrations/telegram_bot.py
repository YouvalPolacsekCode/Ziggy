import os
import time
import pytz

# ✅ Set environment timezone
os.environ["TZ"] = "Asia/Jerusalem"
time.tzset()

# ✅ Monkey-patch apscheduler to force pytz
import apscheduler.util
apscheduler.util.astimezone = lambda tz=None: tz or pytz.timezone("Asia/Jerusalem")

# ✅ Now import telegram
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)
from core.intent_parser import handle_command, load_settings
from voice.voice_interface import VoiceAssistant

va = VoiceAssistant(language="auto")
AUTHORIZED_USER_IDS = []

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message_text = update.message.text.strip()
    if AUTHORIZED_USER_IDS and user_id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("⛔ Unauthorized user.")
        return
    print(f"📩 Received from Telegram: {message_text}")
    response = handle_command(message_text)
    print(f"🤖 Ziggy replies: {response}")
    if response:
        await update.message.reply_text(response)
        va.say(response)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Ziggy is ready!")
    va.say("זיגי מוכן")

def run_bot():
    settings = load_settings()
    token = settings["telegram"]["bot_token"]
    if not token:
        raise ValueError("Telegram bot token not set in settings.yaml")

    # ✅ DO NOT manually set scheduler – just let the monkey patch take care of it
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Telegram bot is running…")
    app.run_polling()
