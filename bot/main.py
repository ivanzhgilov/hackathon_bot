import asyncio
import logging

from aiogram import Bot
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from aiogram_dialog import setup_dialogs

from commands.admin_delete_point import delete_point_router
from commands.admin_menu import admin_router
from commands.admin_point_create import admin_point_create_router
from app import dp, bot
from commands.articles import article_router
from core.config import config
from commands.intro import intro_router
from commands.points_of_my_city import points_of_city_router
from commands.eco_piggy_bank import eco_bank_router
from commands.get_stats import stats_router
from commands.managing_articles import managing_articles_router
from commands.newsletter import newsletter_router
from commands.point_create import point_create_router
from utils.utils import setup_logging, get_poster, send_message_to_all_users

logger = logging.getLogger('startup')


async def check_vk_posts_and_send_messages(bot: Bot):
    last_post = await get_poster(None)
    while True:
        new_post = await get_poster(last_post)
        if new_post:
            await send_message_to_all_users(bot, new_post)
            last_post = new_post

        await asyncio.sleep(100)


async def main(bot) -> None:
    logger.info('Starting the bot')
    setup_logging(level=config.log_level)
    dp.include_routers(
        intro_router,
        points_of_city_router,
        admin_router,
        article_router,
        managing_articles_router,
        point_create_router,
        eco_bank_router,
        newsletter_router,
        admin_point_create_router,
        stats_router,
        delete_point_router
    )
    dp.callback_query.middleware(CallbackAnswerMiddleware())
    setup_dialogs(dp)

    asyncio.create_task(check_vk_posts_and_send_messages(bot))

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main(bot))
