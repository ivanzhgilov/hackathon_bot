import asyncio
import logging

from aiogram import Bot
from aiogram.enums import ParseMode

from app import dp
from commands.intro import intro_router
from core.config import config
from utils.utils import setup_logging

logger = logging.getLogger('startup')


async def main() -> None:
    logger.info('Starting the bot')
    setup_logging(level=config.log_level)
    bot = Bot(config.bot_token, parse_mode=ParseMode.HTML)
    dp.include_routers(
        intro_router
    )
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
