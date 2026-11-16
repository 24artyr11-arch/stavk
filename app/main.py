import asyncio
import logging

from aiogram import Bot

from app.bot import create_dispatcher
from app.config import settings, validate_settings
from app.db import db

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    validate_settings()
    await db.connect()
    bot = Bot(token=settings.bot_token)
    dp = create_dispatcher()
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types() + ["channel_post"])
    finally:
        await bot.session.close()
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())

