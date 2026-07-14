import os

# Токен берем из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
ACCESS_CODE = os.getenv("ACCESS_CODE", "PHUKET2026")

# Если токен не найден — ошибка
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден! Добавьте переменную BOT_TOKEN")

# Путь к Excel файлу
EXCEL_PATH = "data/Thailand_Bot_Master_Districts_filled.xlsx"
