import asyncio

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from aviasales_api import AviasalesAPI
from bot_utils.answers import answers
from bot_utils.buttons import buttons
from bot_utils.keyboards import KeyboardBuilder
from find_airport import airports_finder
from weather_api import WeatherApi

router = Router()


class UserObject:
    user_coordinates: tuple = None


class WeatherState(StatesGroup):
    any_city_state = State()


@router.message(F.content_type == "location")
async def location(message: Message) -> None:
    UserObject.user_coordinates = (message.location.latitude, message.location.longitude)
    nearest_airport = airports_finder.find_nearest_airport(UserObject.user_coordinates)

    response_city_info = asyncio.create_task(AviasalesAPI.get_city_with_airport_code(nearest_airport))
    in_city, country, airport = await response_city_info
    await message.answer(answers.geolocation.format(in_city=in_city, country=country, airport=airport))


@router.message(lambda message: message.text == buttons.weather)
async def weather_in_your_city_handler(message: Message) -> None:
    kb = [
        [KeyboardButton(text=buttons.weather_in_your_city), KeyboardButton(text=buttons.weather_in_any_city)],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(answers.actions, reply_markup=keyboard)


@router.message(lambda message: message.text == buttons.weather_in_your_city)
async def your_city(message: Message):
    weather_your_city = asyncio.create_task(
        WeatherApi.get_weather_with_coor(UserObject.user_coordinates[0], UserObject.user_coordinates[1])
    )
    result = await weather_your_city
    await message.reply(answers.weather_in_your_city.format(result=result))


@router.message(lambda message: message.text == buttons.weather_in_any_city)
async def any_city(message: Message, state: FSMContext) -> None:
    await state.set_state(WeatherState.any_city_state)
    await message.answer(answers.weather)


@router.message(WeatherState.any_city_state)
async def weather_any_city(message: Message, state: FSMContext) -> None:
    weather_response = asyncio.create_task(WeatherApi.get_weather(message.text))
    result = await weather_response
    await message.reply(answers.weather_in_any_city.format(result=result))
    await state.clear()


@router.message()
async def echo_handler(message: Message) -> None:
    main_keyboard = KeyboardBuilder.main_reply_keyboard()
    try:
        await message.send_copy(chat_id=message.chat.id, reply_markup=main_keyboard)
    except TypeError:
        await message.answer("Nice try!")
