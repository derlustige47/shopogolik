import os
import time
from telegram import Bot
import schedule

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TOKEN)

def send_message(text):
    try:
        bot.send_message(CHAT_ID, text)
        print("Отправлено:", text)
    except Exception as e:
        print("Ошибка отправки:", e)

def check():
    send_message("Шопоголик запущен и работает ")

schedule.every(3).minutes.do(check)

print("Шопоголик запущен...")
while True:
    schedule.run_pending()
    time.sleep(1)
