import asyncio
import logging
import os
import sys
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import weather_service
from aviasales_api import AviasalesAPI
from bot_utils.answers import answers
from bot_utils.buttons import buttons
from bot_utils.keyboards import KeyboardBuilder
from destinations import dct, dst
from weather_api import WeatherApi

TOKEN = os.environ.get("BOT_TOKEN")
dp = Dispatcher()

cities_where_the_season = [
    "AUH",
    "SSA",
    "BZC",
    "SCU",
    "TND",
    "UPB",
    "VRA",
    "PQC",
    "PHH",
    "CSJ",
    "CEB",
    "TAG",
    "KCI",
    "DXB",
    "SHJ",
    "FJR",
    "GOI",
    "PYX",
    "CNX",
    "HHQ",
    "TRV",
    "SYX",
    "REC",
]
cities = {
    "AUH": "Абу-Даби",
    "SSA": "Сальвадор",
    "BZC": "Бузиос",
    "SCU": "Сантьяго-де-Куба",
    "TND": "Тринидад",
    "UPB": "Гавана",
    "VRA": "Варадеро",
    "PQC": "Фукуок",
    "PHH": "Фантхьет",
    "CSJ": "Вунгтау",
    "CEB": "Себу",
    "TAG": "Бохоль",
    "KCI": "Корон",
    "DXB": "Дубай",
    "SHJ": "Шарджа",
    "FJR": "Фуджейра",
    "GOI": "Гоа",
    "PYX": "Паттайя",
    "CNX": "Ко Чанг",
    "HHQ": "Районг",
    "TRV": "Хуахин",
    "SYX": "остров Хайнань",
    "REC": "Ресифи",
}


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    main_keyboard = KeyboardBuilder.main_reply_keyboard()
    await message.answer(
        answers.start.format(username=message.from_user.username),
        reply_markup=main_keyboard,
    )


@dp.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    await message.answer(answers.help_command)


class DestinationLimit(StatesGroup):
    choosing_destination = State()
    choosing_limit = State()


@dp.message(StateFilter(None), Command("destination"))
async def destination_choose_city(message: Message, state: FSMContext):
    kb = [
        [
            InlineKeyboardButton(text=dst.led, callback_data="LED"),
            InlineKeyboardButton(text=dst.aer, callback_data="AER"),
            InlineKeyboardButton(text=dst.kzn, callback_data="KZN"),
        ],
    ]
    destination_kb = InlineKeyboardMarkup(inline_keyboard=kb)
    await message.answer(text=answers.destination, reply_markup=destination_kb)
    await state.set_state(DestinationLimit.choosing_destination)


@dp.callback_query(
    DestinationLimit.choosing_destination,
    lambda callback: callback.data in ["LED", "AER", "KZN"],
)
async def choose_destination(callback: CallbackQuery, state: FSMContext):
    await state.update_data(destination=callback.data)
    await callback.message.answer(text=answers.limit)
    await state.set_state(DestinationLimit.choosing_limit)


@dp.message(DestinationLimit.choosing_limit, lambda message: message.text.isdecimal() and int(message.text) < 10)
async def choose_limit(message: Message, state: FSMContext) -> Optional[Message]:
    await state.update_data(limit=message.text)
    user_data = await state.get_data()

    url = AviasalesAPI.create_default_request_url(user_data["destination"], user_data["limit"])
    task_one_city = asyncio.create_task(AviasalesAPI.get_one_city_price(request_url=url))
    result = await task_one_city
    await message.answer(answers.cheapest)

    if not result:
        await state.clear()
        return await message.answer(answers.no_tickets)

    for destination in result:
        ticket_url = destination["link"]
        reply_keyboard = KeyboardBuilder.ticket_reply_keyboard(ticket_url)
        destination_string = answers.you_can_fly.format(
            destination=dct[destination["destination"]], price=destination["price"]
        )
        await message.answer(destination_string, reply_markup=reply_keyboard)

    await state.clear()


@dp.message(DestinationLimit.choosing_limit)
async def wrong_limit(message: Message):
    await message.answer(text=answers.wrong_limit)


@dp.message(lambda message: message.text == buttons.five_cheapest)
async def five_cheapest_handler(message: Message) -> None:
    default_date = AviasalesAPI.get_default_dates()
    request_url = AviasalesAPI.create_custom_request_url(departure_date=default_date, unique="true", limit=5)
    task_get_five = asyncio.create_task(AviasalesAPI.get_one_city_price(request_url=request_url))
    result = await task_get_five
    await message.answer(answers.cheapest)

    for destination in result:
        ticket_url = destination.get("link", "")
        reply_keyboard = KeyboardBuilder.ticket_reply_keyboard(ticket_url)
        answer_string = answers.you_can_fly.format(destination=destination["destination"], price=destination["price"])
        await message.answer(answer_string, reply_markup=reply_keyboard)


@dp.callback_query(lambda callback: callback.data == buttons.subscribe)
async def subscribe(callback: CallbackQuery) -> None:
    await callback.message.answer(answers.subscribe)


@dp.message(Command("season"))
async def command_season(message: Message):
    kb = [
        [KeyboardButton(text=buttons.season)],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(answers.actions, reply_markup=keyboard)


#


@dp.message(lambda message: message.text == buttons.season)
async def season_handler(message: Message) -> None:
    ticket_list = []
    for city in cities_where_the_season:
        default_date = AviasalesAPI.get_default_dates()
        request_url = AviasalesAPI.create_custom_request_url(
            destination=city, departure_date=default_date, unique="true", limit=1
        )

        response = asyncio.create_task(AviasalesAPI.get_one_city_price(request_url=request_url))
        result = await response
        if result:
            ticket_list.append(result)
        if len(ticket_list) == 5:
            break

    await message.answer(answers.season)
    for ticket in ticket_list:
        destination = ticket[0]
        ticket_url = destination.get("link", "")
        weather_city = asyncio.create_task(WeatherApi.get_weather(cities[destination["destination"]]))
        result = await weather_city
        reply_keyboard = KeyboardBuilder.ticket_reply_keyboard(ticket_url)
        answer_string = answers.season_weather.format(
            destination=destination["destination"], price=destination["price"], result=result
        )

        await message.answer(answer_string, reply_markup=reply_keyboard)


@dp.message(Command("location"))
async def cmd_location_buttons(message: Message):
    builder = ReplyKeyboardBuilder()

    builder.row(
        KeyboardButton(text="Запросить геолокацию", request_location=True),
    )

    await message.answer(
        "Выберите действие:",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    dp.include_router(weather_service.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
