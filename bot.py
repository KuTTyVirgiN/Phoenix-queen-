import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Game storage
current_host = None
current_word = None
current_definition = None
scores = {}

# Sample word list
words = [
    ("Python", "A high-level programming language."),
    ("Telegram", "A cloud-based instant messaging app."),
    ("Algorithm", "A step-by-step procedure for solving problems."),
    ("Database", "An organized collection of structured information."),
    ("Internet", "A global network that connects millions of computers."),
]

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to the Word Quiz Bot! Use /host to become the host.")

# Host command
async def host(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_host, current_word, current_definition
    user = update.effective_user

    if current_host is not None:
        await update.message.reply_text(f"❌ {current_host.first_name} is already the host.")
        return

    current_host = user
    current_word, current_definition = random.choice(words)

    keyboard = [
        [InlineKeyboardButton("📖 Word", callback_data="show_word")],
        [InlineKeyboardButton("➡️ Next Word", callback_data="next_word")],
        [InlineKeyboardButton("📚 Definition", callback_data="show_definition")],
        [InlineKeyboardButton("🚪 Leave Host", callback_data="leave_host")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🎉 {user.first_name} is now the Host!\nOnly host can see the word and definition.",
        reply_markup=reply_markup,
    )

# Handle host buttons
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_host, current_word, current_definition
    query = update.callback_query
    user = query.from_user
    await query.answer()

    if current_host is None or user.id != current_host.id:
        await query.edit_message_text("❌ You are not the current host.")
        return

    if query.data == "show_word":
        await query.message.reply_text(f"🔤 Word: {current_word}")
    elif query.data == "show_definition":
        await query.message.reply_text(f"📚 Definition: {current_definition}")
    elif query.data == "next_word":
        current_word, current_definition = random.choice(words)
        await query.message.reply_text("🔄 New word selected!")
    elif query.data == "leave_host":
        await query.message.reply_text(f"🚪 {current_host.first_name} has left hosting.")
        current_host = None
        current_word = None
        current_definition = None
        # Hosting button for others
        await query.message.reply_text("👉 Use /host to become the new Host!")

# Handle answers
async def answer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_word, scores
    if current_word is None:
        return

    user = update.effective_user
    text = update.message.text.strip().lower()
    correct_answer = current_word.lower()

    if text == correct_answer:
        scores[user.id] = scores.get(user.id, 0) + 1
        await update.message.reply_text(
            f"✅ Correct! {user.first_name} gets 1 point. 🎉"
        )
        # Move to next word automatically
        new_word, new_def = random.choice(words)
        current_word, current_definition = new_word, new_def
    else:
        pass  # ❌ No wrong answer message (silent ignore)

# Scoreboard
async def scoreboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not scores:
        await update.message.reply_text("📊 No scores yet.")
        return

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:20]
    text = "🏆 Top 20 Players 🏆\n\n"

    for i, (user_id, score) in enumerate(sorted_scores, start=1):
        user = await context.bot.get_chat(user_id)
        medal = ""
        if i == 1:
            medal = "🥇"
        elif i == 2:
            medal = "🥈"
        elif i == 3:
            medal = "🥉"
        elif i <= 10:
            medal = "🏅"
        else:
            medal = "🎖️"
        text += f"{i}. {user.first_name} — {score} {medal}\n"

    await update.message.reply_text(text)

# Main function
def main():
    application = Application.builder().token("YOUR_TELEGRAM_BOT_TOKEN").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("host", host))
    application.add_handler(CommandHandler("scoreboard", scoreboard))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer_handler))

    application.run_polling()

if __name__ == "__main__":
    main()
