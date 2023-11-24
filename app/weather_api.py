import asyncio
import os

from aiohttp import ClientSession


class WeatherApi:
    TOKEN = os.environ.get("OPEN_WEATHER_TOKEN")

    weather_icon = {
        "Clear": "\U00002600",
        "Clouds": "\U00002601",
        "Rain": "\U00002614",
        "Drizzle": "\U00002614",
        "Thunderstorm": "\U000026A1",
        "Snow": "\U0001F328",
        "Mist": "\U0001F32B",
    }

    @classmethod
    def _parse_response(cls, response: dict) -> dict:
        return (
            f"Погода в городе "
            f'{response["name"].capitalize()}:\n'
            f'{response["weather"][0]["description"].capitalize()}'
            f'{cls.weather_icon[response["weather"][0]["main"]]} \n'
            f'Температура: {response["main"]["temp"]}C°\n'
            f'Ощущается как: {response["main"]["feels_like"]}C°\n'
            f'Влажность: {response["main"]["humidity"]}%\n'
            f'Давление: {response["main"]["pressure"]}мм.рт.ст\n'
            f'Ветер: {response["wind"]["speed"]}м/с'
        )

    @classmethod
    async def get_weather_with_coor(cls, lat, lon):
        async with ClientSession() as session:
            async with session.get(
                f"https://api.openweathermap.org/data/2.5/weather?lat="
                f"{lat}&lon={lon}&appid={cls.TOKEN}&units=metric&lang=ru"
            ) as response:
                data = await response.json()
                if len(data) <= 2:
                    return None
                return cls._parse_response(data)

    @classmethod
    async def get_weather(cls, city):
        async with ClientSession() as session:
            async with session.get(
                f"https://api.openweathermap.org/data/2.5/weather?" f"q={city}&appid={cls.TOKEN}&units=metric&lang=ru"
            ) as response:
                data = await response.json()
                if len(data) <= 2:
                    return f"Для города {city} нет данных. Проверьте название или введите другой город."
                return cls._parse_response(data)


if __name__ == "__main__":
    city = input("Введите город: ")
    weather_data = asyncio.run(WeatherApi.get_weather(city))
    weather_data1 = asyncio.run(WeatherApi.get_weather_with_coor(62.266154, 74.478042))
    print(weather_data1)
    print(weather_data)
