from config import *
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from localisation import setup_middleware


bot = Bot(token=bot_token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

i18n = setup_middleware(dp)
_ = i18n.gettext
