import requests
from datetime import datetime, timedelta
from setup_all import _ # Весь текст, который должен быть локализован, будет обернут в эту функцию
from countries import countries_dict


code_to_smile = {
    'Clear': _('☀️ Ясно ☀️'),
    'Clouds': _('☁️ Облачно ☁️'),
    'Rain': _('🌧 Дождь 🌧'),
    'Drizzle': _('⛈ Ливень ⛈'),
    'Thunderstorm': _('🌩 Гроза 🌩'),
    'Snow': _('❄️ Снег ❄️'),
    'Mist': _('🌫 Туман 🌫')
} # Словарь для добавления эмодзи к описанию погоды

weekdays = {
    'Sunday': _('Воскресенье'),
    'Monday': _('Понедельник'),
    'Tuesday': _('Вторник'),
    'Wednesday': _('Среда'),
    'Thursday': _('Четверг'),
    'Friday': _('Пятница'),
    'Saturday': _('Суббота')
} # Словарь для добавления перевода к дням недели

degrees_dict = {
    'standart': 'K',
    'metric': '°C',
    'imperial': '°F'
} # Различные единицы измерения температуры

speed_dict = {
    'standart': _('м/с'),
    'metric': _('м/с'),
    'imperial': _('миль/ч')
} # Различные единицы измерения скорости ветра

pressure_dict = {
    'standart': _('гПа'),
    'metric': _('мм рт ст'),
    'imperial': _('гПа')
} # Различные единицы измерения давления


def wind_deg_to_dir(wind_deg: float):
    '''
    Эта функция необходима для перевода градусов, которые отдает сайт после запроса, в направление ветра
    '''
    
    dirs = (
    _('С ⬆️'), _('ССВ ↗️'), _('СВ ↗️'), _('ВСВ ↗️'), _('В ➡️'), _('ВЮВ ️↘️'), _('ЮВ ↘️'), _('ЮЮВ ↘️'), _('Ю ⬇️'),
    _('ЮЮЗ ↙️'), _('ЮЗ ↙️'), _('ЗЮЗ ↙️'), _('З ⬅️'), _('ЗСЗ ↖️'), _('СЗ ↖️'), _('ССЗ ↖️'))
    index = round(wind_deg / 22.5) if round(wind_deg / 22.5) < len(dirs) else 0
    return dirs[index]


def get_weather_data(weather_json: dict, units: str = 'metric'):
    '''
    Функция достает из результатов запроса погоды все необходимые данные, такие как время, температуру, описание, давление и т. д.
    '''
    
    result = {}
    result['weather_time'] = datetime.fromtimestamp(weather_json['dt'])
    result['temperature'] = weather_json['main']['temp']

    wd = weather_json['weather'][0]['main']
    if wd in code_to_smile:
        result['description'] = code_to_smile[wd]
    else:
        result['description'] = _('🌫 Мгла 🌫')

    result['feels_like'] = weather_json['main']['feels_like']
    result['humidity'] = weather_json['main']['humidity']
    result['pressure'] = weather_json['main']['pressure'] * 0.75 if units == 'metric' else weather_json['main']['pressure']
    result['wind_speed'] = weather_json['wind']['speed']
    result['wind_direction'] = wind_deg_to_dir(weather_json['wind']['deg'])

    return result


def make_weather_request(url, units: str = 'metric'):
    '''
    Делаем запрос текущей погоды
    '''
    
    result = ''
    try:
        r = requests.get(url=url)
        data = r.json()

        city = data['name'] # Из результата запроса достаем город
        country_code = data['sys']['country'] # Из результата запроса достаем код страны
        country_emoji = ''
        if country_code in countries_dict:
            country_name = countries_dict[country_code][0]
            country_emoji = countries_dict[country_code][1]
            if country_name == city:
                country_name = ''
        else:
            country_name = country_code # Переводим код страны в название страны и эмодзи флага

        coordinates = f"{float(data['coord']['lat']):.4f} {float(data['coord']['lon']):.4f}" # Из результата запроса достаем координаты

        time_shift = data['timezone']
        local_time = datetime.fromtimestamp(int(datetime.timestamp(datetime.utcnow())) + time_shift) # Вычисляем местное время

        weather_data = get_weather_data(data, units=units)

        description = weather_data['description']
        temperature = weather_data['temperature']
        feels_like = weather_data['feels_like']
        humidity = weather_data['humidity']
        pressure = weather_data['pressure']
        wind_speed = weather_data['wind_speed']
        wind_direction = weather_data['wind_direction']

        sunrise_time = datetime.fromtimestamp(data['sys']['sunrise'])
        sunset_time = datetime.fromtimestamp(data['sys']['sunset'])
        length_of_day = sunset_time - sunrise_time
        if sunrise_time.time() > sunset_time.time():
            sunrise_time, sunset_time = sunset_time - timedelta(days=1), sunrise_time # Вычисляем время заката и рассвета

        sunrise_formated = sunrise_time.strftime("%d.%m.%Y, %H:%M")
        if local_time < sunrise_time:
            time_to_sunrise = sunrise_time - local_time
            sunrise_formated = sunrise_formated + _('\n      (через ') + str(time_to_sunrise) + ')'

        sunset_formated = sunset_time.strftime("%d.%m.%Y, %H:%M")
        if local_time < sunset_time:
            time_to_sunset = sunset_time - local_time
            sunset_formated = sunset_formated + _('\n       (через ') + str(time_to_sunset) + ')' # Вычисляем, через сколько будет рассвет и закат

        result = _('<b>🗺 Погода в ') + city + ', ' + _(country_name) + '\xa0' + country_emoji + ':</b>\n' \
                                                       '\n' + \
                 _('🕰 Местное время: ') + local_time.strftime("%d.%m.%Y, %H:%M") + '\n' + \
                 _('🎯 Координаты: <code>') + coordinates + '</code>\n' + \
                 _('🌡 Температура ') + str(temperature) + ' ' + _(degrees_dict[units]) + ', ' + _(description) + '\n' + \
                 _('🤔 Ощущается как ') + str(feels_like) + ' ' + _(degrees_dict[units]) + '\n' + \
                 _('💧 Влажность ') + str(humidity) + ' %\n' + \
                 _('✈️️ Давление ') + str(pressure) + ' ' + _(pressure_dict[units]) + '\n' + \
                 _('💨 Ветер ') + str(wind_speed) + ' ' +  _(speed_dict[units]) + ', ' + wind_direction + '\n' + \
                 _('🌅 Рассвет ') + sunrise_formated + '\n' + \
                 _('🌆 Закат ') + sunset_formated + '\n' + \
                 _('🕓 Продолжительность дня ') + str(length_of_day) + '\n' \
                                                                       '\n' + \
                 _('        🧚‍♀️     Хорошего дня!     🧚‍♂️') # Формируем сообщение, которое бот будет отправлять пользователю
    except Exception as ex:
        print(ex)
        result = _('⚠️ Проверьте название города!') # Если во время выполнения кода возникнет исключение, просим пользователя проверить название города
    finally:
        return result


def make_forecast_request(url, forecast_annotation: str, step=1, end=40, day_night_emoji=False, units: str = 'metric'):
    '''
    Данная функция необходима для запроса прогноза погоды.
    Сайт отдает массив из 40 данных с разницей в 3 часа между соседними
    Параметр forecast_annotation будет добавлен в текст сообщения чтобы сформировать заголовок (см. комментарии ниже)
    Параметр step нужен для задания шага, с которым из массива с результатами будут браться данные (например, шагу в 3 часа соответствует step=1, а шагу в 12 часов - step=4)
    Параметр end определяет, до какого элемента массива будут браться данные (например, прогнозу на 24 ч соответствует end=8, а прогнозу на 5 дней - end=40)
    Параметр day_night_emoji определяет, будут ли в текст сообщения включены эмодзи, отвечающие за день/ночь
    '''
    
    result = ''
    try:
        r = requests.get(url=url)
        data = r.json()

        city = data['city']['name']
        country_code = data['city']['country']
        country_emoji = ''
        if country_code in countries_dict:
            country_name = countries_dict[country_code][0]
            country_emoji = countries_dict[country_code][1]
            if country_name == city:
                country_name = ''
        else:
            country_name = country_code

        result = _('<b>Прогноз погоды в ') + city + ', ' + _(country_name) + '\xa0' + country_emoji + '</b>\n' + \
                 _('<b>на ') + forecast_annotation + ':</b>\n' \ # Формируем текст, в котором будет написано, на какой промежуток времени этот прогноз
                                                     '\n' # Формируем основной заголовок

        sunrise_time = datetime.fromtimestamp(data['city']['sunrise']).time()
        sunset_time = datetime.fromtimestamp(data['city']['sunset']).time()

        for i in range(0, end, step): # Берем из результата запроса данные с определенным шагом
            weather_data = get_weather_data(data['list'][i], units=units)

            weather_time = weather_data['weather_time']
            description = weather_data['description']
            temperature = weather_data['temperature']
            feels_like = weather_data['feels_like']
            humidity = weather_data['humidity']
            pressure = weather_data['pressure']
            wind_speed = weather_data['wind_speed']
            wind_direction = weather_data['wind_direction']

            is_day = sunrise_time < weather_time.time() < sunset_time # Определяем, день или ночь, через время заката и рассвета

            result = result + '<i>' + _(weekdays[weather_time.strftime("%A")]) + ', ' + weather_time.strftime(
                "%d.%m.%Y, %H:%M") + '</i>'

            if day_night_emoji:
                if is_day:
                    result = result + ' 🌞'
                else:
                    result = result + ' 🌚' # Добавляем эмодзи

            result = result + _('<i>:</i>\n🌡 Температура ') + str(temperature) + ' ' + _(degrees_dict[units]) + ', ' + _(description) + '\n' + \
                     _('🤔 Ощущается как ') + str(feels_like) + ' ' + _(degrees_dict[units]) + '\n' + \
                     _('💧 Влажность ') + str(humidity) + ' %\n' + \
                     _('✈️️ Давление ') + str(pressure) + ' ' + _(pressure_dict[units]) + '\n' + \
                     _('💨 Ветер ') + str(wind_speed) + ' ' + _(speed_dict[units]) + ', ' + wind_direction + '\n\n'

        return result

    except Exception as ex:
        print(ex)
        result = _('⚠️ Проверьте название города!')
    finally:
        return result
