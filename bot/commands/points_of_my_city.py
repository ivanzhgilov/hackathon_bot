import enum
import operator

from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Window, DialogManager, StartMode, Dialog, setup_dialogs, DialogProtocol
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Next, Back, Cancel, Button, Multiselect, Column
from aiogram_dialog.widgets.text import Const, Format

from app import dp
from commands.intro import IntroAction, intro_dialogs
from utils.keyboards import get_home_keyboard

points_of_city_router = Router(name='points')


class PointsActionKinds(str, enum.Enum):
    points_of_city = 'points_of_city'
    categories_chosen = 'categories_chosen'
    main_menu = 'main_menu'


categories = '''Бумага📃
Пластик🔫
Стекло🍾
Металл⚙️
Одежда🎩
Лампочки💡
Крышечки🔴
Техника📱	
Батареки🪫
Шины🛞
Опасное☢
Другое'''


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
    waste_types = [(el, i) for i, el in enumerate(categories.split('\n'))]
    return {
        "waste_types": waste_types,
        "count": len(waste_types),
    }


class GetClosestPoint(StatesGroup):
    choosing_categories = State()
    getting_cords = State()


@points_of_city_router.callback_query(IntroAction.filter(F.action == PointsActionKinds.points_of_city))
async def func(query: CallbackQuery, state: FSMContext, bot: Bot, dialog_manager: DialogManager):
    await dialog_manager.start(GetClosestPoint.choosing_categories, mode=StartMode.RESET_STACK)


async def main_menu(callback: CallbackQuery, button: Button,
                    manager: DialogManager):
    await manager.done()
    builder = get_home_keyboard()
    await callback.message.answer(
        intro_dialogs['start']['usage_statistic'],

        reply_markup=builder.as_markup()

    )


@points_of_city_router.callback_query(IntroAction.filter(F.action == PointsActionKinds.main_menu))
async def func(query: CallbackQuery, state: FSMContext, bot: Bot, dialog_manager: DialogManager):
    builder = get_home_keyboard()
    await query.answer(
        intro_dialogs['start']['usage_statistic'],

        reply_markup=builder.as_markup()

    )


async def cords_sent(message: Message, dialog: DialogProtocol, manager: DialogManager):
    global checked_lst
    print(checked_lst)
    manager.dialog_data["lat"] = message.location.latitude
    manager.dialog_data["long"] = message.location.longitude
    await manager.done()


dialog = Dialog(
    Window(
        Const("Выберите виды мусора для сортировки"),
        Next(Const("Категории выбраны✔️")),
        Column(Multiselect(
            Format("✓ {item[0]}"),  # E.g `✓ Apple`
            Format("{item[0]}"),
            id="m_waste_types",
            item_id_getter=operator.itemgetter(1),
            items="waste_types"
        )),
        getter=get_data
        ,
        state=GetClosestPoint.choosing_categories,
    ),
    Window(
        Const("Отправьте свои координаты"),
        Back(Const("⬅Вернуться к выбору категорий")),
        Cancel(Const("Close"), on_click=main_menu),
        MessageInput(cords_sent),
        state=GetClosestPoint.getting_cords,
    )
)

dp.include_router(dialog)
setup_dialogs(dp)
