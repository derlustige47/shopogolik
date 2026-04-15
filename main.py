import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Шопоголик запущен и работает.\nПиши, что хочешь найти.")

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    print("Бот запущен и ждёт команды...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
