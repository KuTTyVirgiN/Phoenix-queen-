import os, random, logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

QUESTIONS = {
    "🐊 இந்தியாவின் தலைநகர்?": "delhi",
    "🐊 உலகின் மிகப்பெரிய கடல் உயிரினம்?": "blue whale",
    "🐊 8 கைகள் உடைய உயிரினம் யார்?": "octopus"
}
SCORES = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🐊 Welcome to Crocodile Bot!\nType /play to start game.")

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q, a = random.choice(list(QUESTIONS.items()))
    context.user_data["answer"] = a
    await update.message.reply_text(q)

async def guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "answer" not in context.user_data:
        return
    if update.message.text and update.message.text.lower() == context.user_data["answer"]:
        user = update.message.from_user.first_name or "Player"
        SCORES[user] = SCORES.get(user, 0) + 1
        await update.message.reply_text(f"🎉 சரியான பதில் {user}! (+1)\nScoreboard: {SCORES}")
        context.user_data.clear()

def main():
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN not set")

    PORT = int(os.environ.get("PORT", "10000"))
    HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    if not HOSTNAME:
        raise RuntimeError("RENDER_EXTERNAL_HOSTNAME not set by Render")

    WEBHOOK_PATH = f"/{TOKEN}"
    WEBHOOK_URL = f"https://{HOSTNAME}{WEBHOOK_PATH}"

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, guess))

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=WEBHOOK_PATH,
        webhook_url=WEBHOOK_URL,
        drop_pending_updates=True,
    )

if __name__ == "__main__":
    main()
