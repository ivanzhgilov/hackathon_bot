from aiogram.fsm.state import StatesGroup, State


class MainMenu(StatesGroup):
    main = State()


class AdminMenu(StatesGroup):
    admin_password = State()
    admin_operations = State()


class GetClosestPoint(StatesGroup):
    getting_cords = State()


class ArticleChoose(StatesGroup):
    choosing_article = State()
    sending_article = State()


class ArticleSender(StatesGroup):
    sending_article = State()


class ArticleManage(StatesGroup):
    start = State()


class PointCreate(StatesGroup):
    title = State()
    description = State()
    address = State()
    phone_number = State()
    types_of_garbage = State()
    save = State()
    sure = State()
    notification = State()


class ArticleEdit(StatesGroup):
    choosing = State()
    managing = State()
    sure = State()
    result = State()


class PointDelete(StatesGroup):
    choosing = State()
    managing = State()
    sure = State()
    result = State()


class EcoPiggyBank(StatesGroup):
    show = State()


class AddArticle(StatesGroup):
    insert_name = State()
    insert_text = State()
    sure = State()
    result = State()


class CreatingNewsletter(StatesGroup):
    text_insert = State()
    media_insert = State()
    sure = State()
    result = State()


class AdminPointCreate(StatesGroup):
    title = State()
    description = State()
    address = State()
    phone_number = State()
    types_of_garbage = State()
    schedule = State()
    cords = State()
    save = State()
    sure = State()
    notification = State()


class AdminPointRequestsWatching(StatesGroup):
    points = State()


class AdminPointRequestsManaging(StatesGroup):
    cords = State()
    sure = State()
    save = State()


class GetStats(StatesGroup):
    days = State()
    stats = State()


class Links(StatesGroup):
    links = State()


class Nothing(StatesGroup):
    nothing = State()
