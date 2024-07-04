import operator

from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, Window, DialogProtocol, DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Cancel, Back, Next, Column, Multiselect, Button
from aiogram_dialog.widgets.text import Const, Format

from app import dp
from commands.state_classes import PointCreate
from core.text import dialogs
from models import command
from repositories.command_repository import command_repository
from repositories.point_repository import point_repository
from schemas.point_request import PointRequest
from utils.database import db_async_session_manager

intro_dialogs = dialogs['intro']
point_create_router = Router(name='point_create')

waste_select = Multiselect(
    Format("✓ {item[0]}"),
    Format("{item[0]}"),
    id="m_waste_types",
    item_id_getter=operator.itemgetter(1),
    items="waste_types"
)

categories = ['Бумага📃',
              'Пластик🔫',
              'Стекло🍾',
              'Металл🔧',
              'Одежда🎩',
              'Лампочки💡',
              'Крышечки🔴',
              'Техника📱',
              'Батареки🪫',
              'Шины🛞',
              'Опасное☢',
              'Другое ']


async def get_data(**kwargs):
    waste_types = [(el, i) for i, el in enumerate(categories)]
    return {
        "waste_types": waste_types,
        "count": len(waste_types),
    }


async def insert_title(message: Message, dialog: DialogProtocol, manager: DialogManager):
    manager.dialog_data['title'] = message.text
    await manager.next()


async def insert_description(message: Message, dialog: DialogProtocol, manager: DialogManager):
    manager.dialog_data['description'] = message.text
    await manager.next()


async def insert_adress(message: Message, dialog: DialogProtocol, manager: DialogManager):
    manager.dialog_data['address'] = message.text
    await manager.next()


async def insert_phone(message: Message, dialog: DialogProtocol, manager: DialogManager):
    manager.dialog_data['phone_number'] = message.text
    await manager.next()


async def process_categories(callback: CallbackQuery, button: Button, manager: DialogManager):
    chosen = [categories[int(i)][:-1] for i in waste_select.get_checked(manager)]
    manager.dialog_data['types_of_garbage'] = ', '.join(chosen)
    await manager.next()


async def save(callback: CallbackQuery, button: Button, manager: DialogManager):
    manager.dialog_data['author'] = f'@{callback.from_user.username}'
    dct = manager.dialog_data
    async with db_async_session_manager() as session:
        await command_repository.create_point(session, command.Command(name="point_request",
                                                                       user=callback.from_user.chat_id))

    async with db_async_session_manager() as session:
        await point_repository.create_point(session, PointRequest(lat=None, lon=None, **dct))
    await manager.next()


dialog = Dialog(Window(Const("Отправьте название точки"), Cancel(Const("Отмена❌")), MessageInput(insert_title),
                       state=PointCreate.title),
                Window(Const("Отправьте описание точки"),
                       Back(Const("Назад⬅️")), Cancel(Const("Отмена❌")), MessageInput(insert_description),
                       state=PointCreate.description),
                Window(Const("Отправьте адрес точки аналогично\nНижневартовск, Маршала Жукова, 6А"),
                       Back(Const("Назад⬅️")), Cancel(Const("Отмена❌")),
                       MessageInput(insert_adress), state=PointCreate.address),
                Window(Const("Отправьте номер телефона  по которому можно связаться с работниками точки"),
                       Back(Const("Назад⬅️")), Cancel(Const("Отмена❌")),
                       MessageInput(insert_phone), state=PointCreate.phone_number),
                Window(
                    Const("Выберите виды мусора для сортировки"),
                    Button(Const("Категории выбраны✔️"), id="all_done", on_click=process_categories),
                    Column(waste_select),
                    getter=get_data,
                    state=PointCreate.types_of_garbage
                ),
                Window(Format("""{dialog_data[title]}
        
{dialog_data[description]}

{dialog_data[address]}

Принимается: {dialog_data[types_of_garbage]}

Номер телефона: {dialog_data[phone_number]}"""),
                       Cancel(Const("Отмена❌")), Back(Const("Назад⬅️")),
                       Button(Const("Подтвердить✅"), id="approve", on_click=save), state=PointCreate.sure),
                Window(Const('Запрос на добавление точки отправлен успешно!'), Cancel(Const("Главное меню🏠")),
                       state=PointCreate.save)
                )

dp.include_router(dialog)
