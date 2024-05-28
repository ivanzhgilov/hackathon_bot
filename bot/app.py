from aiogram import Dispatcher, Bot
from aiogram.enums import ParseMode

from core.config import config

dp = Dispatcher()
bot = Bot(config.bot_token, parse_mode=ParseMode.HTML)
