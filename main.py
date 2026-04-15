import os
from telegram import Update
from telegram.ext import Application, CommandHandler

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

async def start(update: Update, context):
    await update.message.reply_text("Шопоголик запущен и готов мониторить объявления ")

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Бот запущен...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
