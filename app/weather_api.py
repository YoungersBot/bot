import os
import asyncio
import datetime
import sys

from aiohttp import ClientSession
from pprint import pprint
from dotenv import load_dotenv

# Загрузка переменных среды из файла .env
load_dotenv()
token_weather = os.environ.get("OPEN_WEATHER_TOKEN")

# Словарь для соответствия кодов погоды эмодзи
code_to_smile = {
    "Clear": "Ясно \U00002600",
    "Clouds": "Облачно \U00002601",
    "Rain": "Дождь \U00002614",
    "Drizzle": "Дождь \U00002614",
    "Thunderstorm": "Гроза \U000026A1",
    "Snow": "Снег \U0001F328",
    "Mist": "Туман \U0001F32B"
}


# Асинхронная функция для получения информации о погоде
async def get_weather(city, token_weather):
    try:
        async with ClientSession() as session:
            async with session.get(
                    f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={token_weather}&units=metric"
            ) as response:
                data = await response.json()

        pprint(data)

        # Извлечение данных о погоде из JSON ответа
        city = data["name"]
        cur_weather = data["main"]["temp"]
        weather_description = data["weather"][0]["main"]

        # Преобразование кода погоды в соответствующий эмодзи
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = "???"

        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]

        # Вывод информации о погоде
        print(f"Погода на дату и время: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
              f"В городе: {city}\nТемпература: {cur_weather}C° {wd}\n"
              f"Влажность: {humidity}%\nДавление: {pressure} мм.рт.ст\nВетер: {wind} м/с")

    except Exception as ex:
        print(ex)
        print("Проверьте название города")


if __name__ == '__main__':
    city = input("Введите город: ")
    if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(get_weather(city, token_weather))
    else:
        asyncio.run(get_weather(city, token_weather))
