import asyncio
import datetime
import os

from aiohttp import ClientSession

token_weather = os.environ.get("OPEN_WEATHER_TOKEN")

code_to_smile = {
    "Clear": "Ясно \U00002600",
    "Clouds": "Облачно \U00002601",
    "Rain": "Дождь \U00002614",
    "Drizzle": "Дождь \U00002614",
    "Thunderstorm": "Гроза \U000026A1",
    "Snow": "Снег \U0001F328",
    "Mist": "Туман \U0001F32B",
}


async def get_weather(city, token_weather):
    try:
        async with ClientSession() as session:
            async with session.get(
                f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={token_weather}&units=metric"
            ) as response:
                data = await response.json()

        city = data["name"]
        cur_weather = data["main"]["temp"]
        weather_description = data["weather"][0]["main"]

        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = "Ошибка/Нет данных"

        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]

        weather_info = {
            "date_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "city": city,
            "temperature": f"{cur_weather}C° {wd}",
            "humidity": f"{humidity}%",
            "pressure": f"{pressure} мм.рт.ст",
            "wind_speed": f"{wind} м/с",
        }

        return weather_info

    except Exception as ex:
        print(ex)
        return None


if __name__ == "__main__":
    city = input("Введите город: ")
    weather_data = asyncio.run(get_weather(city, token_weather))

    if weather_data:
        print(
            f"Погода на дату и время: {weather_data['date_time']}\n"
            f"В городе: {weather_data['city']}\n"
            f"Температура: {weather_data['temperature']}\n"
            f"Влажность: {weather_data['humidity']}\n"
            f"Давление: {weather_data['pressure']}\n"
            f"Ветер: {weather_data['wind_speed']}"
        )
    else:
        print("Проверьте название города")
