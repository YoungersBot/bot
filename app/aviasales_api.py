import asyncio
import datetime
import os

from aiohttp import ClientSession
from typing import Optional, Union


class AviasalesAPI:
    TOKEN = os.environ.get("AVIASALES_TOKEN")
    TEST_CITIES = ["HRG", "VRA", "DXB"]

    @classmethod
    def get_default_dates(cls) -> tuple[str, str]:
        tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
        next_week_date = tomorrow_date + datetime.timedelta(days=8)
        tomorrow = tomorrow_date.isoformat()
        next_week = next_week_date.isoformat()
        return tomorrow, next_week

    @classmethod
    def _parse_response(cls, api_response: dict) -> dict:
        link = "https://www.aviasales.ru" + api_response["link"]
        return {
            "destination": api_response["destination"],
            "price": api_response["price"],
            "link": link,
        }

    @classmethod

    def create_default_request_url(
        cls, destination: str, limit: int = 1, departure_date: str = None, return_date: str = None
    ) -> str:
        tomorrow, next_week = cls.get_default_dates()
        if not departure_date:
            departure_date = tomorrow
        if not return_date:
            return_date = next_week
        return (
            f"https://api.travelpayouts.com/aviasales/v3/prices_for_dates?origin=MOW&destination={destination}"
            f"&departure_at={departure_date}&return_at={return_date}&unique=false&sorting=price&direct=false"
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
        tomorrow, next_week = cls.get_default_dates()
        request_url = AviasalesAPI.create_custom_request_url(departure_date=tomorrow, unique="true", limit=5)
        return await cls.get_one_city_price(request_url=request_url)

    @classmethod
    async def get_cities_prices(cls, cities_list: list, limit: int = 1) -> list[dict]:
        tasks = []
        for city in cities_list:
            request_url = cls.create_default_request_url(destination=city, limit=limit)
            tasks.append(asyncio.create_task(cls.get_one_city_price(request_url=request_url)))
        results = await asyncio.gather(*tasks)
        return results


if __name__ == "__main__":

    async def check_result_coroutine():
        task = asyncio.create_task(AviasalesAPI.get_five_cheapest())
        result = await task
        print(result)

    asyncio.run(check_result_coroutine())
