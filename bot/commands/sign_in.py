import os

from aiogram import Router
from aiogram.types import Message
from aiogram_dialog import DialogManager, Dialog, Window, DialogProtocol, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Cancel, Next
from aiogram_dialog.widgets.text import Const

from app import dp
from commands.state_classes import SignIn, AccountMainPage
from core.text import dialogs
from repositories.user_repository import user_repository
from utils.database import db_async_session_manager

sign_in_router = Router(name='sign_in_router')

entry = dialogs['entry']


async def insert_login(message: Message, dialog: DialogProtocol, manager: DialogManager):
    async with db_async_session_manager() as session:
        logins = await user_repository.get_all_logins(session)
        if message.text not in logins:
            await manager.next()
        else:
            await message.reply(entry['login_exists'])


async def insert_password(message: Message, dialog: DialogProtocol, manager: DialogManager):
    manager.dialog_data['password'] = message.text
    await message.delete()
    await manager.next()


async def confirm_password(message: Message, dialog: DialogProtocol, manager: DialogManager):
    if message.text == manager.dialog_data['password']:
        async with db_async_session_manager() as session:
            await user_repository.update_hashed_password_by_chat_id(session, message.chat.id, message.text)
        await message.delete()
        await manager.start(AccountMainPage.main, mode=StartMode.RESET_STACK)
    else:
        await message.reply(entry['different_passwords'])
        await message.delete()


dialog = Dialog(Window(Const(entry['sign_in']), Next(Const('далее')), Cancel(Const("Отмена❌")),
                       MessageInput(insert_login), state=SignIn.login),
                Window(Const(entry['password']), Back(Const("Назад⬅️")), Cancel(Const("Отмена❌")),
                       MessageInput(insert_password), state=SignIn.password),
                Window(Const(entry['password']), Back(Const("Назад⬅️")), Cancel(Const("Отмена❌")),
                       MessageInput(confirm_password), state=SignIn.password_confirm))

dp.include_router(dialog)
