import os
from telegram.ext import Application, CommandHandler
import asyncio

TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update, context):
    await update.message.reply_text("✅ Шопоголик запущен и работает\nНапиши, что хочешь найти")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

print("Бот запущен и готов к работе...")

if __name__ == '__main__':
    asyncio.run(app.run_polling())
