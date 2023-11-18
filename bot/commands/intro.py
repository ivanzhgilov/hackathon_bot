from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from schemas.user import UserInit
from services.account_service import account_service
from utils.database import db_async_session_manager

intro_router = Router(name='intro')


@intro_router.message(Command('start'))
async def start(message: Message):
    # сессия к БД также должна проходить через DI и передаваться в параметры функции, но встроенный DI у aiogram также плох
    async with db_async_session_manager() as session:
        await account_service.register_account(
            session, UserInit(
                chat_id=message.from_user.id,
                login=message.from_user.username,
                name=message.from_user.first_name,
                surname=message.from_user.last_name,
            )
        )

        await message.answer('Привет!')
