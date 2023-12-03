from dataclasses import dataclass


@dataclass(frozen=True)
class ButtonsText:
    buy: str = "Купить"
    subscribe: str = "Подписаться"

    subscriptions: str = "Ваши подписки"
    five_cheapest: str = "Самые дешёвые билеты"
    season: str = "Сезон"
    weather: str = "Погода"
    custom_ticket: str = "Настроить поиск билета"

    weather_in_your_city: str = "Погода в городе отправления"
    weather_in_any_city: str = "Погода в любом городе"
    location: str = "Запрос геолокации"
    unsubscribe: str = "Отменить подписку"


@dataclass
class DefaultCustomTicketText:
    origin_city: str = "Выбрать город вылета ..."
    destination_city: str = "Выбрать город прилета ..."
    departure_date: str = "Выбрать дату вылета ..."
    return_date: str = "Выбрать дату возвращения ..."


@dataclass
class SelectedCustomTicketText:
    origin_city: str = "\U0001F6EB из города: {origin_city}"
    destination_city: str = "\U0001F6EC в город: {destination_city}"
    departure_date: str = "\U0001F5D3 дата туда: {departure_date}"
    return_date: str = "\U0001F5D3 дата обратно: {return_date}"


@dataclass
class ConfirmRejectText:
    confirm: str = "Подтвердить \u2705"
    reject: str = "Отменить \uE332"


buttons = ButtonsText()
