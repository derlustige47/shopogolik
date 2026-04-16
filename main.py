import os
import logging
from fastapi import FastAPI, Request, HTTPException
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.ext import Dispatcher
import requests
from bs4 import BeautifulSoup
import json

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токен Telegram из переменной окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("Токен Telegram не задан в окружении")

# Инициализация FastAPI приложения
app = FastAPI()

# Инициализация Telegram Application (для webhook)
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Функция для создания клавиатуры
def create_keyboard():
    keyboard = [
        ['Одежда', 'Для взрослых +18'],
        ['Новинки', 'Из Китая']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Обработчик команды /start
async def start(update: Update, context):
    keyboard = create_keyboard()
    await update.message.reply_text("Привет! Выберите категорию или отправьте запрос для поиска на Avito.", reply_markup=keyboard)

# Функция поиска на Avito
def search_avito(query: str):
    url = f"https://www.avito.ru/search?q={query}&p=1"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Проверка на ошибки HTTP
        soup = BeautifulSoup(response.text, 'lxml')

        items = []
        for ad in soup.find_all('div', {'class': 'iva-item-content'}):
            title = ad.find('h3').get_text(strip=True)
            price = ad.find('span', {'class': 'price'}).get_text(strip=True) if ad.find('span', {'class': 'price'}) else 'Цена не указана'
            link = 'https://www.avito.ru' + ad.find('a', {'class': 'link'})['href']
            items.append((title, price, link))
            if len(items) == 5:
                break

        return items

    except requests.RequestException as e:
        logger.error(f"Ошибка при запросе к Avito: {e}")
        return None

# Обработчик текстовых сообщений
async def handle_message(update: Update, context):
    query = update.message.text
    items = search_avito(query)

    if items:
        for title, price, link in items:
            await update.message.reply_text(f"Название: {title}\nЦена: {price}\nСсылка: {link}")
    else:
        await update.message.reply_text("Не удалось найти результаты. Попробуйте позже.")

# Настройка webhook (обработчик входящих обновлений от Telegram)
@app.post("/webhook")
async def webhook(request: Request):
    try:
        json_str = await request.json()
        update = Update.de_json(json_str, application.bot)
        # Обработка полученного обновления
        Dispatcher(application, update)
        await application.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Ошибка при обработке webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Регистрация обработчиков для команд
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Вызов установки webhook (только после деплоя)
def set_webhook():
    webhook_url = os.getenv("WEBHOOK_URL")
    if not webhook_url:
        raise ValueError("Не задана переменная окружения WEBHOOK_URL")
    application.bot.set_webhook(webhook_url)

# Вызов установки webhook (только после деплоя)
if __name__ == "__main__":
    set_webhook()
    logger.info("Бот запущен и webhook установлен")
