import json
import operator
import os
from typing import Any

from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, Window, DialogManager, DialogProtocol
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Cancel, Button, Back, Row, Column, Select
from aiogram_dialog.widgets.text import Const, Format
from transliterate import translit

from app import dp
from commands.state_classes import ArticleManage, ArticleEdit, AddArticle
from core.text import dialogs

commands_dir = os.path.dirname(os.path.abspath(__file__))

intro_dialogs = dialogs['intro']
managing_articles_router = Router(name='managing_articles')


async def edit_articles_start(callback, button, manager):
    await manager.start(ArticleEdit.choosing)


async def add_article_start(callback, button, manager):
    await manager.start(AddArticle.insert_name)


async def start_delete_article(callback, button, manager):
    await manager.next()


async def delete_article(callback, button, manager):
    articles = manager.dialog_data['articles']
    del articles[manager.dialog_data["key"]]
    with open(os.path.join(commands_dir, 'articles.json'), 'w', encoding='utf-8') as file:
        json.dump(articles, file, indent=4, ensure_ascii=False)
    await manager.next()


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
    manager.dialog_data['key'] = translit_back[item_id]
    await manager.next()


async def insert_name(message: Message, dialog: DialogProtocol, manager: DialogManager):
    manager.dialog_data['name'] = message.text
    await manager.next()


async def insert_text(message: Message, dialog: DialogProtocol, manager: DialogManager):
    manager.dialog_data['text'] = message.text
    await manager.next()


async def approve_article(callback: CallbackQuery, button: Button, manager: DialogManager):
    with open(os.path.join(commands_dir, 'articles.json'), encoding='utf-8') as file:
        articles = json.load(file)
    articles[manager.dialog_data['name']] = manager.dialog_data['text']
    with open(os.path.join(commands_dir, 'articles.json'), 'w', encoding='utf-8') as file:
        json.dump(articles, file, indent=4, ensure_ascii=False)
    await manager.next()


kbd = Select(
    Format("{item[0]}"),  # E.g `✓ Apple (1/4)`
    id="s_articles",
    item_id_getter=operator.itemgetter(1),
    # each item is a tuple with id on a first position
    items="titles",  # we will use items from window data at a key `fruits`
    on_click=on_article_selected,
)

start_dialog = Dialog(Window(Const('Выберите опцию'),
                             Button(Const('Удалить статью'), on_click=edit_articles_start,
                                    id='edit_articles_start'),
                             Button(Const('Добавить статью'), on_click=add_article_start, id='add_article_start'),
                             Cancel(Const("Меню администратора")), state=ArticleManage.start))

edit_article_dialog = Dialog(Window(Const('Выберите статью'),
                                    Column(kbd,
                                           Cancel(Const("Назад⬅️"))), state=ArticleEdit.choosing, getter=get_data),
                             Window(Format('{dialog_data[text]}'),
                                    Row(Back(Const("Назад ⬅️")),
                                        Button(Const('Удалить'), id='start_delete_article',
                                               on_click=start_delete_article)),
                                    Cancel(Const("Отменить")), state=ArticleEdit.managing),
                             Window(Const('Вы уверены?'),
                                    Button(Const('Удалить'), id='delete_article', on_click=delete_article),
                                    Cancel(Const("Отменить")), state=ArticleEdit.sure),
                             Window(Const("Успешно!"), Cancel(Const('В меню администратора')), state=ArticleEdit.result))

add_article_dialog = Dialog(Window(Const("Введите название статьи"), Cancel(Const("Отмена❌")),
                                   MessageInput(insert_name), state=AddArticle.insert_name),
                            Window(Const("Отправьте текст статьи"), Cancel(Const("Отмена❌")), Back(Const("Назад⬅️")),
                                   MessageInput(insert_text), state=AddArticle.insert_text),
                            Window(Format("""{dialog_data[name]}
{dialog_data[text]}"""), Button(Const("Подтвердить✅"), id="approve_article", on_click=approve_article),
                                   Cancel(Const('Отмена❌')), Back(Const("Назад ⬅️")), state=AddArticle.sure),
                            Window(Const("Успешно!"), Cancel(Const('К управлению статьями')), state=AddArticle.result))

dp.include_router(add_article_dialog)
dp.include_router(start_dialog)
dp.include_router(edit_article_dialog)
