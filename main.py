import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from bs4 import BeautifulSoup

# Логирование, чтобы видеть что происходит
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_TOKEN")

# Меню
keyboard = [
    [KeyboardButton("Одежда")],
    [KeyboardButton("Для взрослых +18")],
    [KeyboardButton("Новинки")],
    [KeyboardButton("Из Китая")]
]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Выбери категорию:", reply_markup=reply_markup)

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    await update.message.reply_text(f"🔍 Ищу по запросу: {query}...")

    # Поиск на Avito
    url = f"https://www.avito.ru/all?q={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        items = soup.find_all("div", {"data-marker": "item"})[:6]

        if items:
            for item in items:
                title_tag = item.find("h3", {"data-marker": "item-title"})
                price_tag = item.find("span", {"data-marker": "item-price"})
                link_tag = item.find("a", {"data-marker": "item-title"})

                title = title_tag.get_text(strip=True) if title_tag else "Без названия"
                price = price_tag.get_text(strip=True) if price_tag else ""
                link = "https://www.avito.ru" + link_tag.get("href") if link_tag else ""

                text = f"📦 {title}\n💰 {price}\n🔗 {link}"
                await update.message.reply_text(text)
        else:
            await update.message.reply_text("😕 Ничего не найдено по этому запросу.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при поиске: {str(e)[:200]}")

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & filters.COMMAND, search))

if __name__ == "__main__":
    print("Бот запущен и готов к работе")
    app.run_polling(drop_pending_updates=True)
