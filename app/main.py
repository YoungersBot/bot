import os
import sys
import asyncio
import datetime
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, KeyboardButton, InlineKeyboardButton, \
    InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from answers import answers
from aviasales_api import AviasalesAPI
from buttons import btns
from destinations import dst, dct

TOKEN = os.environ.get("BOT_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    kb = [
        [
            KeyboardButton(text=btns.subscribes),
            KeyboardButton(text=btns.five_cheapest),
            KeyboardButton(text=btns.weather)
        ],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        one_time_keyboard=False,
    )

    await message.answer(answers.start.format(
        username=message.from_user.username),
        reply_markup=keyboard)


class DestinationLimit(StatesGroup):
    choosing_destination = State()
    choosing_limit = State()


@dp.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer("""Когда нибудь здесь будет описание работы бота
пока просто перечень команд: \n
/destination""")


@dp.message(StateFilter(None), Command('destination'))
async def destination_choose_city(message: Message, state: FSMContext):
    """
    Самые дешёвые билеты по направлению
    Первый этап. Выбор направления.
    """
    kb = [
        [
            InlineKeyboardButton(text=dst.led, callback_data='LED'),
            InlineKeyboardButton(text=dst.aer, callback_data='AER'),
            InlineKeyboardButton(text=dst.kzn, callback_data='KZN')
        ],
    ]
    distination_kb = InlineKeyboardMarkup(inline_keyboard=kb)
    await message.answer(
        text=answers.destination, reply_markup=distination_kb)
    await state.set_state(DestinationLimit.choosing_destination)


@dp.callback_query(DestinationLimit.choosing_destination, lambda callback:
callback.data in ['LED', 'AER', 'KZN'])
async def choose_destination(callback: CallbackQuery, state: FSMContext):
    """Второй этап. Выбор количества рейсов"""
    await state.update_data(destination=callback.data)
    await callback.message.answer(text=answers.limit)
    await state.set_state(DestinationLimit.choosing_limit)


@dp.message(DestinationLimit.choosing_limit, lambda message: int(message.text) < 10)
async def choose_limit(message: Message, state: FSMContext):
    """
    Получаем ответ от api и формируем сообщения с кнопками
    """
    await state.update_data(limit=message.text)
    user_data = await state.get_data()
    departure_date = datetime.date.today().isoformat()
    arrival_date = (
            datetime.date.today() + datetime.timedelta(days=30)).isoformat()

    link = AviasalesAPI.create_request_link(
        departure_date, arrival_date, user_data['destination'],
        user_data['limit']
    )
    task_one_city = asyncio.create_task(AviasalesAPI.get_one_city_price(link))
    result = await task_one_city

    await message.answer(answers.cheapest)
    for dest in result:
        kb = [
            [
                InlineKeyboardButton(text=btns.buy, url=dest['link']),
                InlineKeyboardButton(text=btns.subscribe,
                                     callback_data=btns.subscribe)
            ],
        ]
        inline_kb = InlineKeyboardMarkup(inline_keyboard=kb)

        dest_string = answers.you_can_fly.format(destination=dct[dest[
            'destination']], price=dest['price'])

        await message.answer(dest_string, reply_markup=inline_kb)

    await state.clear()


@dp.message(DestinationLimit.choosing_limit)
async def choose_limit(message: Message):
    await message.answer(text=answers.wrong_limit)


@dp.message(lambda message: message.text == btns.five_cheapest)
async def five_cheapest(message: Message):
    """
    Пять самых дешёвых билетов из города.
    Получаем ответ от api и формируем 5 сообщений с кнопками
    """
    task_get_five = asyncio.create_task(AviasalesAPI.get_five_cheapest())
    result = await task_get_five
    await message.answer(answers.cheapest)
    for dest in result:
        kb = [
            [
                InlineKeyboardButton(text=btns.buy, url=dest['link']),
                InlineKeyboardButton(text=btns.subscribe,
                                     callback_data=btns.subscribe)
            ],
        ]
        inline_kb = InlineKeyboardMarkup(inline_keyboard=kb)

        dest_string = answers.you_can_fly.format(destination=dest[
            'destination'], price=dest['price'])

        await message.answer(dest_string, reply_markup=inline_kb)


@dp.callback_query(lambda callback: callback.data == btns.subscribe)
async def subscribe(callback: CallbackQuery) -> None:
    """
    Позже будет запись подписки в базу, пока просто ответ

    """
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


from airport_finder import airports_finder


@dp.message(F.content_type == 'location')
async def location(message: Message) -> None:
    user_coords = (message.location.latitude, message.location.longitude)
    nearest_airport = airports_finder.find_nearest_airport(user_coords)
    print(nearest_airport
          )
    response_city_info = asyncio.create_task(AviasalesAPI.get_city_with_airport_code(nearest_airport))
    city_info = await response_city_info
    city_dict = city_info[0]
    await message.answer(answers.geolocation.format(in_city=city_dict['cases']['pr'],
                                                    country=city_dict['country_cases']['su'],
                                                    airport=city_dict['main_airport_name']))

@dp.message()
async def echo_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:
        # Send a copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
