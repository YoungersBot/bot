import asyncio
import datetime
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)

from answers import answers
from aviasales_api import AviasalesAPI
from keyboards import KeyboardBuilder
from buttons import buttons
from destinations import dst, dct

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
async def command_help_handler(message: Message):
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
    distination_kb = InlineKeyboardMarkup(inline_keyboard=kb)
    await message.answer(text=answers.destination, reply_markup=distination_kb)
    await state.set_state(DestinationLimit.choosing_destination)


@dp.callback_query(
    DestinationLimit.choosing_destination,
    lambda callback: callback.data in ["LED", "AER", "KZN"],
)
async def choose_destination(callback: CallbackQuery, state: FSMContext):
    await state.update_data(destination=callback.data)
    await callback.message.answer(text=answers.limit)
    await state.set_state(DestinationLimit.choosing_limit)


@dp.message(DestinationLimit.choosing_limit, lambda message: int(message.text) < 10)
async def choose_limit(message: Message, state: FSMContext):
    await state.update_data(limit=message.text)
    user_data = await state.get_data()

    departure_date = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
    arrival_date = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
    link = AviasalesAPI.create_request_link(
        departure_date, arrival_date, user_data["destination"], user_data["limit"]
    )
    task_one_city = asyncio.create_task(AviasalesAPI.get_one_city_price(link))
    result = await task_one_city
    await message.answer(answers.cheapest)
    results_list: list
    if isinstance(result, dict):
        results_list = [result]
    if isinstance(result, list):
        results_list = result

    if result:
        for destination in results_list:
            ticket_url = destination["link"]
            reply_keyboard = KeyboardBuilder.ticket_reply_keyboard(ticket_url)
            destination_string = answers.you_can_fly.format(
                destination=dct[destination["destination"]], price=destination["price"]
            )
            await message.answer(destination_string, reply_markup=reply_keyboard)
    else:
        await message.answer(answers.no_tickets)
    await state.clear()


@dp.message(DestinationLimit.choosing_limit)
async def wrong_limit(message: Message):
    await message.answer(text=answers.wrong_limit)


@dp.message(lambda message: message.text == buttons.five_cheapest)
async def five_cheapest_handler(message: Message):
    task_get_five = asyncio.create_task(AviasalesAPI.get_five_cheapest())
    result = await task_get_five
    await message.answer(answers.cheapest)
    for destination in result:
        ticket_url = destination.get("link", "")
        reply_keyboard = KeyboardBuilder.ticket_reply_keyboard(ticket_url)
        answer_string = answers.you_can_fly.format(
            destination=destination["destination"], price=destination["price"]
        )
        await message.answer(answer_string, reply_markup=reply_keyboard)


@dp.callback_query(lambda callback: callback.data == buttons.subscribe)
async def subscribe(callback: CallbackQuery) -> None:
    await callback.message.answer(answers.subscribe)


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
