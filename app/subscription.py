import asyncio

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from aviasales_api import AviasalesAPI
from bot_utils.answers import answers
from bot_utils.buttons import buttons
from bot_utils.keyboards import KeyboardBuilder
from database.db_api import DatabaseQueries
from weather_api import WeatherApi

router = Router()


@router.message(lambda message: message.text == buttons.subscriptions)
async def subscribe_handler(message: Message) -> None:

    await message.answer(',vlfg,lf')