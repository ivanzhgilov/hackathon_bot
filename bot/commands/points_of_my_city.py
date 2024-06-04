import enum
import json
import operator
import os
from typing import Any

from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Window, DialogManager, StartMode, Dialog, DialogProtocol
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Next, Back, Cancel, Multiselect, Column, RequestLocation, Select
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory
from aiogram_dialog.widgets.text import Const, Format

from app import dp
from commands.state_classes import MainMenu, GetClosestPoint
from core.text import dialogs
from utils.utils import get_city, find_closest

intro_dialogs = dialogs['intro']
points_of_city_router = Router(name='points')

commands_dir = os.path.dirname(os.path.abspath(__file__))

# Open the 'points.json' file using its absolute pat

waste_select = Multiselect(
    Format("✓ {item[0]}"),
    Format("{item[0]}"),
    id="m_waste_types",
    item_id_getter=operator.itemgetter(1),
    items="waste_types"
)


class PointsActionKinds(str, enum.Enum):
    points_of_city = 'points_of_city'
    categories_chosen = 'categories_chosen'
    main_menu = 'main_menu'


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


async def on_city_selected(callback: CallbackQuery, widget: Any,
                              manager: DialogManager, item_id: str):
    manager.dialog_data['city'] = item_id

    await manager.next()


async def get_data(**kwargs):
    with open(os.path.join(commands_dir, 'points.json'), encoding='utf-8') as file:
        points = json.load(file)
        cities = points.keys()
    kwargs['dialog_manager'].dialog_data['points'] = points
    buttons = [(city, i) for i, city in enumerate(cities)]
    return {
        "buttons": buttons,
        "count": len(buttons),
    }


async def cords_sent(message: Message, dialog: DialogProtocol, manager: DialogManager):
    with open(os.path.join(commands_dir, 'points.json'), encoding='utf-8') as file:
        points = json.load(file)
    lat = message.location.latitude
    lon = message.location.longitude
    await message.delete()
    text = await find_closest(points, lat, lon)
    await message.answer(text)
    await manager.start(MainMenu.main, mode=StartMode.RESET_STACK)

dialog = Dialog(
    Window(
        Const("Отправьте свое местоположение"),
        RequestLocation(Const("Отправить геолокацию")),
        Cancel(Const("Главное меню🏠")),
        MessageInput(cords_sent),
        state=GetClosestPoint.getting_cords,
        markup_factory=ReplyKeyboardFactory()
    )
)

dp.include_router(dialog)
