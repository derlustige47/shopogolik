import logging
import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from telegram.ext import Updater

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получение токена
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("Токен Telegram не задан в окружении")

# Основной обработчик команды /start
async def start(update: Update, context: CallbackContext):
    keyboard = [
        ['Одежда', 'Для взрослых +18'],
        ['Новинки', 'Из Китая']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text('Привет! Выберите категорию или отправьте запрос для поиска на Avito.', reply_markup=reply_markup)

# Функция поиска по Avito
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
async def handle_message(update: Update, context: CallbackContext):
    query = update.message.text
    items = search_avito(query)

    if items:
        for title, price, link in items:
            await update.message.reply_text(f"Название: {title}\nЦена: {price}\nСсылка: {link}")
    else:
        await update.message.reply_text("Не удалось найти результаты. Попробуйте позже.")

# Главная функция для запуска бота
async def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Обработчики
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота с polling
    await application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
requirements.txt

python-telegram-bot==21.3
requests==2.28.1
beautifulsoup4==4.11.1
lxml==4.9.1
Объяснение кода:
Логирование: Уровень логирования установлен на INFO, чтобы отслеживать выполнение бота.

Обработчик команды /start: При отправке команды /start бот показывает меню с четырьмя кнопками.

Поиск на Avito: Бот использует библиотеку requests для получения HTML-страницы с результатами поиска по запросу. Затем с помощью BeautifulSoup извлекаются данные о товаре: название, цена и ссылка.

Обработчик текстовых сообщений: На любое текстовое сообщение бот выполняет поиск по Avito по запросу пользователя.

Ошибка: Если запрос не удаётся или нет результатов, бот сообщает об этом пользователю.

Deploy на Railway: В коде нет необходимости в отдельном старте через Custom Start Command, достаточно просто запускать python main.py. Переменные окружения, такие как TELEGRAM_TOKEN, подгружаются через os.getenv.

Как это работает:
Вы создаёте на Railway новое приложение, загружаете файлы main.py и requirements.txt.

Устанавливаете переменную окружения TELEGRAM_TOKEN в настройках приложения на Railway.

Разворачиваете приложение, и бот автоматически запускается с использованием polling.

Настройка на Railway:
Создайте новое приложение на Railway.

В разделе Settings > Environment Variables добавьте переменную TELEGRAM_TOKEN и укажите ваш токен бота.

Загрузите файлы main.py и requirements.txt.

Бот будет автоматически работать при запуске приложения.








Вы сказали:
Ты — senior Python-разработчик с большим опытом деплоя Telegram-ботов на Railway.app в 2026 году.

Создай **production-ready** код Telegram-бота с использованием **FastAPI + webhook** (НЕ polling).

Требования:
- Используй python-telegram-bot версии 21.x (или актуальную)
- FastAPI как ASGI-приложение
- Один эндпоинт /webhook для приёма обновлений от Telegram
- Правильно интегрируй Application из python-telegram-bot с FastAPI (используй process_update и Update.de_json)
- Запуск через uvicorn: uvicorn main:app --host 0.0.0.0 --port $PORT (обязательно используй переменную $PORT из Railway)
- Добавь health-check эндпоинт / который возвращает {"status": "ok"}
- Добавь простое меню с ReplyKeyboardMarkup (кнопки: "Одежда", "Для взрослых +18", "Новинки", "Из Китая")
- На /start показывай меню
- На любое текстовое сообщение выполняй поиск по Avito.ru (requests + BeautifulSoup + lxml)
- Показывай до 5 результатов с названием, ценой и ссылкой
- Добавь хорошую обработку ошибок и информативные сообщения пользователю
- Добавь logging (INFO уровень) с понятными сообщениями
- TOKEN бери строго из os.getenv("TELEGRAM_TOKEN")
- Добавь комментарии, где важно (особенно про обработку webhook и $PORT)
- Код должен быть чистым, без лишних запятых, без конфликтов polling/webhook

Также напиши отдельно содержимое **requirements.txt** с точными версиями пакетов, которые нужны для стабильной работы на Railway:
- fastapi
- uvicorn
- python-telegram-bot
- requests
- beautifulsoup4
- lxml

В конце добавь краткую инструкцию:
- Какой Custom Start Command использовать в Railway
- Как установить webhook после деплоя (пример ссылки)
- Рекомендации по настройке Public Networking и переменных

Сделай код максимально надёжным для Railway (учти $PORT, lifespan, возможные проблемы с Application object).



ChatGPT сказал:
Для создания production-ready Telegram-бота с использованием FastAPI и webhook с библиотекой python-telegram-bot версии 21.x, мы создадим интеграцию между FastAPI и Telegram через webhook. Вот пример кода, который полностью соответствует вашим требованиям.

main.py
Python


Запустить
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

# Эндпоинт для здоровья бота (health check)
@app.get("/")
async def health_check():
    return {"status": "ok"}

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

# Функция для установки webhook в Telegram
def set_webhook():
    webhook_url = os.getenv("WEBHOOK_URL")
    if not webhook_url:
        raise ValueError("Не задана переменная окружения WEBHOOK_URL")
    application.bot.set_webhook(webhook_url)

# Вызов установки webhook (только после деплоя)
if __name__ == "__main__":
    set_webhook()