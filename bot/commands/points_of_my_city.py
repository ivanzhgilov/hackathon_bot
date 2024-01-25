from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery
from aiogram_dialog import Window, DialogManager, StartMode, Dialog, setup_dialogs
from aiogram_dialog.widgets.kbd import Checkbox
from aiogram_dialog.widgets.text import Const

from app import dp
from commands.intro import IntroAction, IntroActionKinds

points_of_city_router = Router(name='points')

categories = '''Категории выбраны✔️
Бумага📃
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

waste_types = []
for i, el in enumerate(categories.split('\n')):
    waste_types.append(Checkbox(Const(el),
                                Const(f"✅{el}"),
                                id=str(i),
                                default=True))


class GetClosestPoint(StatesGroup):
    main = State()


window = Window(
    Const("Hello, unknown person"),
    *waste_types,
    state=GetClosestPoint.main,
)

dialog = Dialog(window)
dp.include_router(dialog)
setup_dialogs(dp)

@points_of_city_router.callback_query(IntroAction.filter(F.action == IntroActionKinds.points_of_city))
async def func(query: CallbackQuery, state: FSMContext, bot: Bot, dialog_manager: DialogManager):
    await dialog_manager.start(GetClosestPoint.main, mode=StartMode.RESET_STACK)
