import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN не найден!")

# Lifespan для правильной инициализации
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    logger.info("Запуск бота...")
    tg_app = Application.builder().token(TOKEN).build()
    await tg_app.initialize()
    await tg_app.start()
    
    # Регистрация обработчиков
    keyboard = [
        [KeyboardButton("Одежда")],
        [KeyboardButton("Для взрослых +18")],
        [KeyboardButton("Новинки")],
        [KeyboardButton("Из Китая")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    async def start(update: Update, context):
        await update.message.reply_text("👋 Выбери категорию:", reply_markup=reply_markup)

    async def search(update: Update, context):
        query = update.message.text.strip()
        await update.message.reply_text(f"🔍 Ищу: {query}...")

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
                    await update.message.reply_text(f"{title_text}\n💰 {price_text}\n🔗 {link_text}")
            else:
                await update.message.reply_text("Ничего не найдено.")
        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")
            await update.message.reply_text("Ошибка поиска, попробуй позже.")

    tg_app.add_handler(CommandHandler("start", start))
    tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))

    logger.info("Бот успешно запущен (webhook)")
    yield

    # SHUTDOWN
    logger.info("Остановка бота...")
    await tg_app.stop()
    await tg_app.shutdown()

app = FastAPI(lifespan=lifespan)

# Health check
@app.get("/")
async def health():
    return {"status": "ok"}

# Webhook
@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, tg_app.bot)   # обратите внимание: tg_app нужно сделать глобальным
        await tg_app.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")