from typing import Any

from aiogram import Router
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.kbd import Cancel
from aiogram_dialog.widgets.text import Const, Format

from app import dp
from commands.state_classes import EcoPiggyBank
from core.text import dialogs
from utils.eco_bank_getter import text_top_schools

intro_dialogs = dialogs['intro']
eco_bank_router = Router(name='eco_bank')


async def on_dialog_start(start_data: Any, manager: DialogManager):
    manager.dialog_data['text'] = await text_top_schools()


dialog = Dialog(Window(Format('{dialog_data[text]}'),
                       Cancel(Const("Главное меню🏠")), state=EcoPiggyBank.show),
                on_start=on_dialog_start)

dp.include_router(dialog)
