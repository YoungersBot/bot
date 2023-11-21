from dataclasses import dataclass


@dataclass(frozen=True)
class ButtonsText:
    buy: str = "Купить"
    subscribe: str = "Подписаться"
    subscribes: str = "Ваши подписки"
    five_cheapest: str = "5 самых дешёвых билетов"
    weather: str = "Погода"
    weather_in_your_city: str = "Погода в твоем городе"
    weather_in_any_city: str = "Погода в любом городе"


buttons = ButtonsText()
