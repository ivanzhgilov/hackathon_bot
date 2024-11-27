from aiogram import Router
from aiogram.types import Message
from aiogram_dialog import DialogManager, Dialog, Window, DialogProtocol, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Cancel, Next
from aiogram_dialog.widgets.text import Const

from app import dp
from commands.state_classes import AccountMainPage, LogIn
from core.text import dialogs
from repositories.user_repository import user_repository
from utils.database import db_async_session_manager
from utils.utils import hash_password, check_password

log_in_router = Router(name='log_in_router')

entry = dialogs['entry']


async def insert_login(message: Message, dialog: DialogProtocol, manager: DialogManager):
    async with db_async_session_manager() as session:
        logins = await user_repository.get_all_logins(session)
        if message.text in logins:
            manager.dialog_data['login'] = message.text
            await manager.next()
        else:
            await message.answer(entry['no_such_login'])


async def insert_password(message: Message, dialog: DialogProtocol, manager: DialogManager):
    async with db_async_session_manager() as session:
        if manager.dialog_data.get('login'):
            hashed_password = (
                await user_repository.get_user_by_login(session, manager.dialog_data['login'])).hashed_password
        else:
            hashed_password = (
                await user_repository.get_user_by_login(session, message.from_user.username)).hashed_password
        if check_password(hashed_password, message.text):
            await message.delete()
            await user_repository.update_login_status_by_chat_id(session, message.chat.id, True)
            await manager.start(AccountMainPage.main, mode=StartMode.RESET_STACK)
        else:
            await message.answer(entry['wrong_password'])
            await message.delete()


dialog = Dialog(Window(Const(entry['sign_in']), Next(Const('далее')), Cancel(Const("Отмена❌")),
                       MessageInput(insert_login), state=LogIn.login),
                Window(Const(entry['insert_password']), Back(Const("Назад⬅️")), Cancel(Const("Отмена❌")),
                       MessageInput(insert_password), state=LogIn.password))

dp.include_router(dialog)
