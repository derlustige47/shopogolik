import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
import requests
from bs4 import BeautifulSoup

TOKEN = os.getenv("TELEGRAM_TOKEN")

# Главное меню категорий
category_keyboard = [
    [KeyboardButton("Одежда")],
    [KeyboardButton("Для взрослых +18")],
    [KeyboardButton("Новинки")],
    [KeyboardButton("Из Китая")],
    [KeyboardButton("Wildberries")],
    [KeyboardButton("Ozon")]
]
category_markup = ReplyKeyboardMarkup(category_keyboard, resize_keyboard=True)

# Меню типа товара
type_keyboard = [
    [KeyboardButton("Новое")],
    [KeyboardButton("Б/у")],
    [KeyboardButton("Все вместе")]
]
type_markup = ReplyKeyboardMarkup(type_keyboard, resize_keyboard=True)

async def start(update: Update, context):
    await update.message.reply_text(
        "👋 Выбери категорию:",
        reply_markup=category_markup
    )

async def handle_message(update: Update, context):
    text = update.message.text.strip()

    # Если это выбор категории
    if text in ["Одежда", "Для взрослых +18", "Новинки", "Из Китая", "Wildberries", "Ozon"]:
        context.user_data['category'] = text
        await update.message.reply_text(
            f"Выбрано: {text}\nТеперь выбери тип товара:",
            reply_markup=type_markup
        )
        return

    # Если это выбор типа (Новое / Б/у / Все)
    category = context.user_data.get('category')
    if not category:
        await update.message.reply_text("Сначала выбери категорию через /start")
        return

    await update.message.reply_text(f"🔍 Ищу {text} в категории «{category}»...")

    query = category.lower()

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        if text == "Б/у":
            # Только Avito + б/у
            url = f"https://www.avito.ru/all?q={query.replace(' ', '+')}&s=1"  # s=1 = б/у
            platform = "Avito (б/у)"
        elif text == "Новое":
            # Все площадки + новые вещи
            url = f"https://www.avito.ru/all?q={query.replace(' ', '+')}"
            platform = "Avito + Wildberries + Ozon (новое)"
        else:
            # Все вместе
            url = f"https://www.avito.ru/all?q={query.replace(' ', '+')}"
            platform = "Avito"

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
                await update.message.reply_text(f"{platform}:\n{title_text}\n{price_text}\n{link_text}")
        else:
            await update.message.reply_text("Ничего не найдено.")

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & filters.COMMAND, handle_message))

print("Шопоголик запущен с выбором Новое / Б/у / Все")

if __name__ == "__main__":
    app.run_polling()
