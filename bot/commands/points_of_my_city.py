import enum
import json
import operator
import os

from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Window, DialogManager, StartMode, Dialog, DialogProtocol
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Next, Back, Cancel, Button, Multiselect, Column, RequestLocation
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
              'Металл⚙️',
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


async def points_of_city_start(callback: CallbackQuery, button: Button,
                               manager: DialogManager):
    await manager.start(GetClosestPoint.choosing_categories)


async def cords_sent(message: Message, dialog: DialogProtocol, manager: DialogManager):
    with open(os.path.join(commands_dir, 'points.json'), encoding='utf-8') as file:
        points = json.load(file)
    lat = message.location.latitude
    lon = message.location.longitude
    await message.delete()

    city = await get_city(lat, lon)
    if city == "городской округ Сургут":
        city = "Сургут"
    city_points = points.get(city)
    chosen = [categories[int(i)][:-1] for i in waste_select.get_checked(manager)]
    if city_points:
        lst = await find_closest(city_points, chosen, lat, lon)
        for text in lst:
            await message.answer(text)
    else:
        await message.answer("К сожалению в вашем населенном пункте нет точек удовлетворяющих данным параметрам")
    await manager.start(MainMenu.main, mode=StartMode.RESET_STACK)


dialog = Dialog(
    Window(
        Const("Выберите виды мусора для сортировки"),
        Next(Const("Категории выбраны✔️")),
        Column(waste_select),
        getter=get_data,
        state=GetClosestPoint.choosing_categories,
    ),
    Window(
        Const("Отправьте свои координаты"),
        RequestLocation(Const("Отправить геолокацию")),
        Back(Const("⬅Вернуться к выбору категорий")),
        Cancel(Const("Главное меню")),
        MessageInput(cords_sent),
        state=GetClosestPoint.getting_cords,
        markup_factory=ReplyKeyboardFactory()
    )
)

dp.include_router(dialog)
