import enum
import operator

from aiogram import Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Window, DialogManager, StartMode, Dialog, DialogProtocol
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Next, Back, Cancel, Button, Multiselect, Column
from aiogram_dialog.widgets.text import Const, Format

from app import dp
from commands.state_classes import MainMenu, GetClosestPoint
from core.text import dialogs

intro_dialogs = dialogs['intro']
points_of_city_router = Router(name='points')

waste_select = Multiselect(
    Format("✓ {item[0]}"),  # E.g `✓ Apple`
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


# checked_lst = []
#
#
# async def check_changed(event: ChatEvent, checkbox: ManagedCheckbox,
#                         manager: DialogManager):
#     global checked_lst
#     if checkbox.is_checked():
#         checked_lst.append(checkbox.)
#     else:
#         checked_lst.remove(checkbox.)


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
    long = message.location.longitude
    await message.delete()
    categories = waste_select.get_checked(manager)
    await manager.start(MainMenu.main, mode=StartMode.RESET_STACK)


# async def close(callback: CallbackQuery, button: Button,
#                 manager: DialogManager):
#     await manager.switch_to(MainMenu.main)


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
