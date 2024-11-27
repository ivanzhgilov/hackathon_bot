import operator
from typing import Any

from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.kbd import Cancel, Select, Column, Button, Back
from aiogram_dialog.widgets.text import Const, Format

from app import dp
from commands.state_classes import MyRequests
from core.text import dialogs
from repositories.request_repository import request_repository
from utils.database import db_async_session_manager

my_requests_text = dialogs['my_requests']
my_requests_router = Router(name='my_requests_router')


async def get_data(**kwargs):
    manager = kwargs['dialog_manager']
    async with db_async_session_manager() as session:
        requests_obj = await request_repository.get_requests_by_user(session, manager.start_data['user_id'])
        requests = []
        manager.dialog_data['transition'] = []
        for i, request in enumerate(requests_obj):
            manager.dialog_data['transition'].append(request)
            requests.append((request.question[:15], i))
        return {
            "requests": requests,
            "count": len(requests),
        }


async def on_request_selected(callback: CallbackQuery, widget: Any,
                              manager: DialogManager, item_id: str):
    request = manager.dialog_data['transition'][int(item_id)]
    manager.dialog_data['request'] = vars(request)
    await manager.next()


async def start_adding(callback: CallbackQuery, button: Button,
                       manager: DialogManager):
    pass


async def start_answers(callback: CallbackQuery, button: Button,
                        manager: DialogManager):
    pass


async def start_deleting(callback: CallbackQuery, button: Button,
                         manager: DialogManager):
    pass


kbd = Select(
    Format("{item[0]}"),  # E.g `✓ Apple (1/4)`
    id="s_request_questions",
    item_id_getter=operator.itemgetter(1),
    # each item is a tuple with id on a first position
    items="requests",  # we will use items from window data at a key `fruits`
    on_click=on_request_selected,
)

dialog = Dialog(Window(Const(my_requests_text['main_page']),
                       Column(kbd,
                              Cancel(Const("Главное меню🏠"))), state=MyRequests.requests, getter=get_data),
                Window(Format('{dialog_data[request][question]}'),
                       Button(Const("Дополнить"), id='add', on_click=start_adding),
                       Button(Const("Ответы"), id='answers', on_click=start_answers),
                       Button(Const("Удалить заявку"), id='delete', on_click=start_deleting),
                       Back(Const("Назад⬅️")),
                       Cancel(Const("Главное меню🏠")), state=MyRequests.request_menu
                       )
                )

dp.include_router(dialog)
