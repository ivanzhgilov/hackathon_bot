import json
import os

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Back, Cancel
from aiogram_dialog.widgets.text import Const, Format
from transliterate import translit

from app import dp
from commands.state_classes import ArticleChoose
from core.text import dialogs

intro_dialogs = dialogs['intro']
article_router = Router(name='articles')

commands_dir = os.path.dirname(os.path.abspath(__file__))

# Open the 'points.json' file using its absolute path
with open(os.path.join(commands_dir, 'articles.json'), encoding='utf-8') as file:
    articles = json.load(file)
    article_names = articles.keys()
    article_ids = {}
    translit_back = {}
    for name in article_names:
        article_ids[name] = translit(name, language_code='ru', reversed=True).replace(" ", "").replace("'", "").lower()
        translit_back[article_ids[name]] = name


async def process_article_selection(callback: CallbackQuery, button: Button,
                                    manager: DialogManager):
    manager.dialog_data["text"] = articles[translit_back[callback.data]]
    await manager.next()


def generate_articles_keyboard():
    keyboard = []
    for name in article_names:
        keyboard.append(Button(Const(name), id=article_ids[name], on_click=process_article_selection))
    return keyboard


@dp.callback_query(F.data == "articles_start")
async def articles_restart(callback: CallbackQuery, manager: DialogManager):
    await manager.start(ArticleChoose.choosing_article)


async def articles_start(callback: CallbackQuery, button: Button,
                         manager: DialogManager):
    await manager.start(ArticleChoose.choosing_article)


dialog = Dialog(Window(Const('Выберете статью'),
                       *generate_articles_keyboard(),
                       Cancel(Const("Главное меню")), state=ArticleChoose.choosing_article),
                Window(Format('{dialog_data[text]}'),
                       Back(Const("Назад")),
                       Cancel(Const("Главное меню")), state=ArticleChoose.sending_article
                       ))

dp.include_router(dialog)
