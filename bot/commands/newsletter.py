import os

from aiogram import Router
from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, Dialog, Window, DialogProtocol
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Cancel, Button, Url
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format
from sqlalchemy import select

from app import dp, bot
from commands.state_classes import CreatingNewsletter, Links
from core.text import dialogs
from models import User
from utils.database import db_async_session_manager

intro_dialogs = dialogs['intro']
newsletter_router = Router(name='newsletter')

commands_dir = os.path.dirname(os.path.abspath(__file__))


async def get_data(**kwargs):
    manager = kwargs['dialog_manager']
    image_id = manager.dialog_data['id']
    image = MediaAttachment(ContentType.PHOTO, file_id=MediaId(image_id))
    return {'photo': image}


async def insert_text(message: Message, dialog: DialogProtocol, manager: DialogManager):
    manager.dialog_data['text'] = message.text
    await manager.next()


async def insert_media(message: Message, dialog: DialogProtocol, manager: DialogManager):
    manager.dialog_data['id'] = message.photo[-1].file_id
    await manager.next()


async def approve_newsletter(callback: CallbackQuery, button: Button, manager: DialogManager):
    async with db_async_session_manager() as session:
        users = await session.execute(select(User))
    for user in users.scalars().all():
        await bot.send_photo(chat_id=user.chat_id, photo=manager.dialog_data['id'], caption=manager.dialog_data['text'])
    await manager.next()


dialog = Dialog(Window(Const('Введите текст новости'), Cancel(Const("Отмена❌")),
                       MessageInput(insert_text), state=CreatingNewsletter.text_insert),
                Window(Const('Отправьте фото'), Back(Const("Назад⬅️")), Cancel(Const("Отмена❌")),
                       MessageInput(insert_media), state=CreatingNewsletter.media_insert),
                Window(Format("{dialog_data[text]}"),
                       DynamicMedia("photo"),
                       Button(Const("Подтвердить✅"), id="approve_newsletter", on_click=approve_newsletter),
                       Back(Const("Назад⬅️")),
                       Cancel(Const("Главное меню🏠")), state=CreatingNewsletter.sure, getter=get_data),
                Window(Const("Успешно!"), Cancel(Const('В меню администратора')), state=CreatingNewsletter.result))

subdialog = Dialog(
    Window(Const('Полезные ссылки'), Url(Const("ВКонтакте"), Const("https://vk.com/eco4u2")),
           Url(Const("Телеграм"), Const("https://t.me/yugraecology")),
           Url(Const("Одноклассники"), Const("https://ok.ru/group/55933980573950")),
           Url(Const("Сайт Югра Собирает"), Const("https://sobiraet.yugra-ecology.ru/")),
           Cancel(Const("Главное меню🏠")), state=Links.links))

dp.include_router(dialog)
dp.include_router(subdialog)
