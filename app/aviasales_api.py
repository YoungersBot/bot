import os
import asyncio
from typing import Optional, Union
from aiohttp import ClientSession


class AviasalesAPI:
    TOKEN = os.environ.get("AVIASALES_TOKEN")
    TEST_CITIES = ["TBS", "IST", "DXB"]

    @classmethod
    def create_request_link(cls, departure_date: str, return_date: str, destination: str, limit: str) -> str:
        return f'' \
               f'https://api.travelpayouts.com/aviasales/v3/prices_for_dates?origin=MOW&destination={destination}' \
               f'&departure_at={departure_date}&return_at={return_date}&unique=false&sorting=price&direct=false' \
               f'&cy=rub&limit={limit}&page=1&one_way=true&token=ce9a4e4345260ca6e88fc6f6337c662d'

    @classmethod
    def _parse_response(cls, api_response: dict) -> dict:
        link = "https://www.aviasales.ru" + api_response["link"]
        return {
            "destination": api_response["destination"],
            "price": api_response["price"],
            "link": link,
        }

    @classmethod
    async def get_one_city_price(cls, request_url: str) -> Optional[Union[dict, list]]:
        async with ClientSession() as session:

            async with session.get(request_url) as request:
                response = await request.json()
                response_data = response.get("data", None)
                if not response_data:
                    return None

                if len(response_data) == 1:
                    return cls._parse_response(response_data[0])

                results_list = []
                for obj in response_data:
                    result = cls._parse_response(obj)
                    results_list.append(result)
                print(results_list)
                return results_list

    @classmethod
    async def get_cities_prices(cls, cities_list: list = None) -> list[dict]:
        departure: str = "2023-11"  # datetime.date.today() отформатировать в строку
        return_date: str = "2023-12"  # departure + datetime.timedelta(days=30) прибавить один месяц к сегодня
        tasks = []
        for city in cities_list:
            url = cls.create_request_link(departure_date=departure, return_date=return_date, destination=city, limit=1
                                          )
            tasks.append(asyncio.create_task(cls.get_one_city_price(url)))
        results = await asyncio.gather(*tasks)
        print(results)
        return results


TEST_CITIES = ["TBS", "IST", "DXB"]
asyncio.run(AviasalesAPI.get_cities_prices(AviasalesAPI.TEST_CITIES))
asyncio.run(AviasalesAPI.get_one_city_price(AviasalesAPI.create_request_link('2023-11', '2023-12', 'DXB', '30')))
