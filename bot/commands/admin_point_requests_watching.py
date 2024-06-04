import json
import os

from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Window, Dialog, DialogManager, StartMode, DialogProtocol
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Back
from aiogram_dialog.widgets.text import Const, Format
from sqlalchemy import select

from app import dp
from commands.state_classes import AdminPointRequestsWatching, AdminPointRequestsManaging, AdminMenu
from core.text import get_point_request_text
from models import PointRequest
from utils.database import db_async_session_manager
from utils.utils import get_city

points_managing_router = Router(name='points_managing_router')
commands_dir = os.path.dirname(os.path.abspath(__file__))


async def window1_get_data(**kwargs):
    async with db_async_session_manager() as session:
        request = await session.execute(select(PointRequest))
        request = request.scalars().one_or_none()
    if request:
        text = await get_point_request_text(request)
        kwargs['dialog_manager'].dialog_data["point"] = request
        kwargs['dialog_manager'].dialog_data["text"] = text
    else:
        text = "Запросов пока нет"

    return {
        "text": text
    }


async def approve(callback: CallbackQuery, button: Button,
                  manager: DialogManager):
    await manager.start(AdminPointRequestsManaging.cords, data=manager.dialog_data)


async def admin_menu(callback: CallbackQuery, button: Button,
                     manager: DialogManager):
    await manager.start(AdminMenu.admin_operations, mode=StartMode.RESET_STACK)


async def decline(callback: CallbackQuery, button: Button,
                  manager: DialogManager):
    point = manager.dialog_data["point"]
    async with db_async_session_manager() as session:
        async with session.begin():
            try:
                # Assuming that 'point' is an instance of PointRequest
                if point:
                    await session.delete(point)
                    manager.dialog_data["point"] = None
                    await callback.answer("Запрос отклонен успешно!", show_alert=True)
                else:
                    await callback.answer("Point request not found.", show_alert=True)
            except Exception as e:
                await callback.answer(f"An error occurred: {str(e)}", show_alert=True)
                raise
    await manager.start(AdminPointRequestsWatching.points)


async def insert_cords(message: Message, dialog: DialogProtocol, manager: DialogManager):
    point = manager.start_data["point"]
    manager.dialog_data["title"] = point.title
    manager.dialog_data["description"] = point.description
    manager.dialog_data["address"] = point.address
    manager.dialog_data["phone_number"] = point.phone_number
    manager.dialog_data["types_of_garbage"] = point.types_of_garbage.split(",")

    lst = message.text.replace(" ", "").split(',')
    manager.dialog_data["coordinates"] = {}
    manager.dialog_data["coordinates"]['lat'] = float(lst[0])
    manager.dialog_data["coordinates"]['lon'] = float(lst[1])
    await manager.next()


async def save(callback: CallbackQuery, button: Button, manager: DialogManager):
    with open(os.path.join(commands_dir, 'points.json'), encoding='utf-8') as file:
        points = json.load(file)
    city = await get_city(manager.dialog_data["coordinates"]["lat"], manager.dialog_data["coordinates"]["lon"])
    if city == "городской округ Сургут":
        city = "Сургут"
    if points.get(city):
        points[city].append(manager.dialog_data)
    else:
        points[city] = []
        points[city].append(manager.dialog_data)
    with open(os.path.join(commands_dir, 'points.json'), "w", encoding='utf-8') as file:
        json.dump(points, file, indent=4, ensure_ascii=False)
    point = manager.start_data["point"]
    async with db_async_session_manager() as session:
        async with session.begin():
            try:
                # Assuming that 'point' is an instance of PointRequest
                if point:
                    await session.delete(point)
                    manager.dialog_data["point"] = None
                    await callback.answer("Запрос отклонен успешно!", show_alert=True)
                else:
                    await callback.answer("Point request not found.", show_alert=True)
            except Exception as e:
                await callback.answer(f"An error occurred: {str(e)}", show_alert=True)
                raise
    await manager.next()


dialog = Dialog(
    Window(Format("{text}"),
           Button(Const("Дополнить информацию о точке и одобрить"), id="admin_approve_point", on_click=approve),
           Button(Const("Отклонить"), id="admin_decline_point", on_click=decline),
           Button(Const("Меню администратора"), id="admin_menu", on_click=admin_menu),
           state=AdminPointRequestsWatching.points,
           getter=window1_get_data))

subdialog = Dialog(Window(Format(
    "{start_data[text]}\nОтправьте координаты вида <b>55.756265512853076,37.542354827164544</b> (можете взять их с сайта https://snipp.ru/tools/address-coord"),
    Cancel(Const("Назад⬅️")), MessageInput(insert_cords), state=AdminPointRequestsManaging.cords),
    Window(Format("""{dialog_data[title]}

{dialog_data[description]}

{dialog_data[address]}

Принимается: {dialog_data[types_of_garbage]}

Номер телефона: {dialog_data[phone_number]}"""), Cancel(Const("❌")), Back(Const("Назад⬅️")),
           Button(Const("Подтвердить✅"), id="approve", on_click=save), state=AdminPointRequestsManaging.sure),
    Window(Const('Точка добавлена успешно!'), Cancel(Const("К другим запросам")),
           state=AdminPointRequestsManaging.save)
)

dp.include_router(dialog)
dp.include_router(subdialog)
