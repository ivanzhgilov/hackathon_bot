import enum
import json
import operator
import os

from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Window, DialogManager, StartMode, Dialog, DialogProtocol
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Next, Back, Cancel, Button, Multiselect, Column
from aiogram_dialog.widgets.text import Const, Format

from app import dp
from commands.state_classes import MainMenu, GetClosestPoint
from core.text import dialogs
from utils.utils import get_city, find_matching_points, find_closest

intro_dialogs = dialogs['intro']
points_of_city_router = Router(name='points')

commands_dir = os.path.dirname(os.path.abspath(__file__))

# Open the 'points.json' file using its absolute path
with open(os.path.join(commands_dir, 'points.json'), encoding='utf-8') as file:
    points = json.load(file)


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
              'Металл⚙️',
              'Одежда🎩',
              'Лампочки💡',
              'Крышечки🔴',
              'Техника📱',
              'Батареки🪫',
              'Шины🛞',
              'Опасное☢',
              'Другое']


async def get_data(**kwargs):
    waste_types = [(el, i) for i, el in enumerate(categories)]
    return {
        "waste_types": waste_types,
        "count": len(waste_types),
    }


async def points_of_city_start(callback: CallbackQuery, button: Button,
                               manager: DialogManager):
    await manager.start(GetClosestPoint.choosing_categories)


async def cords_sent(message: Message, dialog: DialogProtocol, manager: DialogManager):
    lat = message.location.latitude
    lon = message.location.longitude
    await message.delete()

    city = points.get(await get_city(lat, lon))
    chosen = [i[1:-1] for i in waste_select.get_checked(manager)]
    if city:
        text = await find_closest(city, chosen)
        await message.answer(text)
    await manager.start(MainMenu.main, mode=StartMode.RESET_STACK)


dialog = Dialog(
    Window(
        Const("Выберите виды мусора для сортировки"),
        Next(Const("Категории выбраны✔️")),
        Column(waste_select),
        getter=get_data
        ,
        state=GetClosestPoint.choosing_categories,
    ),
    Window(
        Const("Отправьте свои координаты"),
        Back(Const("⬅Вернуться к выбору категорий")),
        Cancel(Const("Главное меню")),
        MessageInput(cords_sent),
        state=GetClosestPoint.getting_cords,
    )
)

dp.include_router(dialog)
