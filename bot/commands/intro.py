import enum

from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import Window, Dialog, DialogManager, StartMode, DialogProtocol
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Row, Column, Cancel
from aiogram_dialog.widgets.text import Const

from app import dp
from commands.points_of_my_city import points_of_city_start
from commands.state_classes import MainMenu, AdminMenu
from core.text import dialogs
from schemas.user import UserInit
from services.account_service import account_service
from services.statistic_service import statistic_service
from utils.database import db_async_session_manager
from utils.utils import check_password

intro_dialogs = dialogs['intro']


@dp.message(Command("start"))
async def start(message: Message, dialog_manager: DialogManager):
    async with db_async_session_manager() as session:
        await account_service.register_account(
            session, UserInit(
                chat_id=message.from_user.id,
                login=message.from_user.username,
                name=message.from_user.first_name,
                surname=message.from_user.last_name,
            )
        )

        stat = await statistic_service.active_statistic(session)

    await dialog_manager.start(MainMenu.main)


@dp.message(Command("admin"))
async def admin(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(AdminMenu.admin_password, mode=StartMode.NORMAL)


async def password_sent(message: Message, dialog: DialogProtocol, manager: DialogManager):
    if await check_password(message.text):
        await manager.next()


class IntroActionKinds(str, enum.Enum):
    confirm = 'confirm'
    eco_lesson = 'eco_lesson'
    recycling_tips = 'recycling_tips'
    eco_piggy_bank = 'eco_piggy_bank'
    useful_links = 'useful_links'
    points_of_city = 'points_of_city'


main_window = Window(
    Const(intro_dialogs['start']['hello']),
    Column(Button(Const(intro_dialogs['start']['points_of_city_button']), id='points_of_city',
                  on_click=points_of_city_start),
           Button(Const(intro_dialogs['start']['recycling_tips_button']), id='recycling_tips')),
    Row(Button(Const(intro_dialogs['start']['eco_lesson_button']), id='eco_lesson'),
        Button(Const(intro_dialogs['start']['eco_piggy_bank_button']), id='eco_piggy_bank'),
        Button(Const(intro_dialogs['start']['useful_links_button']), id='useful_links')),

    state=MainMenu.main,
)

admin_router = Dialog(Window(
    Const(intro_dialogs['admin']['password']),
    Cancel(Const("Главное меню")),
    MessageInput(password_sent),
    state=AdminMenu.admin_password
),
    Window(Const('OOOO ADMIN'), Column(Button(Const(intro_dialogs['admin']['new_article_button']), id='new_article'),
                                       Button(Const(intro_dialogs['admin']['post_news_button']), id='post_news'),
                                       Button(Const(intro_dialogs['admin']['get_statistic_button']),
                                              id='get_statistic')),
           state=AdminMenu.admin_operations))

intro_router = Dialog(main_window)
