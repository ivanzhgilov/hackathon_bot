import json
import operator
import os
from typing import Any

from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Cancel, Button, Back, Row, Column, Select
from aiogram_dialog.widgets.text import Const, Format

from app import dp
from commands.state_classes import PointDelete
from core.text import dialogs, get_point_text

commands_dir = os.path.dirname(os.path.abspath(__file__))

intro_dialogs = dialogs['intro']
delete_point_router = Router(name='delete_point')


async def start_delete_article(callback, button, manager):
    await manager.next()


async def delete_article(callback, button, manager):
    articles = manager.dialog_data['points']
    articles.remove(manager.dialog_data["delete"])
    with open(os.path.join(commands_dir, 'points.json'), 'w', encoding='utf-8') as file:
        json.dump(articles, file, indent=4, ensure_ascii=False)
    await manager.next()


async def get_data(**kwargs):
    with open(os.path.join(commands_dir, 'points.json'), encoding='utf-8') as file:
        articles = json.load(file)
        article_names = []
        for el in articles:
            article_names.append(el["address"])
    kwargs['dialog_manager'].dialog_data['points'] = articles
    titles = [(name, i) for i, name in enumerate(article_names)]
    return {
        "titles": titles,
        "count": len(titles),
    }


async def on_article_selected(callback: CallbackQuery, widget: Any,
                              manager: DialogManager, item_id: int):
    obj = manager.dialog_data['points'][int(item_id)]
    manager.dialog_data['delete'] = obj
    manager.dialog_data['text'] = await get_point_text(obj)
    await manager.next()


kbd = Select(
    Format("{item[0]}"),  # E.g `✓ Apple (1/4)`
    id="s_articles",
    item_id_getter=operator.itemgetter(1),
    # each item is a tuple with id on a first position
    items="titles",  # we will use items from window data at a key `fruits`
    on_click=on_article_selected,
)
delete_point_dialog = Dialog(Window(Const('Выберите точку'),
                                    Column(kbd,
                                           Cancel(Const("Назад⬅️"))), state=PointDelete.choosing, getter=get_data),
                             Window(Format('{dialog_data[text]}'),
                                    Row(Back(Const("Назад ⬅️")),
                                        Button(Const('Удалить'), id='start_delete_article',
                                               on_click=start_delete_article)),
                                    Cancel(Const("Отменить")), state=PointDelete.managing),
                             Window(Const('Вы уверены?'),
                                    Button(Const('Удалить'), id='delete_article', on_click=delete_article),
                                    Cancel(Const("Отменить")), state=PointDelete.sure),
                             Window(Const("Успешно!"), Cancel(Const('В меню администратора')),
                                    state=PointDelete.result))
dp.include_router(delete_point_dialog)
