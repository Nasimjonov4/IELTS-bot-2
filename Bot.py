import os
import google.generativeai as genai
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

TELEGRAM_TOKEN = os.environ.get("8088033129:AAG4QC_n7pukQSwVvW31F9tJQzQVDYKGoYs")
GEMINI_API_KEY = os.environ.get("AIzaSyBBQgmhREcAo-8YtSnllbKgavIJ4JxY_RQ")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

WAITING_TOPIC = 1

MAIN_MENU = ReplyKeyboardMarkup(
    [
        [KeyboardButton("📖 Reading Tasks")],
        [KeyboardButton("✍️ Writing Tasks")],
        [KeyboardButton("🎙️ Speaking Vocab & Ideas")],
        [KeyboardButton("💡 Writing Vocab & Ideas")],
        [KeyboardButton("🌐 Others")],
    ],
    resize_keyboard=True,
    persistent=True
)

def ask_ai(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Xatolik yuz berdi: {str(e)}\nQayta urinib ko'ring."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salom! Men IELTS Master Bot!\n\nIELTS tayyorgarligingizda yordam beraman.\nQuyidagi bo'limlardan birini tanlang:",
        reply_markup=MAIN_MENU
    )

async def reading_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Reading task tayyorlanmoqda...")
    prompt = """Generate a complete IELTS Academic Reading task:
    1. A passage (250-300 words) on an interesting academic topic
    2. 5 questions: mix of True/False/Not Given, Multiple Choice, Short Answer
    3. Answer key at the end
    Format it clearly with sections. Make it realistic IELTS style."""
    reply = ask_ai(prompt)
    await update.message.reply_text(reply, reply_markup=MAIN_MENU)

async def writing_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Writing task tayyorlanmoqda...")
    prompt = """Generate 2 IELTS Writing tasks:
    TASK 1: Describe a chart/graph with prompt.
    TASK 2: Argumentative essay topic.
    For each: vocabulary suggestions, structure tips, sample opening."""
    reply = ask_ai(prompt)
    await update.message.reply_text(reply, reply_markup=MAIN_MENU)

async def speaking_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "speaking"
    await update.message.reply_text(
        "🎙️ Speaking mavzuingizni kiriting:\n(Masalan: Describe a place you like to visit)"
    )
    return WAITING_TOPIC

async def writing_vocab_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "writing_vocab"
    await update.message.reply_text(
        "💡 Writing mavzuingizni kiriting:\n(Masalan: Environmental pollution)"
    )
    return WAITING_TOPIC

async def others_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "others"
    await update.message.reply_text(
        "🌐 IELTS haqida istalgan savolingizni yozing!"
    )
    return WAITING_TOPIC

async def topic_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = update.message.text
    mode = context.user_data.get("mode")
    await update.message.reply_text("⏳ Tayyorlanmoqda...")

    if mode == "speaking":
        prompt = f"""For the IELTS Speaking topic: "{topic}"
        1. KEY VOCABULARY (10-12 words with Uzbek translations)
        2. MAIN IDEAS & TALKING POINTS (5-6 bullet points)
        3. USEFUL PHRASES to use in speaking
        4. SAMPLE ANSWER OPENING (2-3 sentences)
        5. COMMON MISTAKES to avoid
        Target Band 7+"""
    elif mode == "writing_vocab":
        prompt = f"""For the IELTS Writing topic: "{topic}"
        1. KEY VOCABULARY (12-15 words with meaning)
        2. MAIN ARGUMENTS & IDEAS
        3. USEFUL LINKING WORDS
        4. ACADEMIC PHRASES
        5. SAMPLE THESIS STATEMENT
        6. WORDS TO AVOID
        Target Band 7+"""
    else:
        prompt = f"""You are an expert IELTS tutor. Answer: "{topic}"
        Give practical advice, examples and tips."""

    reply = ask_ai(prompt)
    await update.message.reply_text(reply, reply_markup=MAIN_MENU)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Bekor qilindi.", reply_markup=MAIN_MENU)
    return ConversationHandler.END

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("🎙️ Speaking"), speaking_start),
            MessageHandler(filters.Regex("💡 Writing Vocab"), writing_vocab_start),
            MessageHandler(filters.Regex("🌐 Others"), others_handler),
        ],
        states={
            WAITING_TOPIC: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, topic_received)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("📖 Reading"), reading_handler))
    app.add_handler(MessageHandler(filters.Regex("✍️ Writing Tasks"), writing_handler))
    app.add_handler(conv_handler)

    print("✅ Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
