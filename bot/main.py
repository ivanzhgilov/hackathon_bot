import asyncio
import logging

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from aiogram_dialog import setup_dialogs

from admin_menu import admin_router
from app import dp
from articles import article_router
from commands.intro import intro_router
from commands.points_of_my_city import points_of_city_router
from core.config import config
from utils.utils import setup_logging

logger = logging.getLogger('startup')


async def main() -> None:
    logger.info('Starting the bot')
    setup_logging(level=config.log_level)
    bot = Bot(config.bot_token, parse_mode=ParseMode.HTML)
    dp.include_routers(
        intro_router,
        points_of_city_router,
        admin_router,
        article_router
    )
    dp.callback_query.middleware(CallbackAnswerMiddleware())
    setup_dialogs(dp)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
