import asyncio
import logging
import os
import random
import sys
from typing import Optional

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BotCommand, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

import weather_service
from aviasales_api import AviasalesAPI
from bot_utils.answers import answers
from bot_utils.buttons import buttons
from bot_utils.keyboards import KeyboardBuilder
from database.db_api import DatabaseQueries
from destinations import dct, dst
from find_airport import AirportFinder
from weather_api import WeatherApi

TOKEN = os.environ.get("BOT_TOKEN")
dp = Dispatcher()


class StartLocation(StatesGroup):
    choosing_location = State()
    choosing_city = State()


class FeedbackState(StatesGroup):
    waiting_for_feedback = State()


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start1", description="Начать заново"),
        BotCommand(command="feed", description="Обратная связь"),
        BotCommand(command="subscriptions", description="Подписки"),
        BotCommand(command="about", description="О боте"),
    ]
    await bot.set_my_commands(commands)


@dp.message(StateFilter(None), CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    location_keyboard = KeyboardBuilder.location_reply_keyboard()
    await message.answer(answers.start.format(username=message.from_user.username))
    await message.answer(answers.city_or_location, reply_markup=location_keyboard)

    await state.set_state(StartLocation.choosing_location)


@dp.message(StartLocation.choosing_location, F.content_type == "location")
async def location(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    username = message.from_user.username
    chat_id = message.chat.id

    user_coords = (message.location.latitude, message.location.longitude)
    airport_name, city_code = await asyncio.create_task(AirportFinder.find_nearest_airport(user_coords))

    response_city_info = asyncio.create_task(AviasalesAPI.get_city_names_with_code(city_code))
    in_city, country = await response_city_info

    count_airports = await asyncio.create_task(DatabaseQueries.count_airports_in_city_by_code(city_code))
    city_id = count_airports[0][3]
    await asyncio.create_task(DatabaseQueries.insert_new_user(user_id, username, chat_id, city_id))
    if len(count_airports) > 1:
        airports_list = []
        for name in count_airports:
            airports_list.append(name[0])
        airports_text = ", ".join(airports_list)
        await message.answer(
            answers.location_many.format(
                in_city=in_city,
                country=country,
                airport=airport_name,
                airports=airports_text,
            ),
            reply_markup=KeyboardBuilder.main_reply_keyboard(),
        )
        await state.clear()
    else:
        await message.answer(
            answers.location.format(in_city=in_city, country=country, airport=airport_name),
            reply_markup=KeyboardBuilder.main_reply_keyboard(),
        )
        await state.clear()


@dp.message(StartLocation.choosing_location, lambda message: message.text)
async def city_input(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    username = message.from_user.username
    chat_id = message.chat.id

    cities = await asyncio.create_task(DatabaseQueries.find_airports_by_city_name(message.text))
    if not cities:
        await message.answer(answers.city_with_airport_not_found)
        await message.answer(
            answers.city_or_location,
            reply_markup=KeyboardBuilder.location_reply_keyboard(),
        )
    elif len(cities) > 1:
        city_one = cities[0]
        city_two = cities[1]
        await state.update_data({city_one[1]: city_one[0], city_two[1]: city_two[0]})
        await message.answer(
            text=answers.two_cities,
            reply_markup=KeyboardBuilder.location_two_cities_keyboard(city_one, city_two),
        )
        await state.set_state(StartLocation.choosing_city)
    else:
        city_name = cities[0][0]
        city_code = cities[0][1]
        count_airports = await asyncio.create_task(DatabaseQueries.count_airports_in_city_by_code(city_code))
        city_id = count_airports[0][3]
        await asyncio.create_task(DatabaseQueries.insert_new_user(user_id, username, chat_id, city_id))
        if len(count_airports) > 1:
            airports_list = []
            for name in count_airports:
                airports_list.append(name[2])
            airports_text = ", ".join(airports_list)
            await asyncio.create_task(DatabaseQueries.insert_new_user(user_id, username, chat_id, city_id))
            await message.answer(
                answers.cities_found.format(city_name=city_name, airports_names=airports_text),
                reply_markup=KeyboardBuilder.main_reply_keyboard(),
            )
            await state.clear()
        else:
            airport_name = count_airports[0][2]
            await message.answer(
                answers.city_found.format(city_name=city_name, airport_name=airport_name),
                reply_markup=KeyboardBuilder.main_reply_keyboard(),
            )
            await state.clear()


@dp.callback_query(StartLocation.choosing_city)
async def city_selected_from_two(callback: CallbackQuery, state: FSMContext) -> None:
    user_id = callback.from_user.id
    username = callback.from_user.username
    chat_id = callback.message.chat.id

    city_code = callback.data
    data = await state.get_data()
    city_name = data[city_code]

    count_airports = await asyncio.create_task(DatabaseQueries.count_airports_in_city_by_code(city_code))
    city_id = count_airports[0][3]
    await asyncio.create_task(DatabaseQueries.insert_new_user(user_id, username, chat_id, city_id))

    if len(count_airports) > 1:
        airports_list = []
        for name in count_airports:
            airports_list.append(name[0])
        airports_text = ", ".join(airports_list)
        await callback.message.answer(
            answers.cities_found.format(city_name=city_name, airports_names=airports_text),
            reply_markup=KeyboardBuilder.main_reply_keyboard(),
        )
        await state.clear()
    else:
        airport_name = count_airports[0][2]
        await callback.message.answer(
            answers.city_found.format(city_name=city_name, airport_name=airport_name),
            reply_markup=KeyboardBuilder.main_reply_keyboard(),
        )
        await state.clear()


@dp.message(StartLocation.choosing_city)
async def airport_not_found(message: Message) -> None:
    await message.answer(answers.city_or_location, reply_markup=KeyboardBuilder.location_reply_keyboard())


@dp.message(Command("feed"))
async def start(message: Message):
    await message.answer(
        "Приветствую! Для того, чтобы оставить отзыв нажмите кнопку снизу",
        reply_markup=KeyboardBuilder.feedback_keyboards(),
    )


@dp.callback_query(F.data == "feedback")
async def show_feedback_message(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Ваш отзыв будет передан администратору. Введите пожалуйста сообщение: ")
    await state.set_state(FeedbackState.waiting_for_feedback)


@dp.message(FeedbackState.waiting_for_feedback)
async def handle_feedback_message(message: Message, bot: Bot, state: FSMContext):
    await bot.send_message(os.environ.get("ADMIN_ID"), f"Новый отзыв от {message.from_user.id}:\n{message.text}")
    await message.answer("Спасибо за отзыв! Ваше сообщение было передано администратору.")
    await state.clear()


@dp.callback_query(lambda c: c.data == "cancel_feedback")
async def cancel_feedback(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Ваше мнение важно для нас, будем рады вашим будущим отзывам!")
    await state.clear()


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


@dp.message(
    DestinationLimit.choosing_limit,
    lambda message: message.text.isdecimal() and int(message.text) < 10,
)
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


@dp.message(lambda message: message.text == buttons.subscriptions)
async def show_subscriptions(message: Message):
    user_id = message.chat.id
    subscriptions = await asyncio.create_task(DatabaseQueries.user_subscriptions(user_id))

    if subscriptions:
        await message.answer(answers.subscriptions)
        for subscription in subscriptions:
            origin = await asyncio.create_task(DatabaseQueries.city_by_code(subscription[0]))
            arrival = await asyncio.create_task(DatabaseQueries.city_by_code(subscription[1]))
            answer_text = answers.subscription.format(origin=origin[0], arrival=arrival[0])
            data = f"unsubscribe {subscription[0]} {subscription[1]}"
            await message.answer(answer_text, reply_markup=KeyboardBuilder.delete_subscription(data))
    else:
        await message.answer(answers.no_subscriptions)


@dp.callback_query(lambda callback: callback.data.split()[0] == "unsubscribe")
async def unsubscribe(callback: CallbackQuery) -> None:
    data = callback.data.split()
    await DatabaseQueries.unsubscription(callback.from_user.id, data[1], data[2])
    await callback.message.answer(answers.unsubscription)
    await show_subscriptions(callback.message)


@dp.message(lambda message: message.text == buttons.five_cheapest)
async def five_cheapest_handler(message: Message) -> None:
    users_city = await asyncio.create_task(DatabaseQueries.get_users_city(message.from_user.id))
    origin = users_city[3]
    default_date = AviasalesAPI.get_default_dates()
    request_url = AviasalesAPI.create_custom_request_url(
        origin=origin, departure_date=default_date, unique="true", limit=5
    )
    task_get_five = asyncio.create_task(AviasalesAPI.get_one_city_price(request_url=request_url))
    result = await task_get_five
    await message.answer(answers.cheapest)

    for destination in result:
        ticket_url = destination.get("link", "")
        destination_city = await asyncio.create_task(DatabaseQueries.city_by_code(destination["destination"]))
        data = f"subscription {origin} {destination['destination']}"
        reply_keyboard = KeyboardBuilder.ticket_reply_keyboard(ticket_url, data)

        weather_city = asyncio.create_task(WeatherApi.get_weather_with_coor(destination_city[1], destination_city[2]))
        result = await weather_city
        parsed_result = WeatherApi.small_parse_response(result)
        answer_string = answers.you_can_fly.format(
            destination=destination_city[0],
            price=destination["price"],
            weather=parsed_result,
        )

        await message.answer(answer_string, reply_markup=reply_keyboard)


@dp.callback_query(lambda callback: callback.data.split()[0] == "subscription")
async def subscribe(callback: CallbackQuery) -> None:
    data = callback.data.split()
    await DatabaseQueries.subscription(callback.from_user.id, data[1], data[2])
    await callback.message.answer(answers.subscribe)


@dp.message(Command("season"))
async def command_season(message: Message):
    await season_handler(message)


@dp.message(lambda message: message.text == buttons.season)
async def season_handler(message: Message) -> None:
    ticket_list = []
    users_city = await asyncio.create_task(DatabaseQueries.get_users_city(message.from_user.id))
    origin = users_city[3]
    cities_where_the_season = await asyncio.create_task(DatabaseQueries.cities_where_the_season())
    random_cities_where_season = random.sample(cities_where_the_season, len(cities_where_the_season))

    for city in random_cities_where_season:
        default_date = AviasalesAPI.get_default_dates()
        request_url = AviasalesAPI.create_custom_request_url(
            origin=origin,
            destination=city[0],
            departure_date=default_date,
            unique="true",
            limit=1,
        )

        response = asyncio.create_task(AviasalesAPI.get_one_city_price(request_url=request_url))
        result = await response
        if result:
            ticket = {
                "ticket_url": result[0].get("link", ""),
                "price": result[0].get("price", 0),
                "destination": city[1],
                "lat": city[2],
                "lon": city[3],
                "destination_code": city[0],
            }
            ticket_list.append(ticket)
        if len(ticket_list) == 5:
            break

    await message.answer(answers.season)
    for ticket in ticket_list:
        data = f"subscription {origin} {ticket['destination_code']}"
        weather_city = asyncio.create_task(WeatherApi.get_weather_with_coor(ticket["lat"], ticket["lon"]))
        result = await weather_city
        parsed_result = WeatherApi.small_parse_response(result)
        reply_keyboard = KeyboardBuilder.ticket_reply_keyboard(ticket["ticket_url"], data)
        answer_string = answers.season_weather.format(
            destination=ticket["destination"],
            price=ticket["price"],
            weather=parsed_result,
        )

        await message.answer(answer_string, reply_markup=reply_keyboard)


@dp.message(Command("cancel"))
@dp.message(F.text.casefold() == "cancel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info("Cancelling state %r", current_state)
    await state.clear()


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    dp.include_router(weather_service.router)
    await set_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
