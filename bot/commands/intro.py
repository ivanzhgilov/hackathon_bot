import enum

from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Window, Dialog, DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button, Row, Column, Url
from aiogram_dialog.widgets.text import Const

from app import dp
from commands.state_classes import MainMenu, AdminMenu, PointCreate, EcoPiggyBank, GetClosestPoint, ArticleChoose, \
    Links
from core.text import dialogs
from repositories.admin_password_repository import password_repository
from repositories.command_repository import command_repository
from schemas import command
from schemas.admin_password import AdminPassword
from schemas.user import UserInit
from services.account_service import account_service
from utils.database import db_async_session_manager

intro_dialogs = dialogs['intro']


@dp.message(Command("start"))
async def start(message: Message, dialog_manager: DialogManager):
    async with db_async_session_manager() as session:
        if message.from_user.username:
            await account_service.register_account(
                session, UserInit(
                    chat_id=message.from_user.id,
                    login=message.from_user.username,
                    name=message.from_user.first_name,
                    surname="None",
                    admin=False
                )
            )
        else:
            await account_service.register_account(
                session, UserInit(
                    chat_id=message.from_user.id,
                    login="None",
                    name=message.from_user.first_name,
                    surname="None",
                    admin=False
                )
            )
        await password_repository.create_point(session, AdminPassword(
            password="$argon2id$v=19$m=65536,t=3,p=4$TAsLRMUhXkRf9N5bAB5Saw$/LeN+tSQCsFq9k+bsNA9pisByIdDBXVnoNf/qMZso+w"))

    await dialog_manager.start(MainMenu.main)


@dp.message(Command("admin"))
async def admin(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(AdminMenu.admin_password, mode=StartMode.NORMAL)


async def point_request_start(callback: CallbackQuery, button: Button,
                              manager: DialogManager):
    await manager.start(PointCreate.title)


async def eco_bank_start(callback: CallbackQuery, button: Button,
                         manager: DialogManager):
    async with db_async_session_manager() as session:
        await command_repository.create_point(session, command.Command(name="eco_bank",
                                                                       chat_id=callback.message.chat.id))
    await manager.start(EcoPiggyBank.show)


async def points_of_city_start(callback: CallbackQuery, button: Button,
                               manager: DialogManager):
    async with db_async_session_manager() as session:
        await command_repository.create_point(session, command.Command(name="points_of_city",
                                                                       chat_id=callback.message.chat.id))
    await manager.start(GetClosestPoint.getting_cords)


async def articles_start(callback: CallbackQuery, button: Button,
                         manager: DialogManager):
    async with db_async_session_manager() as session:
        await command_repository.create_point(session, command.Command(name="articles",
                                                                       chat_id=callback.message.chat.id))
    await manager.start(ArticleChoose.choosing_article)


async def useful_links_start(callback: CallbackQuery, button: Button,
                             manager: DialogManager):
    async with db_async_session_manager() as session:
        await command_repository.create_point(session, command.Command(name="useful_links",
                                                                       chat_id=callback.message.chat.id))
    await manager.start(Links.links)


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
           Button(Const(intro_dialogs['start']['recycling_tips_button']), id='recycling_tips',
                  on_click=articles_start)),
    Row(Url(Const(intro_dialogs['start']['eco_lesson_button']), Const("https://sobiraet.yugra-ecology.ru/form")),
        Button(Const(intro_dialogs['start']['eco_piggy_bank_button']), id='eco_piggy_bank',
               on_click=eco_bank_start),
        Button(Const(intro_dialogs['start']['useful_links_button']), id='useful_links',
               on_click=useful_links_start)),
    state=MainMenu.main,
)

intro_router = Dialog(main_window)
