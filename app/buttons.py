from dataclasses import dataclass


@dataclass(frozen=True)
class Buttons:
    buy: str = 'Купить'
    subscribe: str = 'Подписаться'
    subscribes: str = 'Ваши подписки'
    five_cheapest: str = '5 самых дешёвых билетов'
    weather: str = 'Погода'


btns = Buttons()
