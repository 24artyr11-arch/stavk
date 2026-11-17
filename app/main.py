import asyncio
import logging

from aiohttp import web
from aiogram import Bot

from app.bot import create_dispatcher
from app.config import settings, validate_settings
from app.db import db
from app.webapp import create_web_app

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    validate_settings()
    await db.connect()
    bot = Bot(token=settings.bot_token)
    dp = create_dispatcher()
    app = create_web_app()
    runner = web.AppRunner(app)
    try:
        await runner.setup()
        site = web.TCPSite(runner, host="0.0.0.0", port=settings.port)
        await site.start()
        logging.info("Mini App web server listening on port %s", settings.port)
        if not settings.webapp_url:
            logging.warning("WEBAPP_URL is empty; the Mini App button will not be shown")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types() + ["channel_post"])
    finally:
        await runner.cleanup()
        await bot.session.close()
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())

