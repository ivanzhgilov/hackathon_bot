from aiogram.fsm.state import StatesGroup, State


class MainMenu(StatesGroup):
    main = State()


class AdminMenu(StatesGroup):
    admin_password = State()
    admin_operations = State()


class GetClosestPoint(StatesGroup):
    choosing_categories = State()
    getting_cords = State()


class ArticleChoose(StatesGroup):
    choosing_article = State()
    sending_article = State()


class ArticleSender(StatesGroup):
    sending_article = State()


class Nothing(StatesGroup):
    nothing = State()
