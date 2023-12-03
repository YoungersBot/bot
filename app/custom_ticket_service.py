import asyncio
from dataclasses import asdict

from aiogram import F, Router
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from aviasales_api import AviasalesAPI
from bot_utils.answers import answers
from bot_utils.buttons import buttons
from bot_utils.keyboards import KeyboardBuilder
from service_utils import CustomTicketUtils, SetCityUtils, SetDateUtils, TicketRequestData, TicketResponse

custom_ticket_router = Router()
CUSTOM_TICKET_MANAGE_ACTIONS: list = ["origin_city", "destination_city", "departure_date", "return_date"]


class CustomTicketState(StatesGroup):
    manage_ticket = State()
    select_origin_city = State()
    select_destination_city = State()
    select_departure_date = State()
    select_return_date = State()


@custom_ticket_router.message(lambda message: message.text == buttons.custom_ticket)
async def custom_ticket_choose_city(message: Message, state: FSMContext) -> None:
    keyboard = KeyboardBuilder.custom_ticket_keyboard()

    await message.answer(text=answers.custom_ticket_main, reply_markup=keyboard)
    await state.set_state(CustomTicketState.manage_ticket)


@custom_ticket_router.callback_query(
    CustomTicketState.manage_ticket,
    lambda callback: callback.data in CUSTOM_TICKET_MANAGE_ACTIONS,
)
async def manage_ticket(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.data == "origin_city":
        await state.set_state(CustomTicketState.select_origin_city)
        await SetCityUtils.set_city_start(callback.message)

    if callback.data == "destination_city":
        await state.set_state(CustomTicketState.select_destination_city)
        await SetCityUtils.set_city_start(callback.message)

    if callback.data == "departure_date":
        await state.set_state(CustomTicketState.select_departure_date)
        await SetDateUtils.set_date_start(callback.message)

    if callback.data == "return_date":
        await state.set_state(CustomTicketState.select_return_date)
        await SetDateUtils.set_date_start(callback.message)


@custom_ticket_router.message(
    or_f(CustomTicketState.select_origin_city, CustomTicketState.select_destination_city), F.content_type == "location"
)
async def set_city_with_location(message: Message, state: FSMContext) -> None:
    city_response = await SetCityUtils.find_city_with_location(message)

    selected_city_text = answers.custom_ticket_set_city.format(
        city=city_response.city_name, country=city_response.country
    )

    await message.answer(text=selected_city_text, reply_markup=ReplyKeyboardRemove())

    keyboard = await CustomTicketUtils.build_keyboard(state, city_response)
    await state.set_state(CustomTicketState.manage_ticket)
    await message.answer(text=answers.custom_ticket_main, reply_markup=keyboard)


@custom_ticket_router.message(
    or_f(CustomTicketState.select_origin_city, CustomTicketState.select_destination_city), lambda message: message.text
)
async def set_city_with_name(message: Message, state: FSMContext) -> None:
    city_response = await SetCityUtils.find_city_with_name(message)
    if city_response is None:
        await SetCityUtils.set_city_start(message)

    if isinstance(city_response, list):
        await SetCityUtils.two_cities_reply(message, city_response)

    selected_city_text = answers.custom_ticket_set_city.format(
        city=city_response.city_name, country=city_response.country
    )
    await message.answer(text=selected_city_text, reply_markup=ReplyKeyboardRemove())

    keyboard = await CustomTicketUtils.build_keyboard(state, city_response)
    await state.set_state(CustomTicketState.manage_ticket)
    await message.answer(text=answers.custom_ticket_main, reply_markup=keyboard)


@custom_ticket_router.message(
    or_f(CustomTicketState.select_departure_date, CustomTicketState.select_return_date),
    F.text.regexp(r"^\d{4}-\d{2}-\d{2}$"),
)
async def set_date(message: Message, state: FSMContext) -> None:
    validate_task = asyncio.create_task(SetDateUtils.validate_date(message.text))
    is_valid_date = await validate_task
    if not is_valid_date:
        await message.reply(text=answers.custom_ticket_wrong_date)
        await SetDateUtils.set_date_start(message)
    else:
        keyboard = await CustomTicketUtils.build_keyboard(state, message.text)
        await state.set_state(CustomTicketState.manage_ticket)
        await message.answer(text=answers.custom_ticket_main, reply_markup=keyboard)


@custom_ticket_router.callback_query(
    CustomTicketState.manage_ticket,
    lambda callback: callback.data == "confirm",
)
async def confirm_ticket(callback: CallbackQuery, state: FSMContext) -> None:
    state_data = await state.get_data()
    ticket_request_data = TicketRequestData(**state_data)
    await state.update_data({})
    await state.clear()
    await callback.message.answer(answers.custom_ticket_confirm, reply_markup=KeyboardBuilder.main_reply_keyboard())
    KeyboardBuilder.reset_custom_ticket_buttons()

    url = AviasalesAPI.create_custom_request_url(**asdict(ticket_request_data))
    tickets_task = asyncio.create_task(AviasalesAPI.get_one_city_price(url))
    tickets = await tickets_task
    if not tickets:
        await callback.message.answer(answers.no_tickets)
        return None

    await TicketResponse.generate_tickets_messages(
        origin_code=ticket_request_data.origin,
        tickets_result=tickets,
        message=callback.message,
        departure_date=ticket_request_data.departure_date,
        return_date=ticket_request_data.return_date,
    )


@custom_ticket_router.callback_query(
    CustomTicketState.manage_ticket,
    lambda callback: callback.data == "reject",
)
async def reject_ticket(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data({})
    await state.clear()
    KeyboardBuilder.reset_custom_ticket_buttons()
    await callback.message.answer(answers.custom_ticket_reject, reply_markup=KeyboardBuilder.main_reply_keyboard())
