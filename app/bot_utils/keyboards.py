from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from .buttons import buttons


class KeyboardBuilder:
    @staticmethod
    def location_reply_keyboard() -> ReplyKeyboardMarkup:
        location_keyboard_buttons = [
            [
                KeyboardButton(text=buttons.location, request_location=True),
            ],
        ]
        return ReplyKeyboardMarkup(keyboard=location_keyboard_buttons, resize_keyboard=True, one_time_keyboard=True)

    @staticmethod
    def location_two_cities_keyboard(city_one: tuple, city_two: tuple) -> InlineKeyboardMarkup:
        ticket_keyboard_buttons = [
            [
                InlineKeyboardButton(text=f"{city_one[0]} ({city_one[2]})", callback_data=city_one[1]),
                InlineKeyboardButton(text=f"{city_two[0]} ({city_two[2]})", callback_data=city_two[1]),
            ],
        ]
        return InlineKeyboardMarkup(inline_keyboard=ticket_keyboard_buttons)

    @staticmethod
    def main_reply_keyboard() -> ReplyKeyboardMarkup:
        main_keyboard_buttons = [
            [
                KeyboardButton(text=buttons.subscribes),
                KeyboardButton(text=buttons.five_cheapest),
                KeyboardButton(text=buttons.weather),
                KeyboardButton(text=buttons.season),
            ],
        ]
        return ReplyKeyboardMarkup(keyboard=main_keyboard_buttons, resize_keyboard=True, one_time_keyboard=False)

    @staticmethod
    def ticket_reply_keyboard(ticket_url: str) -> InlineKeyboardMarkup:
        ticket_keyboard_buttons = [
            [
                InlineKeyboardButton(text=buttons.buy, url=ticket_url),
                InlineKeyboardButton(text=buttons.subscribe, callback_data=buttons.subscribe),
            ],
        ]
        return InlineKeyboardMarkup(inline_keyboard=ticket_keyboard_buttons)
