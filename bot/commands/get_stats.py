from datetime import datetime, timedelta

from aiogram import Router
from aiogram.types import Message
from aiogram_dialog import Dialog, Window, DialogProtocol, DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Cancel, Back
from aiogram_dialog.widgets.text import Const, Format
from sqlalchemy import select, func

from app import dp
from commands.state_classes import GetStats
from core.text import dialogs
from models.command import Command
from models.user import User
from utils.database import db_async_session_manager
from utils.utils import count_active_users, command_usage

intro_dialogs = dialogs['intro']
stats_router = Router(name='stats_router')


async def insert_days(message: Message, dialog: DialogProtocol, manager: DialogManager):
    if message.text.isdigit():
        n = int(message.text)
        manager.dialog_data['days'] = n
        time_threshold = datetime.now() - timedelta(days=n)
        async with db_async_session_manager() as session:
            commands = await session.execute(
                select(Command).where(func.to_timestamp(func.extract('epoch', Command.created_at)) >= time_threshold)
            )
            commands = commands.scalars().all()
            users = await session.execute(
                select(User).where(func.to_timestamp(func.extract('epoch', User.created_at)) >= time_threshold)
            )
            users = users.scalars().all()
            manager.dialog_data['new_users'] = len(users)
            manager.dialog_data['active_users'] = await count_active_users(commands)
            data = await command_usage(commands)
            for key in data.keys():
                manager.dialog_data[key] = data[key]

        await manager.next()
    else:
        await message.answer("Отправьте число")


dialog = Dialog(Window(Const('За сколько дней вы хотите получить статистику?'),
                       Cancel(Const("Меню администратора")), MessageInput(insert_days), state=GetStats.days),
                Window(Format("""За {dialog_data[days]} дней:
Новых пользователей: {dialog_data[new_users]}
Активных пользователей: {dialog_data[active_users]}

Использование функций:
Справочник отходов: {dialog_data[articles]}
Пункты приема: {dialog_data[points_of_city]}
ЭКО-копилка: {dialog_data[eco_bank]}
Полезные ссылки: {dialog_data[useful_links]}"""), Back(Const("Назад⬅️")), Cancel(Const("Меню администратора")),
                       state=GetStats.stats))

dp.include_router(dialog)
