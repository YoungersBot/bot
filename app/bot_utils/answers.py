from dataclasses import dataclass


@dataclass(frozen=True)
class Answers:
    cheapest = "Самые дешёвые билеты:"
    you_can_fly: str = "Вы можете улететь в {destination} за {price} ."
    subscribe: str = "Вы успешно подписаны!"
    no_tickets: str = "Нет билетов по заданному направлению."

    destination: str = "Выберите направление: "
    limit: str = "Сколько результатов поиска показать?\n От 1 до 10."
    wrong_limit: str = "Введите число от 1 до 10"

    start: str = "Hi, {username}!"
    help_command: str = "Когда-нибудь здесь будет описание работы бота, пока просто перечень команд: \n" "/destination"
    geolocation: str = "Вы находитесь в {in_city}, в стране {country}. Ближайший аэропорт {airport}."
    weather: str = "Введите город:"
    weather_in_your_city: str = "{result}."
    weather_in_any_city: str = "{result}."
    actions: str = "Выберите действие:"
    season: str = "Mожно улететь в летний сезон:"
    season_weather: str =  "Вы можете улететь в {destination} за {price} {result}."


answers = Answers()
