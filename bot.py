import logging
import random
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "7888283815:AAFjBI7LU9Nu5sqakPSPL76W-2o2L7krIpg"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Function to get random question from Open Trivia DB
def get_online_question():
    url = "https://opentdb.com/api.php?amount=1&type=multiple"
    response = requests.get(url).json()
    if response["response_code"] == 0:
        q = response["results"][0]
        question = q["question"]
        correct = q["correct_answer"]
        options = q["incorrect_answers"] + [correct]
        random.shuffle(options)
        return question, options, correct
    return "No question found", [], None

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎮 Welcome! Use /question to get a random quiz question.")

# /question command
async def question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q, options, correct = get_online_question()
    text = f"🤔 Question:\n{q}\n\n"
    for i, opt in enumerate(options, 1):
        text += f"{i}. {opt}\n"
    text += "\n👉 Answer will be revealed after 10 seconds!"
    await update.message.reply_text(text)

    # Reveal answer after 10s
    await context.job_queue.run_once(
        lambda ctx: ctx.bot.send_message(update.effective_chat.id, f"✅ Correct Answer: {correct}"),
        when=10
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("question", question))
    app.run_webhook(
        listen="0.0.0.0",
        port=8080,
        url_path=TOKEN,
        webhook_url=f"https://YOUR_RENDER_URL/{TOKEN}"
    )

if __name__ == "__main__":
    main()
