import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update
import asyncio
import requests
from bs4 import BeautifulSoup

TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context):
    await update.message.reply_text("Отправь мне, что искать. Например:\nRTX 3060\niPhone 13 Москва\nMacBook Pro")

async def search(update: Update, context):
    query = update.message.text
    await update.message.reply_text(f"Ищу по запросу: {query}...")
    
    url = f"https://www.avito.ru/all?q={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'lxml')
        items = soup.find_all('div', {'data-marker': 'item'})[:5]
        
        if items:
            for item in items:
                title = item.find('h3')
                price = item.find('span', {'class': 'price-text'})
                link = item.find('a')
                if title and link:
                    text = f"{title.get_text()}\n{price.get_text() if price else ''}\nhttps://www.avito.ru{link.get('href')}"
                    await update.message.reply_text(text)
        else:
            await update.message.reply_text("Ничего не найдено.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & \~filters.COMMAND, search))
    
    print("Бот запущен...")
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
