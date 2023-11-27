from dataclasses import dataclass


@dataclass(frozen=True)
class ButtonsText:
    buy: str = "Купить"
    subscribe: str = "Подписаться"
    subscriptions: str = "Ваши подписки"
    five_cheapest: str = "5 самых дешёвых билетов"
    season: str = "Сезон"
    weather: str = "Погода"
    weather_in_your_city: str = "Погода в городе отправления"
    weather_in_any_city: str = "Погода в любом городе"
    location: str = "Запрос геолокации"

buttons = ButtonsText()
