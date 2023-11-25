from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from .buttons import buttons


class KeyboardBuilder:
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
