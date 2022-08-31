import requests
from datetime import datetime, timedelta
from setup_all import _
from countries import countries_dict


code_to_smile = {
    'Clear': _('☀️ Ясно ☀️'),
    'Clouds': _('☁️ Облачно ☁️'),
    'Rain': _('🌧 Дождь 🌧'),
    'Drizzle': _('⛈ Ливень ⛈'),
    'Thunderstorm': _('🌩 Гроза 🌩'),
    'Snow': _('❄️ Снег ❄️'),
    'Mist': _('🌫 Туман 🌫')
}

weekdays = {
    'Sunday': _('Воскресенье'),
    'Monday': _('Понедельник'),
    'Tuesday': _('Вторник'),
    'Wednesday': _('Среда'),
    'Thursday': _('Четверг'),
    'Friday': _('Пятница'),
    'Saturday': _('Суббота')
}

degrees_dict = {
    'standart': 'K',
    'metric': '°C',
    'imperial': '°F'
}

speed_dict = {
    'standart': _('м/с'),
    'metric': _('м/с'),
    'imperial': _('миль/ч')
}

pressure_dict = {
    'standart': _('гПа'),
    'metric': _('мм рт ст'),
    'imperial': _('гПа')
}


def wind_deg_to_dir(wind_deg):
    dirs = (
    _('С ⬆️'), _('ССВ ↗️'), _('СВ ↗️'), _('ВСВ ↗️'), _('В ➡️'), _('ВЮВ ️↘️'), _('ЮВ ↘️'), _('ЮЮВ ↘️'), _('Ю ⬇️'),
    _('ЮЮЗ ↙️'), _('ЮЗ ↙️'), _('ЗЮЗ ↙️'), _('З ⬅️'), _('ЗСЗ ↖️'), _('СЗ ↖️'), _('ССЗ ↖️'))
    index = round(wind_deg / 22.5) if round(wind_deg / 22.5) < len(dirs) else 0
    return dirs[index]


def get_weather_data(weather_json: dict, units: str = 'metric'):
    result = {}
    result['weather_time'] = datetime.fromtimestamp(weather_json['dt'])
    result['temperature'] = weather_json['main']['temp']

    wd = weather_json['weather'][0]['main']
    if wd in code_to_smile:
        result['description'] = code_to_smile[wd]
    else:
        result['description'] = _('🌫 Плохая видимость 🌫')

    result['feels_like'] = weather_json['main']['feels_like']
    result['humidity'] = weather_json['main']['humidity']
    result['pressure'] = weather_json['main']['pressure'] * 0.75 if units == 'metric' else weather_json['main']['pressure']
    result['wind_speed'] = weather_json['wind']['speed']
    result['wind_direction'] = wind_deg_to_dir(weather_json['wind']['deg'])

    return result


def make_weather_request(url, units: str = 'metric'):
    result = ''
    try:
        r = requests.get(url=url)
        data = r.json()

        city = data['name']
        country_code = data['sys']['country']
        country_emoji = ''
        if country_code in countries_dict:
            country_name = countries_dict[country_code][0]
            country_emoji = countries_dict[country_code][1]
            if country_name == city:
                country_name = ''
        else:
            country_name = country_code

        coordinates = f"{data['coord']['lat']} {data['coord']['lon']}"

        time_shift = data['timezone']
        local_time = datetime.fromtimestamp(int(datetime.timestamp(datetime.utcnow())) + time_shift)

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
            sunrise_time, sunset_time = sunset_time - timedelta(days=1), sunrise_time

        sunrise_formated = sunrise_time.strftime("%d.%m.%Y, %H:%M")
        if local_time < sunrise_time:
            time_to_sunrise = sunrise_time - local_time
            sunrise_formated = sunrise_formated + _('\n      (через ') + str(time_to_sunrise) + ')'

        sunset_formated = sunset_time.strftime("%d.%m.%Y, %H:%M")
        if local_time < sunset_time:
            time_to_sunset = sunset_time - local_time
            sunset_formated = sunset_formated + _('\n       (через ') + str(time_to_sunset) + ')'

        result = _('<b>🗺 Погода в ') + city + ', ' + _(country_name) + '\xa0' + country_emoji + '</b>\n' \
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
                 _('        🧚‍♀️     Хорошего дня!     🧚‍♂️')
    except Exception as ex:
        print(ex)
        result = _('Проверьте название города!')
    finally:
        return result


def make_forecast_request(url, forecast_annotation: str, step=1, end=40, day_night_emoji=False, units: str = 'metric'):
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
                 _('<b>на ') + forecast_annotation + ':</b>\n' \
                                                     '\n'

        sunrise_time = datetime.fromtimestamp(data['city']['sunrise']).time()
        sunset_time = datetime.fromtimestamp(data['city']['sunset']).time()

        for i in range(0, end, step):
            weather_data = get_weather_data(data['list'][i], units=units)

            weather_time = weather_data['weather_time']
            description = weather_data['description']
            temperature = weather_data['temperature']
            feels_like = weather_data['feels_like']
            humidity = weather_data['humidity']
            pressure = weather_data['pressure']
            wind_speed = weather_data['wind_speed']
            wind_direction = weather_data['wind_direction']

            is_day = sunrise_time < weather_time.time() < sunset_time

            result = result + '<i>' + _(weekdays[weather_time.strftime("%A")]) + ', ' + weather_time.strftime(
                "%d.%m.%Y, %H:%M") + '</i>'

            if day_night_emoji:
                if is_day:
                    result = result + ' 🌞'
                else:
                    result = result + ' 🌚'

            result = result + _('<i>:</i>\n🌡 Температура ') + str(temperature) + ' ' + _(degrees_dict[units]) + ', ' + _(description) + '\n' + \
                     _('🤔 Ощущается как ') + str(feels_like) + ' ' + _(degrees_dict[units]) + '\n' + \
                     _('💧 Влажность ') + str(humidity) + ' %\n' + \
                     _('✈️️ Давление ') + str(pressure) + ' ' + _(pressure_dict[units]) + '\n' + \
                     _('💨 Ветер ') + str(wind_speed) + ' ' + _(speed_dict[units]) + ', ' + wind_direction + '\n\n'

        return result

    except Exception as ex:
        print(ex)
        result = _('Проверьте название города!')
    finally:
        return result
