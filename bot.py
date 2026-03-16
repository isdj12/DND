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

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def main():
    await db.init_db()

    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("BOT_TOKEN не найден в .env файле!")
        return

    proxy_url = os.getenv("PROXY_URL")
    session = None
    if proxy_url:
        connector = aiohttp.ProxyConnector.from_url(proxy_url)
        session = AiohttpSession(connector=connector)

    bot = Bot(token=token, session=session, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)

    logger.info("Бот запущен!")
    try:
        await dp.start_polling(bot, timeout=60, relax=0.1)
    except Exception as e:
        logger.error(f"Ошибка подключения: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
