import os
import requests
import asyncio
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# ---------- GENERATE RESPONSE VIA LLM ----------
def generate_llm_response(prompt: str) -> str:
    API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
    headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
    try:
        r = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": prompt, "parameters": {"max_new_tokens": 150}},
            timeout=60
        )
        resp = r.json()
        if isinstance(resp, list) and "generated_text" in resp[0]:
            return resp[0]["generated_text"]
        elif isinstance(resp, dict) and "generated_text" in resp:
            return resp["generated_text"]
        else:
            return "Извини, не удалось сгенерировать ответ."
    except Exception as e:
        print("Ошибка генерации:", e)
        return "Извини, произошла ошибка при генерации ответа."

# ---------- TELEGRAM COMMANDS ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я твой персональный тренер. 🏋️‍♂️\n\n"
        "Команды:\n"
        "/exercise — получить новое упражнение\n"
        "/nutrition <вопрос> — задать вопрос о питании"
    )

async def exercise(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = (
        "Ты персональный тренер. Сгенерируй одно упражнение для домашней тренировки "
        "с названием и короткой инструкцией, максимум 200 символов."
    )
    response = generate_llm_response(prompt)
    await update.message.reply_text(response)

async def nutrition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = " ".join(context.args) if context.args else "Дай совет по питанию."
    prompt = f"Ты эксперт по питанию. Ответь на вопрос: {question}"
    response = generate_llm_response(prompt)
    await update.message.reply_text(response)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = f"Ты персональный тренер и эксперт по питанию. Ответь на вопрос: {update.message.text}"
    response = generate_llm_response(prompt)
    await update.message.reply_text(response)

# ---------- SEND DAILY EXERCISE ----------
async def send_daily_exercise():
    TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
    TG_CHAT_ID = os.getenv("TG_CHAT_ID")
    bot = Bot(TG_BOT_TOKEN)
    prompt = (
        "Ты персональный тренер. Сгенерируй одно упражнение для домашней тренировки "
        "с названием и короткой инструкцией, максимум 200 символов."
    )
    response = generate_llm_response(prompt)
    await bot.send_message(chat_id=TG_CHAT_ID, text=response)
    print("Ежедневное упражнение отправлено!")

# ---------- MAIN ----------
def main():
    TOKEN = os.getenv("TG_BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("exercise", exercise))
    app.add_handler(CommandHandler("nutrition", nutrition))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск Telegram polling для интерактивного общения
    print("Бот запущен для интерактивного общения!")
    app.run_polling()

if __name__ == "__main__":
    # Если запускается через GitHub Actions для рассылки, можно вызвать send_daily_exercise()
    if os.getenv("GITHUB_ACTIONS"):
        asyncio.run(send_daily_exercise())
    else:
        main()
