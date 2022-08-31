import sqlite3 as sq


def sql_start():
    global base, cur
    base = sq.connect('users.db')
    cur = base.cursor()
    if base:
        print('Database connected OK!')
    base.execute('CREATE TABLE IF NOT EXISTS users_data(user_id TEXT PRIMARY KEY, user_language TEXT, user_units TEXT)')
    base.commit()


async def add_user(user_id: str, user_lang: str, user_units: str):
    try:
        cur.execute('INSERT INTO users_data VALUES (?, ?, ?)', (user_id, user_lang, user_units))
        base.commit()
    except Exception as ex:
        print(f'{ex} when add new user')


async def edit_language(user_id: str, user_lang: str):
    cur.execute('UPDATE users_data SET user_language == ? WHERE user_id == ?', (user_lang, user_id))
    base.commit()


async def edit_units(user_id: str, user_units: str):
    cur.execute('UPDATE users_data SET user_units == ? WHERE user_id == ?', (user_units, user_id))
    base.commit()


async def get_user_language(user_id: str):
    try:
        lang = cur.execute('SELECT user_language FROM users_data WHERE user_id == ?', (user_id,)).fetchone()[0]
    except:
        lang = None
    return lang


async def get_user_data(user_id: str):
    """
    В data будет язык пользователя под индексом [1]
    и единицы измерения под индексом [2]
    :param user_id:
    :return:
    """

    data = cur.execute('SELECT * FROM users_data WHERE user_id == ?', (user_id,)).fetchall()[0]
    return data
