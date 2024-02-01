from aiogram.utils.keyboard import InlineKeyboardBuilder

from commands.intro import intro_dialogs, IntroAction


def get_home_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text=intro_dialogs['start']['points_of_city_button'],
                   callback_data=IntroAction(action='points_of_city'))
    builder.button(text=intro_dialogs['start']['recycling_tips_button'],
                   callback_data=IntroAction(action='recycling_tips'))
    builder.button(text=intro_dialogs['start']['eco_lesson_button'], callback_data=IntroAction(action='eco_lesson'))
    builder.button(text=intro_dialogs['start']['eco_piggy_bank_button'],
                   callback_data=IntroAction(action='eco_piggy_bank'))
    builder.button(text=intro_dialogs['start']['useful_links_button'],
                   callback_data=IntroAction(action='useful_links'))
    builder.adjust(1, 1, 3)
    return builder