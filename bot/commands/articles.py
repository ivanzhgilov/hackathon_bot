import json
import operator
import os
from typing import Any

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Back, Cancel, Select, Column
from aiogram_dialog.widgets.text import Const, Format
from transliterate import translit

from app import dp
from commands.state_classes import ArticleChoose
from core.text import dialogs

intro_dialogs = dialogs['intro']
article_router = Router(name='articles')

commands_dir = os.path.dirname(os.path.abspath(__file__))


# Open the 'points.json' file using its absolute path
# async def get_data(**kwargs):
#     with open(os.path.join(commands_dir, 'articles.json'), encoding='utf-8') as file:
#         articles = json.load(file)
#         article_names = articles.keys()
#         article_ids = {}
#         translit_back = {}
#         for name in article_names:
#             article_ids[name] = translit(name, language_code='ru', reversed=True).replace(" ", "").replace("'",
#                                                                                                            "").lower()
#             translit_back[article_ids[name]] = name
#     return {
#         "article_names": article_names,
#         "article_ids": article_ids,
#         "articles": articles,
#         "translit_back": translit_back
# }


# async def process_article_selection(callback: CallbackQuery, button: Button,
#                                     manager: DialogManager):
#     # manager.dialog_data["key"] = translit_back[callback.data]
#     # manager.dialog_data["text"] = articles[translit_back[callback.data]]
#     await manager.next()
@dp.callback_query(F.data == "articles_start")
async def articles_restart(callback: CallbackQuery, manager: DialogManager):
    await manager.start(ArticleChoose.choosing_article)


async def articles_start(callback: CallbackQuery, button: Button,
                         manager: DialogManager):
    await manager.start(ArticleChoose.choosing_article)


async def get_data(**kwargs):
    with open(os.path.join(commands_dir, 'articles.json'), encoding='utf-8') as file:
        articles = json.load(file)
        article_names = articles.keys()
        article_ids = {}
        translit_back = {}
        for name in article_names:
            article_ids[name] = translit(name, language_code='ru', reversed=True).replace(" ", "").replace("'",
                                                                                                           "").lower()
            translit_back[article_ids[name]] = name
    kwargs['dialog_manager'].dialog_data['translit'] = translit_back
    kwargs['dialog_manager'].dialog_data['articles'] = articles
    titles = [(name, article_ids[name]) for name in article_names]
    return {
        "titles": titles,
        "count": len(titles),
    }


async def on_article_selected(callback: CallbackQuery, widget: Any,
                              manager: DialogManager, item_id: str):
    translit_back = manager.dialog_data['translit']
    manager.dialog_data['text'] = manager.dialog_data['articles'][translit_back[item_id]]
    await manager.next()


kbd = Select(
    Format("{item[0]}"),  # E.g `✓ Apple (1/4)`
    id="s_articles",
    item_id_getter=operator.itemgetter(1),
    # each item is a tuple with id on a first position
    items="titles",  # we will use items from window data at a key `fruits`
    on_click=on_article_selected,
)

dialog = Dialog(Window(Const('Выберете статью'),
                       Column(kbd,
                       Cancel(Const("Главное меню"))), state=ArticleChoose.choosing_article, getter=get_data),
                Window(Format('{dialog_data[text]}'),
                       Back(Const("Назад")),
                       Cancel(Const("Главное меню")), state=ArticleChoose.sending_article
                       ))

dp.include_router(dialog)
