from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from deep_translator import GoogleTranslator
import random

# Store questions
questions = [
    {"word": "Python", "definition": "A popular programming language"},
    {"word": "Algorithm", "definition": "A step by step procedure to solve a problem"},
    {"word": "Database", "definition": "An organized collection of data"}
]

# Store game state
game_state = {
    "host": None,
    "current_question": None,
    "scores": {}
}

# Translate helper
def translate_text(text: str, lang: str = "ta") -> str:
    try:
        return GoogleTranslator(source="en", target=lang).translate(text)
    except Exception:
        return text

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Use /host to become the quiz host.")

# Host command
async def host(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if game_state["host"] and game_state["host"] != user_id:
        await update.message.reply_text("Another host is already active.")
        return
    
    game_state["host"] = user_id
    await update.message.reply_text("You are now the host! Use the buttons below.")

    keyboard = [
        [InlineKeyboardButton("📖 Word", callback_data="word"),
         InlineKeyboardButton("➡️ Next Word", callback_data="next_word")],
        [InlineKeyboardButton("📘 Definition", callback_data="definition")],
        [InlineKeyboardButton("🚪 Leave Host", callback_data="leave_host")]
    ]
    await update.message.reply_text("Choose an option:", reply_markup=InlineKeyboardMarkup(keyboard))

# Button handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if game_state["host"] != user_id:
        await query.edit_message_text("Only the host can use these buttons.")
        return

    if query.data == "word":
        game_state["current_question"] = random.choice(questions)
        word = game_state["current_question"]["word"]
        await query.edit_message_text(f"🔑 Word: {word}")

    elif query.data == "next_word":
        game_state["current_question"] = random.choice(questions)
        word = game_state["current_question"]["word"]
        await query.edit_message_text(f"➡️ Next Word: {word}")

    elif query.data == "definition":
        if not game_state["current_question"]:
            await query.edit_message_text("❌ No active word.")
            return
        definition = game_state["current_question"]["definition"]
        translated_def = translate_text(definition, "ta")
        await query.edit_message_text(f"📘 Definition (EN): {definition}\n📘 விளக்கம் (TA): {translated_def}")

    elif query.data == "leave_host":
        game_state["host"] = None
        game_state["current_question"] = None
        await query.edit_message_text("🚪 You have left the host role.\nAnyone can now /host.")

# Main function
def main():
    app = Application.builder().token("YOUR_TELEGRAM_BOT_TOKEN").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("host", host))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
