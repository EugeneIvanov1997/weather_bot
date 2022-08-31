from config import *
from setup_all import bot, dp, _
from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.utils import executor
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ContentTypes, InlineKeyboardMarkup, InlineKeyboardButton
from weather_requests import make_weather_request, make_forecast_request
import database_sql as db


countries_dict = {}
langs_dict = {'ru': 'русский', 'en': 'English'}


@dp.message_handler(commands='start')
async def start_command(message: types.Message):
    user_lang = message.from_user.language_code if message.from_user.language_code in ('ru', 'en') else 'en'
    await db.add_user(user_id=message.from_user.id, user_lang=user_lang, user_units='metric')
    location_button = KeyboardButton(_('🏠 Погода в моем регионе'), request_location=True)
    languages_button = KeyboardButton(_('🌐 Выбор языка'))
    units_button = KeyboardButton(_('📐 Единицы'))
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).row(location_button).add(languages_button, units_button)
    await message.reply(_('Привет! Напиши мне название города, и я пришлю сводку погоды!'), reply_markup=keyboard)


@dp.message_handler(content_types=ContentTypes.LOCATION)
async def home_weather(message: types.Message):
    weather_24h_button = InlineKeyboardButton(text=_('📆 Прогноз на 24 ч'), callback_data='forecast_24h')
    weather_5d_button = InlineKeyboardButton(text=_('🗓 Прогноз на 5 дней'), callback_data='forecast_5d')
    weather_current_kb = InlineKeyboardMarkup(row_width=1).add(weather_24h_button, weather_5d_button)

    user_data = await db.get_user_data(message.from_user.id)
    user_lang = user_data[1]
    user_units = user_data[2]
    await message.reply(make_weather_request(
        url=f'https://api.openweathermap.org/data/2.5/weather' \
            f'?lat={message.location.latitude}' \
            f'&lon={message.location.longitude}' \
            f'&appid={open_weather_token}' \
            f'&units={user_units}' \
            f'&lang={user_lang}',
        units=user_units),
        reply_markup=weather_current_kb)


@dp.message_handler(Text(startswith='🌐'))
async def choose_lang(message: types.Message):
    lang_ru_button = InlineKeyboardButton(text='🇷🇺 RU', callback_data='changelang_ru')
    lang_en_button = InlineKeyboardButton(text='🇬🇧 EN', callback_data='changelang_en')
    changelang_kb = InlineKeyboardMarkup()
    changelang_kb.add(lang_ru_button, lang_en_button)
    await message.reply(_('Выберите язык:'), reply_markup=changelang_kb)


@dp.message_handler(Text(startswith='📐'))
async def choose_units(message: types.Message):
    units_std_button = InlineKeyboardButton(text=_('K, м/с, гПа'), callback_data='changeunits_standart')
    units_metric_button = InlineKeyboardButton(text=_('°C, м/с, мм рт ст'), callback_data='changeunits_metric')
    units_imper_button = InlineKeyboardButton(text=_('°F, миль/ч, гПа'), callback_data='changeunits_imperial')
    changeunits_kb = InlineKeyboardMarkup(row_width=1)
    changeunits_kb.add(units_std_button, units_metric_button, units_imper_button)
    await message.reply(_('Выберите единицы измерения:'), reply_markup=changeunits_kb)


@dp.message_handler()
async def get_weather(message: types.Message):
    user_data = await db.get_user_data(message.from_user.id)
    user_lang = user_data[1]
    user_units = user_data[2]
    text_for_message = make_weather_request(
        url=f'https://api.openweathermap.org/data/2.5/weather' \
            f'?q={message.text}' \
            f'&appid={open_weather_token}' \
            f'&units={user_units}' \
            f'&lang={user_lang}',
        units=user_units)
    if text_for_message == 'Проверьте название города!':
        await message.reply(text_for_message)
    else:
        weather_24h_button = InlineKeyboardButton(text=_('📆 Прогноз на 24 ч'), callback_data='forecast_24h')
        weather_5d_button = InlineKeyboardButton(text=_('🗓 Прогноз на 5 дней'), callback_data='forecast_5d')
        weather_current_kb = InlineKeyboardMarkup(row_width=1).add(weather_24h_button, weather_5d_button)

        await message.reply(text_for_message, reply_markup=weather_current_kb)


@dp.callback_query_handler(Text(startswith='changeunits_'))
async def changeunits(callback: types.CallbackQuery):
    new_units = callback.data.split('_')[1]
    await db.edit_units(user_id=callback.from_user.id, user_units=new_units)
    await callback.message.reply_to_message.reply(_('Вы изменили единицы измерения!'))
    await callback.answer()


@dp.callback_query_handler(Text(startswith='changelang_'))
async def changelang(callback: types.CallbackQuery):
    new_lang = callback.data.split('_')[1]
    await db.edit_language(user_id=callback.from_user.id, user_lang=new_lang)
    location_button = KeyboardButton(_('🏠 Погода в моем регионе', locale=new_lang), request_location=True)
    languages_button = KeyboardButton(_('🌐 Выбор языка', locale=new_lang))
    units_button = KeyboardButton(_('📐 Единицы', locale=new_lang))
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).row(location_button).add(languages_button,
                                                                                               units_button)
    await callback.message.reply_to_message.reply(_('Вы изменили язык на {0}!', locale=new_lang).format(langs_dict[new_lang]),
                                                  reply_markup=keyboard)
    await callback.answer()


@dp.callback_query_handler(Text(startswith='forecast_'))
async def forecast(callback: types.CallbackQuery):
    forecast_str = callback.data.split('_')[1]

    if forecast_str == 'current':
        weather_24h_button = InlineKeyboardButton(text=_('📆 Прогноз на 24 ч'), callback_data='forecast_24h')
        weather_5d_button = InlineKeyboardButton(text=_('🗓 Прогноз на 5 дней'), callback_data='forecast_5d')
        weather_current_kb = InlineKeyboardMarkup(row_width=1).add(weather_24h_button, weather_5d_button)

        user_data = await db.get_user_data(callback.from_user.id)
        user_lang = user_data[1]
        user_units = user_data[2]
        await callback.message.edit_text(make_weather_request(
            url=f'https://api.openweathermap.org/data/2.5/weather' \
                f'?q={callback.message.text.split(" ")[3].replace(",", "")}' \
                f'&appid={open_weather_token}' \
                f'&units={user_units}' \
                f'&lang={user_lang}',
            units=user_units))
        await callback.message.edit_reply_markup(reply_markup=weather_current_kb)
        await callback.answer()

    elif forecast_str == '24h':
        weather_current_button = InlineKeyboardButton(text=_('⏳ Погода сейчас'), callback_data='forecast_current')
        weather_5d_button = InlineKeyboardButton(text=_('🗓 Прогноз на 5 дней'), callback_data='forecast_5d')
        weather_24h_kb = InlineKeyboardMarkup(row_width=1).add(weather_current_button, weather_5d_button)

        user_data = await db.get_user_data(callback.from_user.id)
        user_lang = user_data[1]
        user_units = user_data[2]
        await callback.message.edit_text(make_forecast_request(
            url=f'https://api.openweathermap.org/data/2.5/forecast' \
                f'?q={callback.message.text.split(" ")[3].replace(",", "")}' \
                f'&appid={open_weather_token}' \
                f'&units={user_units}' \
                f'&lang={user_lang}',
            forecast_annotation=_('ближайшие 24 часа'),
            step=1,
            end=9,
            units=user_units
        ))
        await callback.message.edit_reply_markup(reply_markup=weather_24h_kb)
        await callback.answer()

    elif forecast_str == '5d':
        weather_current_button = InlineKeyboardButton(text=_('⏳ Погода сейчас'), callback_data='forecast_current')
        weather_24h_button = InlineKeyboardButton(text=_('📆 Прогноз на 24 ч'), callback_data='forecast_24h')
        weather_5d_kb = InlineKeyboardMarkup(row_width=1).add(weather_current_button, weather_24h_button)

        user_data = await db.get_user_data(callback.from_user.id)
        user_lang = user_data[1]
        user_units = user_data[2]
        await callback.message.edit_text(make_forecast_request(
            url=f'https://api.openweathermap.org/data/2.5/forecast' \
                f'?q={callback.message.text.split(" ")[3].replace(",", "")}' \
                f'&appid={open_weather_token}' \
                f'&units={user_units}' \
                f'&lang={user_lang}',
            forecast_annotation=_('ближайшие 5 дней'),
            step=4,
            end=40,
            day_night_emoji=True,
            units=user_units
        ))
        await callback.message.edit_reply_markup(reply_markup=weather_5d_kb)
        await callback.answer()


if __name__ == '__main__':
    db.sql_start()
    executor.start_polling(dp, skip_updates=True)
