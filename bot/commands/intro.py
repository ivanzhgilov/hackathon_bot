from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

intro_router = Router(name='intro')


@intro_router.message(Command('start'))
async def start(message: Message):
    await message.answer('Привет!')
