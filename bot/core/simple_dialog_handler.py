import abc
from typing import Any

from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, CallbackQuery


class DialogError(Exception):
    def __init__(self, display_message: str):
        self.display_message = display_message


class CancelError(DialogError):
    def __init__(self, display_message: str = None):
        self.display_message = display_message


class RetryError(DialogError):
    pass


class DialogHandlerMixin:
    dialog: 'SimpleDialog'
    step: 'DialogStep'


class HandlerMixin:
    async def handle(self, message: Message, state: FSMContext):
        pass


class DialogEntityMixin:
    dialog: 'SimpleDialog'

    def set_dialog(self, dialog: 'SimpleDialog'):
        self.dialog = dialog


class ExitHandler(HandlerMixin, DialogEntityMixin):
    pass


class DialogStep(DialogEntityMixin, abc.ABC):
    def __init__(self, state: State, text: str, buttons: list[str] = None):

        self.buttons = buttons
        self.text = text
        self.state = state

    async def _handle(self, message: Message, state: FSMContext):
        try:
            await self._handle(message, state)
            next_step = self.dialog._next_step(self)
            if next_step:
                await state.set_state(next_step.state)
        except CancelError as e:
            if e.display_message:
                await message.answer(e.display_message)
            await state.clear()
        except RetryError as e:
            await message.answer(e.display_message)

    @abc.abstractmethod
    async def handle(self, message: Message, state: FSMContext):
        pass


class DialogContextStep(DialogStep):
    """
    Шаг диалога, записывающий ответ пользователя в state (можно получить через collect_dialog_data)

    также позволяет валидировать ответ пользователя, переопределяя функцию validate_user_data
    """

    async def handle(self, message: Message, state: FSMContext):
        user_data = await self.validate_user_data(message, state)
        # noinspection PyProtectedMember
        key = self.dialog._build_dialog_data_key(self.state._state)

        await state.update_data(**{key: user_data})

    async def validate_user_data(self, message: Message, state: FSMContext)->Any:
        """

        :raises DialogError: при некорректных данных от пользователя
        """
        return message.text


class SimpleDialog:
    def __init__(self, name: str, router: Router, steps: list[DialogStep], on_exit: ExitHandler):
        if '-' in name:
            raise ValueError('dialog name can not containt "-" sign')
        self.on_exit = on_exit
        self.router = router
        if len(steps) <= 1:
            raise ValueError("Dialog expected more than 1 step")

        unfilled_text_steps = [i for i in steps[1:] if i.text is None]
        if any(unfilled_text_steps):
            failed = unfilled_text_steps[0]
            raise ValueError(f'step: {failed.state} should have filled "text" parameter')
        self.name = name
        self._steps = steps

        self.register_handlers()
        self.on_exit.set_dialog(self)

    def register_handlers(self):
        for step in self._steps:

            def build_handler(step: DialogStep):
                async def dialog_step(message: Message, state: FSMContext):
                    try:
                        await step.handle(message, state)
                        next_step = self._next_step(step)

                        if next_step:
                            if next_step.buttons:
                                keyboard = ReplyKeyboardMarkup(
                                    keyboard=[[KeyboardButton(text=i) for i in next_step.buttons]],
                                    one_time_keyboard=True,
                                    resize_keyboard=True
                                )
                            else:
                                keyboard = ReplyKeyboardRemove()

                            await message.answer(next_step.text, reply_markup=keyboard)

                            await state.set_state(next_step.state)
                        else:
                            await self.on_exit.handle(message, state)
                    except CancelError as e:
                        if e.display_message:
                            await message.answer(e.display_message)
                        await state.clear()
                    except RetryError as e:
                        await message.answer(e.display_message)

                # noinspection PyProtectedMember
                dialog_step.__name__ = f'{self.name}_{step.state._state}_dialog_step'

                return dialog_step

            step.set_dialog(self)
            handler = build_handler(step)
            self.router.message.register(handler, step.state)

    StateName = str

    def _build_dialog_data_key(self, key: str):
        return f'{self.name}-{key}'

    def _extract_orig_key(self, built_key: str):
        return '-'.join(built_key.split('-')[1:])

    async def _save_dialog_data(self, key: str, value: Any, state: FSMContext):
        await state.update_data(**{self._build_dialog_data_key(key): value})

    async def collect_dialog_data(self, state: FSMContext) -> dict[StateName, Any]:
        """
        Получает все введённые пользователем данные в формате {названиеШага: текст пользователя}
        """
        current_data = await state.get_data()
        cleared = {self._extract_orig_key(k): v for k, v in current_data.items() if k.startswith(self.name)}

        return cleared

    def _next_step(self, step: DialogStep) -> DialogStep | None:
        next_step = self._steps.index(step) + 1
        try:
            return self._steps[next_step]
        except IndexError:
            return None

    async def start_dialog(self, message: Message | CallbackQuery, state: FSMContext, bot: Bot):
        first_step = self._steps[0]

        await bot.send_message(message.from_user.id, first_step.text)
        await state.set_state(first_step.state)
