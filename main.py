import os
import time
from telegram import Bot
import schedule

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

bot = Bot(token=TOKEN)

def send(text):
    try:
        bot.send_message(CHAT_ID, text, parse_mode='HTML')
    except:
        pass

# ← СЮДА БУДЕШЬ ДОБАВЛЯТЬ ВСЁ, ЧТО ХОЧЕШЬ МОНИТОРИТЬ
watches = [
    {"name": "iPhone 13", "url": "https://www.avito.ru/moskva?q=iphone+13", "price_max": 35000},
    {"name": "RTX 3060", "url": "https://www.avito.ru/moskva?q=rtx+3060", "price_max": 25000},
    # сюда добавляешь новые вещи
]

def check_site(watch):
    try:
        r = requests.get(watch , headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if r.status_code == 200:
            send(f"Проверил <b>{watch }</b>")
    except:
        pass

for w in watches:
    schedule.every(4).minutes.do(check_site, w)

print("Шопоголик запущен. Следит за разными вещами...")

while True:
    schedule.run_pending()
    time.sleep(1)
