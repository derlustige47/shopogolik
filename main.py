import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update
import asyncio
import requests
from bs4 import BeautifulSoup

TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context):
    await update.message.reply_text("Отправь мне, что искать.\nНапример:\nRTX 3060\niPhone 13 Москва")

async def search(update: Update, context):
    query = update.message.text.strip()
    await update.message.reply_text(f"🔍 Ищу по запросу: {query}...")

    url = f"https://www.avito.ru/all?q={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "lxml")
        items = soup.find_all("div", {"data-marker": "item"})[:5]

        if items:
            for item in items:
                title_tag = item.find("h3")
                price_tag = item.find("span", class_="price-text")
                link_tag = item.find("a")

                title = title_tag.get_text(strip=True) if title_tag else "Без названия"
                price = price_tag.get_text(strip=True) if price_tag else ""
                link = "https://www.avito.ru" + link_tag.get("href") if link_tag else ""

                text = f"{title}\n{price}\n{link}"
                await update.message.reply_text(text)
        else:
            await update.message.reply_text("Ничего не найдено на Авито.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    text_filter = filters.TEXT & \~filters.COMMAND
    app.add_handler(MessageHandler(text_filter, search))
    
    print("Шопоголик запущен...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
