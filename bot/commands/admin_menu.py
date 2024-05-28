from aiogram.types import Message
from aiogram_dialog import Window, Dialog, DialogManager, DialogProtocol
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Column, Cancel
from aiogram_dialog.widgets.text import Const
from sqlalchemy import select

from commands.state_classes import AdminMenu, ArticleManage, CreatingNewsletter
from core.text import dialogs
from models import AdminPassword
from utils.database import db_async_session_manager
from utils.utils import check_password

admin_dialogs = dialogs['admin']


async def password_sent(message: Message, dialog: DialogProtocol, manager: DialogManager):
    async with db_async_session_manager() as session:
        hashed_password = await session.scalar(select(AdminPassword).where(AdminPassword.id == 1))
    if check_password(hashed_password.password, message.text):
        await manager.next()


async def manage_articles_start(callback, button, manager):
    await manager.start(ArticleManage.start)


async def newsletter_start(callback, button, manager):
    await manager.start(CreatingNewsletter.text_insert)


admin_router = Dialog(Window(
    Const(admin_dialogs['password']),
    Cancel(Const("Главное меню")),
    MessageInput(password_sent),
    state=AdminMenu.admin_password
),
    Window(Const('OOOO ADMIN'), Column(
        Button(Const(admin_dialogs['manage_articles_button']), id='manage_articles', on_click=manage_articles_start),
        Button(Const(admin_dialogs['post_news_button']), id='post_news', on_click=newsletter_start),
        Button(Const(admin_dialogs['get_statistic_button']),
               id='get_statistic'),
        Cancel(Const("Главное меню"))),
           state=AdminMenu.admin_operations))
