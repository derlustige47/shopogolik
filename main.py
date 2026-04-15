import os
from fastapi import FastAPI, Request
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import uvicorn
import asyncio

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Railway сам даст

app = FastAPI()

# Меню
keyboard = [
    [KeyboardButton("Одежда")],
    [KeyboardButton("Для взрослых +18")],
    [KeyboardButton("Новинки")],
    [KeyboardButton("Из Китая")],
    [KeyboardButton("Wildberries")],
    [KeyboardButton("Ozon")]
]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Выбери категорию:", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    await update.message.reply_text(f"🔍 Ищу по запросу: {text}...")

    # Здесь будет логика поиска (пока заглушка)
    await update.message.reply_text("Пока поиск работает только по Avito.\nСкоро добавлю все площадки.")

# Создаём приложение Telegram
tg_app = Application.builder().token(TOKEN).build()
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(MessageHandler(filters.TEXT & filters.COMMAND, handle_message))

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, tg_app.bot)
    await tg_app.process_update(update)
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"status": "bot is running with webhook"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
