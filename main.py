Ты — опытный Python-разработчик, специализирующийся на Telegram-ботах и деплое на Railway.app.

Создай **полный, минимальный и надёжный** код для Telegram-бота на библиотеке `python-telegram-bot` версии 21+.

Требования:
- Бот использует **polling** (`app.run_polling()`)
- Добавь `drop_pending_updates=True` для избежания конфликтов
- Добавь простое меню с ReplyKeyboardMarkup (4 кнопки: "Одежда", "Для взрослых +18", "Новинки", "Из Китая")
- На команду /start бот показывает меню
- На любое текстовое сообщение бот делает поиск по Avito.ru по этому запросу (используй requests + BeautifulSoup)
- Показывай максимум 5 результатов: название, цену и ссылку
- Добавь обработку ошибок и понятные сообщения пользователю
- Используй logging (INFO уровень)
- TOKEN бери из os.getenv("TELEGRAM_TOKEN")
- Код должен работать сразу после деплоя на Railway без Custom Start Command (просто python main.py)
- requirements.txt должен содержать только необходимые пакеты: python-telegram-bot, requests, beautifulsoup4, lxml

Напиши **полный main.py** и отдельно **requirements.txt**.

Сделай код максимально чистым, без лишних запятых, без FastAPI/uvicorn, без webhook.
