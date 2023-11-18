from typing import NamedTuple

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# class KeyInfo(NamedTuple):
#     text: str
#     callback_data: str
#
#
# def inline_keyboard(keys: list[KeyInfo] | list[list[KeyInfo]]) -> InlineKeyboardMarkup:
#     if len(keys) == 0:
#         return InlineKeyboardMarkup(inline_keyboard=[[]])
#     if any([type(i) == list for i in keys]):
#         values = [
#             [
#                 InlineKeyboardButton(text=key.text, callback_data=key.callback_data) for key in line]
#             for line in keys
#         ]
#     else:
#         values = [[InlineKeyboardButton(text=key.text, callback_data=key.callback_data) for key in keys]]
#     return InlineKeyboardMarkup(
#         inline_keyboard=values
#     )
