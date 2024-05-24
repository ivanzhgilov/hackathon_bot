from aiogram import Router
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Back, Cancel, Button
from aiogram_dialog.widgets.text import Const

from app import dp
from commands.state_classes import ArticleChoose
from core.text import dialogs

intro_dialogs = dialogs['intro']
managing_articles_router = Router(name='managing_articles')


async def edit_articles_start(callback, button, manager):
    pass


async def add_article_start(callback, button, manager):
    pass


dialog = Dialog(Window(Const('Выберите опцию'),
                       Button(Const('Редактировать статьи'), on_click=edit_articles_start, id='edit_articles_start'),
                       Button(Const('Добавить статью'), on_click=add_article_start, id='add_article_start'),
                       Cancel(Const("Назад")), state=ArticleChoose.choosing_article),
                Window(('{dialog_data[text]}'),
                       Back(Const("Назад")),
                       Cancel(Const("Главное меню")), state=ArticleChoose.sending_article
                       ))

dp.include_router(dialog)
