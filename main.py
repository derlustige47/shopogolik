import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
import requests
from bs4 import BeautifulSoup

TOKEN = os.getenv("TELEGRAM_TOKEN")

# Меню с кнопками
keyboard = [
    [KeyboardButton("Одежда")],
    [KeyboardButton("Для взрослых +18")],
    [KeyboardButton("Новинки")],
    [KeyboardButton("Из Китая")]
]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context):
    await update.message.reply_text(
        "Выбери категорию или напиши свой запрос:",
        reply_markup=reply_markup
    )

async def search(update: Update, context):
    query = update.message.text.strip()
    await update.message.reply_text(f"🔍 Ищу по запросу: {query}...")

    url = f"https://www.avito.ru/all?q={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all("div", {"data-marker": "item"})[:5]

        if items:
            for item in items:
                title = item.find("h3")
                price = item.find("span", class_="price-text")
                link = item.find("a")
                title_text = title.get_text(strip=True) if title else "Без названия"
                price_text = price.get_text(strip=True) if price else ""
                link_text = "https://www.avito.ru" + link.get("href") if link else ""
                await update.message.reply_text(f"{title_text}\n{price_text}\n{link_text}")
        else:
            await update.message.reply_text("Ничего не найдено.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & filters.COMMAND, search))

print("Шопоголик запущен с меню")

if __name__ == "__main__":
    app.run_polling()
