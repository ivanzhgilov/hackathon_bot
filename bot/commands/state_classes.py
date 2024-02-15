from aiogram.fsm.state import StatesGroup, State


class MainMenu(StatesGroup):
    main = State()


class GetClosestPoint(StatesGroup):
    choosing_categories = State()
    getting_cords = State()
