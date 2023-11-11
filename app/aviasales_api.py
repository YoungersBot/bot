import datetime
import os
import asyncio
from typing import Optional, Union
from aiohttp import ClientSession


class AviasalesAPI:
    TOKEN = os.environ.get("AVIASALES_TOKEN")

    @classmethod
    def create_request_link(
        cls, departure_date: str, return_date: str, destination: str, limit: str
    ) -> str:
        return (
            f""
            f"https://api.travelpayouts.com/aviasales/v3/prices_for_dates?origin=MOW&destination={destination}"
            f"&departure_at={departure_date}&return_at={return_date}&unique=false&sorting=price&direct=false"
            f"&cy=rub&limit={limit}&page=1&one_way=true&token={cls.TOKEN}"
        )

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
                # print(results_list)
                return results_list

    @classmethod
    async def get_five_cheapest(cls) -> Optional[Union[dict, list]]:
        async with ClientSession() as session:
            tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
            departure_date = tomorrow_date.isoformat()

            request_url = (
                f"https://api.travelpayouts.com/aviasales/v3/"
                f"prices_for_dates?"
                f"origin=MOW&"
                f"departure_at={departure_date}&"
                f"unique=true&sorting=price&direct=false&&cy=rub"
                f"&limit=5&&one_way=true&"
                f"token={cls.TOKEN}"
            )

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
                return results_list

    @classmethod
    async def get_cities_prices(cls, cities_list: list = None) -> list[dict]:
        departure: str = "2023-11"
        return_date: str = "2023-12"
        tasks = []
        for city in cities_list:
            url = cls.create_request_link(
                departure_date=departure,
                return_date=return_date,
                destination=city,
                limit="1",
            )
            tasks.append(asyncio.create_task(cls.get_one_city_price(url)))
        results = await asyncio.gather(*tasks)
        return results


if __name__ == "__main__":
    TEST_CITIES = ["TBS", "IST", "DXB"]
    asyncio.run(AviasalesAPI.get_five_cheapest())
    # asyncio.run(AviasalesAPI.get_cities_prices(TEST_CITIES))
    # asyncio.run(AviasalesAPI.get_one_city_price(AviasalesAPI.create_request_link('2023-11', '2023-12', 'DXB', '30')))
