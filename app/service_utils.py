import asyncio
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Union

from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, Message

from aviasales_api import AviasalesAPI
from bot_utils.answers import answers
from bot_utils.keyboards import KeyboardBuilder
from database.db_api import DatabaseQueries
from find_airport import AirportFinder
from weather_api import WeatherApi


@dataclass
class CityResponse:
    city_code: str
    city_name: str
    country: str


@dataclass
class TicketRequestData:
    origin: str
    destination: str
    departure_date: str
    return_date: str
    limit: int = 5
    one_way: str = "false"


class SetCityUtils:
    @staticmethod
    async def set_city_start(message: Message) -> None:
        location_keyboard = KeyboardBuilder.location_reply_keyboard()
        await message.answer(answers.custom_ticket_select_city, reply_markup=location_keyboard)

    @staticmethod
    async def find_city_with_location(message: Message) -> CityResponse:
        user_coordinates = (message.location.latitude, message.location.longitude)
        airport_name, city_code = await asyncio.create_task(AirportFinder.find_nearest_airport(user_coordinates))
        response_city_info = asyncio.create_task(AviasalesAPI.get_city_names_with_code(city_code))
        in_city, country = await response_city_info

        return CityResponse(city_code=city_code, city_name=in_city, country=country)

    @staticmethod
    async def find_city_with_name(message: Message) -> Union[CityResponse, list, None]:
        cities = await asyncio.create_task(DatabaseQueries.find_airports_by_city_name(message.text))
        if not cities:
            return None

        if len(cities) > 1:
            return cities

        city_name = cities[0][0]
        city_code = cities[0][1]
        country = cities[0][2]
        return CityResponse(city_name=city_name, city_code=city_code, country=country)

    @staticmethod
    async def two_cities_reply(message: Message, cities_list: list) -> None:
        city_one = cities_list[0]
        city_two = cities_list[1]
        await message.answer(
            text=answers.two_cities,
            reply_markup=KeyboardBuilder.location_two_cities_keyboard(city_one, city_two),
        )


class SetDateUtils:
    @staticmethod
    async def set_date_start(message: Message) -> None:
        await message.answer(answers.custom_ticket_select_date)

    @staticmethod
    async def validate_date(message_text: str) -> bool:
        try:
            requested_date = datetime.strptime(message_text, "%Y-%m-%d")
            today = datetime.today()
            if requested_date < today:
                return False
            return True
        except ValueError:
            return False


class CustomTicketUtils:
    @classmethod
    def _check_ready_to_search(cls, state_data: dict) -> bool:
        if len(state_data) < 4:
            return False

        departure_data = state_data.get("departure_date")
        return_data = state_data.get("return_date")
        departure_date = datetime.strptime(departure_data, "%Y-%m-%d")
        return_date = datetime.strptime(return_data, "%Y-%m-%d")
        if return_date < departure_date:
            return False

        return True

    @classmethod
    def _prepare_data_for_state(cls, current_state: str, ticket_params: Union[CityResponse, str]) -> dict[str, str]:
        state_key = current_state.split("_", 1)[-1]
        data_to_update: dict = {}

        if "city" in current_state:
            data_to_update = {state_key[:-5]: ticket_params.city_code}
        if "date" in current_state:
            data_to_update = {state_key: ticket_params}
        return data_to_update

    @classmethod
    async def build_keyboard(cls, state: FSMContext, ticket_params: Union[CityResponse, str]) -> InlineKeyboardMarkup:
        current_state = await state.get_state()
        data_to_update = cls._prepare_data_for_state(current_state, ticket_params)
        await state.update_data(data_to_update)

        state_data = await state.get_data()
        logging.info("build custom kb %r", state_data)
        ready_to_search = cls._check_ready_to_search(state_data)

        if current_state == "CustomTicketState:select_destination_city":
            return KeyboardBuilder.custom_ticket_keyboard(
                destination_city=ticket_params.city_name, ready_to_search=ready_to_search
            )
        if current_state == "CustomTicketState:select_origin_city":
            return KeyboardBuilder.custom_ticket_keyboard(
                origin_city=ticket_params.city_name, ready_to_search=ready_to_search
            )
        if current_state == "CustomTicketState:select_departure_date":
            return KeyboardBuilder.custom_ticket_keyboard(departure_date=ticket_params, ready_to_search=ready_to_search)
        if current_state == "CustomTicketState:select_return_date":
            return KeyboardBuilder.custom_ticket_keyboard(return_date=ticket_params, ready_to_search=ready_to_search)


class TicketResponse:
    @staticmethod
    async def generate_tickets_messages(
        origin_code: str, tickets_result: list, message: Message, departure_date: str = "", return_date: str = ""
    ) -> None:
        for ticket in tickets_result:
            ticket_url = ticket.get("link", "")
            destination_city = await asyncio.create_task(DatabaseQueries.city_by_code(ticket["destination"]))
            if not destination_city:
                continue

            data = f"subscription {origin_code} {ticket['destination']} {departure_date} {return_date}"
            print(data)
            reply_keyboard = KeyboardBuilder.ticket_reply_keyboard(ticket_url, data)

            weather_city = asyncio.create_task(
                WeatherApi.get_weather_with_coor(destination_city[1], destination_city[2])
            )
            weather_result = await weather_city
            parsed_weather_result = WeatherApi.small_parse_response(weather_result) if weather_result else ""

            answer_text = answers.you_can_fly.format(
                destination=destination_city[0],
                price=ticket["price"],
                weather=parsed_weather_result,
            )
            await message.answer(answer_text, reply_markup=reply_keyboard)


if __name__ == "__main__":

    async def check_result_coroutine():
        state_d = {
            "origin": "TBS",  # {'city_code': 'TBS', 'city_name': 'Тбилиси', 'country': 'Грузия'},
            "destination": "MOW",  # {'city_code': 'MOW', 'city_name': 'Москва', 'country': 'Россия'},
            "departure_date": "2023-12-15",
            "return_date": "2023-12-30",
        }

        req = TicketRequestData(**state_d)
        url = AviasalesAPI.create_custom_request_url(**asdict(req))
        task = asyncio.create_task(AviasalesAPI.get_one_city_price(url))
        res = await task
        print(res)

    state_m = "origin_city"
    print(state_m[:-5])
