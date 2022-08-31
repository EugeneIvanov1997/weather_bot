from config import *
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from localisation import setup_middleware


bot = Bot(token=bot_token, parse_mode=types.ParseMode.HTML) # Создаем объект бота
dp = Dispatcher(bot) # Создаем диспатчер

i18n = setup_middleware(dp)
_ = i18n.gettext # Создаем метод для перевода строк
