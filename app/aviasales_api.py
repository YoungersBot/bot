import asyncio
import datetime
import os
from typing import Optional

from aiohttp import ClientSession


class AviasalesAPI:
    TOKEN = os.environ.get("AVIASALES_TOKEN")
    TEST_CITIES = ["HRG", "VRA", "DXB"]

    @classmethod
    def get_default_dates(cls) -> tuple[str]:
        this_date = datetime.date.today()

        if this_date.day < 20:
            return this_date.strftime("%Y-%m")
        if this_date.month == 12:
            next_month = 1
        else:
            next_month = this_date.month + 1

        next_month_date = this_date.replace(day=1, month=next_month)

        return next_month_date.strftime("%Y-%m")

    @classmethod
    def _parse_response(cls, api_response: dict) -> dict:
        link = "https://www.aviasales.ru" + api_response["link"]
        return {
            "destination": api_response["destination"],
            "price": api_response["price"],
            "link": link,
        }

    @classmethod
    def create_default_request_url(cls, destination: str, limit: int = 1, departure_date: str = None) -> str:
        month = cls.get_default_dates()
        if not departure_date:
            departure_date = month

        return (
            f"https://api.travelpayouts.com/aviasales/v3/prices_for_dates?origin=MOW&destination={destination}"
            f"&departure_at={departure_date}&unique=false&sorting=price&direct=false"
            f"&cy=rub&limit={limit}&page=1&one_way=true&token={cls.TOKEN}"
        )

    @classmethod
    def create_custom_request_url(
        cls,
        origin: str = "MOW",
        destination: str = "",
        departure_date: str = "",
        return_date: str = "",
        unique: str = "false",
        direct: str = "false",
        limit: int = 1,
        one_way: str = "true",
    ) -> str:
        print(
            f"https://api.travelpayouts.com/aviasales/v3/prices_for_dates?origin={origin}&destination={destination}"
            f"&departure_at={departure_date}&return_at={return_date}&unique={unique}&sorting=price&direct={direct}"
            f"&cy=rub&limit={limit}&page=1&one_way={one_way}&token={cls.TOKEN}"
        )
        return (
            f"https://api.travelpayouts.com/aviasales/v3/prices_for_dates?origin={origin}&destination={destination}"
            f"&departure_at={departure_date}&return_at={return_date}&unique={unique}&sorting=price&direct={direct}"
            f"&cy=rub&limit={limit}&page=1&one_way={one_way}&token={cls.TOKEN}"
        )

    @classmethod
    async def get_one_city_price(cls, request_url: str) -> Optional[list]:
        async with ClientSession() as session:
            async with session.get(request_url) as request:
                response = await request.json()
                if "error" in response:
                    print(response)
                response_data = response.get("data", None)
                if not response_data:
                    return None

                if len(response_data) == 1:
                    return [cls._parse_response(response_data[0])]

                results_list = []
                for obj in response_data:
                    result = cls._parse_response(obj)
                    results_list.append(result)
                return results_list

    @classmethod
    async def get_five_cheapest(cls) -> None:
        default_date = cls.get_default_dates()
        request_url = AviasalesAPI.create_custom_request_url(departure_date=default_date, unique="true", limit=5)
        return await cls.get_one_city_price(request_url=request_url)

    @classmethod
    async def get_cities_prices(cls, cities_list: list, limit: int = 1) -> list[dict]:
        tasks = []
        for city in cities_list:
            request_url = cls.create_default_request_url(destination=city, limit=limit)
            tasks.append(asyncio.create_task(cls.get_one_city_price(request_url=request_url)))
        results = await asyncio.gather(*tasks)
        return results

    @classmethod
    async def get_city_with_airport_code(cls, airport_code):
        request_url = (
            f"http://autocomplete.travelpayouts.com/places2?" f"term={airport_code}&" f"locale=ru&" f"types[]=city"
        )
        async with ClientSession() as session:
            async with session.get(request_url) as request:
                response = await request.json()
                city_dict = response[0]
                in_city = city_dict["cases"]["pr"]
                country = city_dict["country_cases"]["su"]
                airport = city_dict["main_airport_name"]
                return in_city, country, airport


if __name__ == "__main__":

    async def check_result_coroutine():
        task = asyncio.create_task(AviasalesAPI.get_five_cheapest())
        result = await task
        print(result)

    asyncio.run(check_result_coroutine())
