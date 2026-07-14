#!/usr/bin/env python3
"""
Справочник Пхукета — Telegram бот
Запуск: python bot.py
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, EXCEL_PATH
from data_loader import DataLoader
from handlers import router, init_data_loader

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    """Главная функция запуска бота"""
    logger.info("🚀 Запуск бота...")
    
    # Проверяем токен
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не найден! Проверьте config.py")
        return
    
    # Загружаем данные
    logger.info(f"📂 Загрузка данных из {EXCEL_PATH}")
    try:
        init_data_loader(EXCEL_PATH)
        logger.info("✅ Данные загружены успешно")
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки данных: {e}")
        return
    
    # Создаем бота
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Подключаем обработчики
    dp.include_router(router)
    
    # Запускаем
    logger.info("🤖 Бот запущен! Нажмите /start в Telegram")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")