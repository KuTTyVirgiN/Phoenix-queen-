import os
import random
import html
import logging
import requests
from googletrans import Translator
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
translator = Translator()

# In-memory storage
user_scores = {}
current_question = {}
current_answer = {}
user_language = {}  # en or ta
used_questions = {}  # {user_id: [question_hashes]}

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Quiz Bot!\n"
        "Use /quiz to get a question.\n"
        "Use /skip to skip and see correct answer.\n"
        "Use /score to check your points.\n"
        "Use /language en or /language ta to change language."
    )

# /language command
async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if len(context.args) == 0:
        await update.message.reply_text("Usage: /language en OR /language ta")
        return
    lang = context.args[0].lower()
    if lang in ["en", "ta"]:
        user_language[user_id] = lang
        await update.message.reply_text(f"Language set to {lang}")
    else:
        await update.message.reply_text("Only 'en' or 'ta' allowed")

# Function to fetch question from Open Trivia API
def get_question_for_user(user_id):
    lang = user_language.get(user_id, "en")

    # Track used question hashes to avoid repeat
    if user_id not in used_questions:
        used_questions[user_id] = []

    # Try to fetch until a non-repeating question is found
    while True:
        try:
            response = requests.get("https://opentdb.com/api.php?amount=1&type=multiple")
            data = response.json()["results"][0]
            question_text = html.unescape(data["question"])
            correct_answer = html.unescape(data["correct_answer"])
            q_hash = hash(question_text)
        except Exception as e:
            logging.error(f"API Error: {e}")
            question_text = "What is 2 + 2?"
            correct_answer = "4"
            q_hash = hash(question_text)

        if q_hash not in used_questions[user_id]:
            used_questions[user_id].append(q_hash)
            break

    # Translate to Tamil if needed
    if lang == "ta":
        try:
            question_text = translator.translate(question_text, src='en', dest='ta').text
            correct_answer = translator.translate(correct_answer, src='en', dest='ta').text
        except Exception as e:
            logging.error(f"Translation error: {e}")

    current_question[user_id] = question_text
    current_answer[user_id] = correct_answer
    return question_text, correct_answer

# /quiz command
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    q, _ = get_question_for_user(user_id)
    await update.message.reply_text(f"❓ {q}")

# /skip command
async def skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in current_answer:
        await update.message.reply_text(f"⏭ Skipped! Correct answer: {current_answer[user_id]}")
        q, _ = get_question_for_user(user_id)
        await update.message.reply_text(f"➡️ Next Question: {q}")
    else:
        await update.message.reply_text("No active question. Use /quiz to start.")

# Handle answers
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in current_answer:
        return
    text = update.message.text.strip()
    if text.lower() == current_answer[user_id].lower():
        user_scores[user_id] = user_scores.get(user_id, 0) + 1
        await update.message.reply_text(f"✅ Correct! Your score: {user_scores[user_id]}")
        q, _ = get_question_for_user(user_id)
        await update.message.reply_text(f"➡️ Next Question: {q}")
    # Wrong answer ignored

# /score command
async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    pts = user_scores.get(user_id, 0)
    await update.message.reply_text(f"🏆 Your Score: {pts}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("language", language))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("skip", skip))
    app.add_handler(CommandHandler("score", score))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))

    app.run_polling()

if __name__ == "__main__":
    main()
