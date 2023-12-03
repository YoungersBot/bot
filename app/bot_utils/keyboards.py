from dataclasses import dataclass

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from .buttons import ConfirmRejectText, DefaultCustomTicketText, SelectedCustomTicketText, buttons


@dataclass
class CustomTicketButtons:
    departure_city = InlineKeyboardButton(text=DefaultCustomTicketText.origin_city, callback_data="origin_city")
    destination_city = InlineKeyboardButton(
        text=DefaultCustomTicketText.destination_city, callback_data="destination_city"
    )
    departure_date = InlineKeyboardButton(text=DefaultCustomTicketText.departure_date, callback_data="departure_date")
    return_date = InlineKeyboardButton(text=DefaultCustomTicketText.return_date, callback_data="return_date")


@dataclass
class ConfirmRejectButtons:
    confirm = InlineKeyboardButton(text=ConfirmRejectText.confirm, callback_data="confirm")
    reject = InlineKeyboardButton(text=ConfirmRejectText.reject, callback_data="reject")


class KeyboardBuilder:
    @staticmethod
    def location_reply_keyboard() -> ReplyKeyboardMarkup:
        location_keyboard_buttons = [
            [
                KeyboardButton(text=buttons.location, request_location=True),
            ],
        ]
        return ReplyKeyboardMarkup(
            keyboard=location_keyboard_buttons,
            resize_keyboard=True,
            one_time_keyboard=True,
        )

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
                KeyboardButton(text=buttons.subscriptions),
                KeyboardButton(text=buttons.five_cheapest),
                KeyboardButton(text=buttons.weather),
                KeyboardButton(text=buttons.season),
                KeyboardButton(text=buttons.custom_ticket),
            ],
        ]
        return ReplyKeyboardMarkup(
            keyboard=main_keyboard_buttons,
            resize_keyboard=True,
            one_time_keyboard=False,
        )

    @staticmethod
    def ticket_reply_keyboard(ticket_url: str, data) -> InlineKeyboardMarkup:
        ticket_keyboard_buttons = [
            [
                InlineKeyboardButton(text=buttons.buy, url=ticket_url),
                InlineKeyboardButton(text=buttons.subscribe, callback_data=data),
            ],
        ]
        return InlineKeyboardMarkup(inline_keyboard=ticket_keyboard_buttons)

    @staticmethod
    def delete_subscription(data):
        delete_subscription_keyboard = [
            [InlineKeyboardButton(text=buttons.unsubscribe, callback_data=data)],
        ]
        return InlineKeyboardMarkup(inline_keyboard=delete_subscription_keyboard)

    @staticmethod
    def weather_reply_keyboard():
        weather_keyboard = [
            [
                KeyboardButton(text=buttons.weather_in_your_city),
                KeyboardButton(text=buttons.weather_in_any_city),
            ],
        ]
        return ReplyKeyboardMarkup(keyboard=weather_keyboard, resize_keyboard=True)

    @staticmethod
    def season_reply_keyboard():
        season_keyboard = [
            [KeyboardButton(text=buttons.season)],
        ]
        return ReplyKeyboardMarkup(keyboard=season_keyboard, resize_keyboard=True)

    @staticmethod
    def feedback_keyboards():
        feed_action_menuKB = InlineKeyboardMarkup(
            row_width=2,
            inline_keyboard=[
                [InlineKeyboardButton(text="Оставить отзыв 📝", callback_data="feedback")],
                [InlineKeyboardButton(text="Не хочу оставлять отзыв 🚫", callback_data="cancel_feedback")],
            ],
        )
        return feed_action_menuKB

    @staticmethod
    def custom_ticket_keyboard(
        origin_city: str = None,
        destination_city: str = None,
        departure_date: str = None,
        return_date: str = None,
        ready_to_search: bool = False,
    ):
        custom_ticket_buttons = CustomTicketButtons()

        if origin_city:
            custom_ticket_buttons.departure_city.text = SelectedCustomTicketText.origin_city.format(
                origin_city=origin_city
            )
        if destination_city:
            custom_ticket_buttons.destination_city.text = SelectedCustomTicketText.destination_city.format(
                destination_city=destination_city
            )
        if departure_date:
            custom_ticket_buttons.departure_date.text = SelectedCustomTicketText.departure_date.format(
                departure_date=departure_date
            )
        if return_date:
            custom_ticket_buttons.return_date.text = SelectedCustomTicketText.return_date.format(
                return_date=return_date
            )

        keyboard_buttons = [
            custom_ticket_buttons.departure_city,
            custom_ticket_buttons.destination_city,
            custom_ticket_buttons.departure_date,
            custom_ticket_buttons.return_date,
        ]
        keyboard = [[button] for button in keyboard_buttons]

        if ready_to_search:
            confirm_reject_row = [ConfirmRejectButtons.reject, ConfirmRejectButtons.confirm]
            keyboard.append(confirm_reject_row)
        else:
            keyboard.append([ConfirmRejectButtons.reject])

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def reset_custom_ticket_buttons():
        CustomTicketButtons.departure_city.text = DefaultCustomTicketText.origin_city
        CustomTicketButtons.destination_city.text = DefaultCustomTicketText.destination_city
        CustomTicketButtons.departure_date.text = DefaultCustomTicketText.departure_date
        CustomTicketButtons.return_date.text = DefaultCustomTicketText.return_date
