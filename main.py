import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
import requests
from bs4 import BeautifulSoup

TOKEN = os.getenv("TELEGRAM_TOKEN")

keyboard = ,
    [KeyboardButton("Для взрослых +18")], , ]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context):
    await update.message.reply_text("Выбери категорию или напиши свой запрос:", reply_markup=reply_markup)

async def search(update: Update, context):
    query = update.message.text.strip()
    
    await update.message.reply_text(f"🔍 Ищу по запросу: {query}...")

    url = f"https://www.avito.ru/all?q={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    try:
        r = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        
        items = soup.find_all("div", {"data-marker": "item"})[:6]

        if not items:
            await update.message.reply_text("😔 Ничего не найдено.")
            return

        for item in items:
            title_tag = item.find("h3")
            price_tag = item.find("span", class_="price-text")
            link_tag = item.find("a")

            title = title_tag.get_text(strip=True) if title_tag else "Без названия"
            price = price_tag.get_text(strip=True) if price_tag else "Цена не указана"
            link = "https://www.avito.ru" + link_tag.get("href") if link_tag else "Ссылка отсутствует"

            await update.message.reply_text(f"{title}\n💰 {price}\n🔗 {link}\n")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при поиске: {str(e)}")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & filters.COMMAND, search))

print("Бот запущен")

if __name__ == "__main__":
    app.run_polling()
