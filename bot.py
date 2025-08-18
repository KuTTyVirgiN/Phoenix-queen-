from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os, random

# Simple Tamil Q&A for the Octopus guessing game
QUESTIONS = {
    "🐙 இந்தியாவின் தலைநகர்?": "delhi",
    "🐙 உலகில் மிகப்பெரிய கடல் உயிரினம்?": "blue whale",
    "🐙 8 கைகள் உடைய உயிரினம் யார்?": "octopus"
}

SCORES = {}

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🐙 Welcome to Octopus Bot!\nType /play to start game.")

# /play
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q, a = random.choice(list(QUESTIONS.items()))
    context.user_data["answer"] = a
    await update.message.reply_text(q)

# Guess
async def guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "answer" not in context.user_data:
        return
    answer = context.user_data["answer"].lower()
    if update.message.text and update.message.text.lower() == answer:
        user = update.message.from_user.first_name or "Player"
        SCORES[user] = SCORES.get(user, 0) + 1
        await update.message.reply_text(f"🎉 சரியான பதில் {user}! (+1 point)\nScoreboard: {SCORES}")
        context.user_data.clear()

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is not set.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, guess))
    app.run_polling()

if __name__ == "__main__":
    main()
