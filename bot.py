import asyncio
import logging
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession
import aiohttp

import database as db
from handlers import router

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска бота"""
    # Инициализация базы данных
    await db.init_db()
    
    # Получение токена
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("BOT_TOKEN не найден в .env файле!")
        return
    
    # Настройка прокси (если нужно)
    proxy_url = os.getenv("PROXY_URL")  # например: "http://proxy:port"
    
    session = None
    if proxy_url:
        connector = aiohttp.ProxyConnector.from_url(proxy_url)
        session = AiohttpSession(connector=connector)
        logger.info(f"Используется прокси: {proxy_url}")
    
    # Создание бота и диспетчера
    bot = Bot(
        token=token,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Увеличиваем таймаут для медленного соединения
    dp.startup.register(lambda: logger.info("Бот готов к работе!"))
    
    # Регистрация роутеров
    dp.include_router(router)
    
    logger.info("Попытка подключения к Telegram...")
    
    # Запуск polling с увеличенным таймаутом
    try:
        await dp.start_polling(bot, timeout=60, relax=0.1)
    except Exception as e:
        logger.error(f"Ошибка подключения: {e}")
        logger.info("Проверь интернет-соединение и токен бота")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
