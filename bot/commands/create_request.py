from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, Dialog, Window, DialogProtocol, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Cancel, Button, Row, Next
from aiogram_dialog.widgets.text import Const, Format

from app import dp
from commands.state_classes import AccountMainPage, CreateRequest
from core.text import dialogs
from repositories.request_repository import request_repository
from repositories.user_repository import user_repository
from schemas.request import RequestScheme
from utils.database import db_async_session_manager

create_request_router = Router(name='create_request_router')

request_creating_text = dialogs['creating_request']


async def insert_question(message: Message, dialog: DialogProtocol, manager: DialogManager):
    #     TODO:запрос в иишку определяем текст сообщения
    manager.dialog_data['answer'] = 'Мощнейший ответ'
    manager.dialog_data['question'] = message.text
    await manager.next()


async def return_to_main_page_success(callback: CallbackQuery, button: Button,
                                      manager: DialogManager):
    async with db_async_session_manager() as session:
        user_id = (await user_repository.get_user_by_chat_id(session, callback.from_user.id)).id
        await request_repository.create_request(
            session, RequestScheme(
                question=manager.dialog_data['question'],
                system_id=None,
                answer=manager.dialog_data['answer'],
                user_id=user_id,
                status='successful'

            )
        )
    await manager.start(AccountMainPage.main, mode=StartMode.RESET_STACK)


async def return_to_main_page_unsuccess(callback: CallbackQuery, button: Button,
                                        manager: DialogManager):
    async with db_async_session_manager() as session:
        user_id = (await user_repository.get_user_by_chat_id(session, callback.from_user.id)).id
        await request_repository.create_request(
            session, RequestScheme(
                question=manager.dialog_data['question'],
                system_id=None,
                answer=manager.dialog_data['answer'],
                user_id=user_id,
                status='unsuccessful'

            )
        )
    await manager.start(AccountMainPage.main, mode=StartMode.RESET_STACK)


async def return_to_main_page_escalation(callback: CallbackQuery, button: Button,
                                         manager: DialogManager):
    async with db_async_session_manager() as session:
        user_id = (await user_repository.get_user_by_chat_id(session, callback.from_user.id)).id
        await request_repository.create_request(
            session, RequestScheme(
                question=manager.dialog_data['question'],
                system_id=None,
                answer=manager.dialog_data['answer'],
                user_id=user_id,
                status='escalation'

            )
        )
    await manager.start(AccountMainPage.main, mode=StartMode.RESET_STACK)


async def start_escolation(callback: CallbackQuery, button: Button,
                           manager: DialogManager):
    #     TODO: формируем сообщение с ссылкой на скит
    manager.dialog_data['escalation_message'] = 'крутое сообщение с ссылкой'


dialog = Dialog(Window(Const(request_creating_text['request_start']), Cancel(Const("Отмена❌")),
                       MessageInput(insert_question), state=CreateRequest.question),
                Window(Format('{dialog_data["answer"]}'),
                       Row(Button(Const('👍'), id='success', on_click=return_to_main_page_success),
                           Next(Const('👎'), on_click=start_escolation)),
                       Back(Const("Назад⬅️")),
                       Cancel(Const("Отмена❌")),
                       state=CreateRequest.answer),
                Window(Format('{dialog_data["escalation_message"]}'),
                       Row(Button(Const('👍'), id='escalation_success', on_click=return_to_main_page_escalation),
                           Button(Const('👎'), id='escalation_unsuccess', on_click=return_to_main_page_unsuccess)),
                       Back(Const("Назад⬅️")),
                       Cancel(Const("Отмена❌")), state=CreateRequest.escalation))

dp.include_router(dialog)
