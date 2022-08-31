from pathlib import Path


open_weather_token = 'YOUR OPENWEATHER API TOKEN HERE' # можно получить тут: https://home.openweathermap.org/api_keys
bot_token = 'YOUR TELEGRAM BOT TOKEN HERE' # токен бота можно получить в BotFather: https://t.me/BotFather

I18N_DOMAIN = 'weather_bot'
BASE_DIR = Path(__file__).parent
LOCALES_DIR = BASE_DIR / 'locales'
