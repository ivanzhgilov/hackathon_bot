from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Window, Dialog, DialogManager, DialogProtocol, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Column, Cancel
from aiogram_dialog.widgets.text import Const
from sqlalchemy import select

from commands.state_classes import AdminMenu, ArticleManage, CreatingNewsletter, AdminPointCreate, \
    AdminPointRequestsWatching, MainMenu, GetStats, PointDelete
from core.text import dialogs
from models import AdminPassword
from utils.database import db_async_session_manager
from utils.utils import check_password

admin_dialogs = dialogs['admin']


async def start_point_delete(callback, button, manager):
    await manager.start(PointDelete.choosing)


async def password_sent(message: Message, dialog: DialogProtocol, manager: DialogManager):
    async with db_async_session_manager() as session:
        hashed_password = await session.scalar(select(AdminPassword).where(AdminPassword.id == 1))
    if check_password(hashed_password.password, message.text):
        await message.delete()
        await manager.next()


async def manage_articles_start(callback, button, manager):
    await manager.start(ArticleManage.start)


async def newsletter_start(callback, button, manager):
    await manager.start(CreatingNewsletter.text_insert)


async def admin_point_add_start(callback, button, manager):
    await manager.start(AdminPointCreate.title)


async def start_watch_point_requests(callback, button, manager):
    await manager.start(AdminPointRequestsWatching.points)


async def main_menu(callback: CallbackQuery, button: Button,
                    manager: DialogManager):
    await manager.start(MainMenu.main, mode=StartMode.RESET_STACK)


async def get_statistic(callback: CallbackQuery, button: Button,
                        manager: DialogManager):
    await manager.start(GetStats.days)


admin_router = Dialog(Window(
    Const(admin_dialogs['password']),
    Cancel(Const("Главное меню🏠")),
    MessageInput(password_sent),
    state=AdminMenu.admin_password
),
    Window(Const('Меню администратора'), Column(
        Button(Const(admin_dialogs['manage_articles_button']), id='manage_articles', on_click=manage_articles_start),
        Button(Const(admin_dialogs['post_news_button']), id='post_news', on_click=newsletter_start),
        Button(Const("Добавить точку"), id='admin_add_point', on_click=admin_point_add_start),
        Button(Const("Удалить точку"), id='admin_delete_point', on_click=start_point_delete),
        Button(Const(admin_dialogs['get_statistic_button']),
               id='get_statistic', on_click=get_statistic),
        Button(Const("Главное меню🏠"), id="main_menu", on_click=main_menu)),
           state=AdminMenu.admin_operations))
