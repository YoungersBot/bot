import asyncio
import logging
import os
import sys
from typing import Optional

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, KeyboardButton

from aviasales_api import AviasalesAPI
from bot_utils.answers import answers
from bot_utils.buttons import buttons
from bot_utils.keyboards import KeyboardBuilder
from destinations import dct, dst
from find_airport import airports_finder

TOKEN = os.environ.get("BOT_TOKEN")
dp = Dispatcher()


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
    tomorrow, next_week = AviasalesAPI.get_default_dates()
    request_url = AviasalesAPI.create_custom_request_url(departure_date=tomorrow, unique="true", limit=5)
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


@dp.message(F.content_type == 'location')
async def location(message: Message) -> None:
    user_coords = (message.location.latitude, message.location.longitude)
    nearest_airport = airports_finder.find_nearest_airport(user_coords)

    response_city_info = asyncio.create_task(AviasalesAPI.get_city_with_airport_code(nearest_airport))
    in_city, country, airport = await response_city_info
    await message.answer(answers.geolocation.format(in_city=in_city, country=country, airport=airport))


@dp.message()
async def echo_handler(message: Message) -> None:
    main_keyboard = KeyboardBuilder.main_reply_keyboard()
    try:
        await message.send_copy(chat_id=message.chat.id, reply_markup=main_keyboard)
    except TypeError:
        await message.answer("Nice try!")


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
