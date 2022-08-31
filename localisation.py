from typing import Tuple, Optional, Any
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from aiogram import types
from config import I18N_DOMAIN, LOCALES_DIR
import database_sql as db


class ACLMiddleware(I18nMiddleware): # Создаем класс для middlware
    async def get_user_locale(self, action: str, args: Tuple[Any]) -> Optional[str]:
        user = types.User.get_current()
        lang = await db.get_user_language(str(user.id))
        return lang if lang is not None else user.locale # Перезаписываем функцию для определения языка перевода. Язык будет браться из БД, если он там есть


def setup_middleware(dp):
    i18n = ACLMiddleware(I18N_DOMAIN, LOCALES_DIR)
    dp.middleware.setup(i18n)
    return i18n
