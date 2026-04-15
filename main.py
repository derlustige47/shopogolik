import os
import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Настроим логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токен из переменной окружения
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Функция для поиска на Avito
def search_avito(query: str) -> list:
    url = f'https://www.avito.ru/search?q={query}'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    items = []
    for ad in soup.find_all('div', class_='iva-item-title-step-text'):
        title = ad.get_text(strip=True)
        price = ad.find_next('span', class_='price-text-amount')
        price = price.get_text(strip=True) if price else 'Цена не указана'
        link = ad.find_parent('a', href=True)['href']
        items.append({'title': title, 'price': price, 'link': 'https://www.avito.ru' + link})

        if len(items) >= 5:
            break
    return items

# Функция для обработки команды /start
async def start(update: Update, context: CallbackContext):
    keyboard = [
        ["Одежда", "Для взрослых +18"],
        ["Новинки", "Из Китая"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Привет! Выберите категорию или напишите запрос.", reply_markup=reply_markup)

# Функция для обработки текстовых сообщений
async def handle_message(update: Update, context: CallbackContext):
    user_text = update.message.text.strip()
    if user_text.lower() in ["одежда", "для взрослых +18", "новинки", "из китая"]:
        await update.message.reply_text(f"Вы выбрали категорию: {user_text}. Введите запрос для поиска.")
    else:
        try:
            search_results = search_avito(user_text)
            if search_results:
                message = "Результаты поиска:\n\n"
                for result in search_results:
                    message += f"🔹 {result['title']}\nЦена: {result['price']}\nСсылка: {result['link']}\n\n"
                await update.message.reply_text(message)
            else:
                await update.message.reply_text("По вашему запросу ничего не найдено.")
        except Exception as e:
            logger.error(f"Ошибка при поиске: {e}")
            await update.message.reply_text("Произошла ошибка при поиске. Попробуйте снова позже.")

# Основная функция для запуска бота
def main():
    # Создаем объект приложения
    application = Application.builder().token(TOKEN).build()

    # Обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота с polling
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
