from dataclasses import dataclass


@dataclass(frozen=True)
class Answers:
    start: str = 'Hi, {username}!'
    cheapest = 'Самые дешёвые билеты:'
    you_can_fly: str = 'Вы можете улететь в {destination} за {price}'
    subscribe: str = 'Вы успешно подписаны!'
    destination: str = 'Выберите направление: '
    limit: str = 'Сколько результатов поиска показать?\n От 1 до 10.'
    wrong_limit: str = 'Введите число от 1 до 10'


answers = Answers()
