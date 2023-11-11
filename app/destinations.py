from dataclasses import dataclass


@dataclass(frozen=True)
class Destinations:
    led: str = "Санкт-Петербург"
    aer: str = "Сочи"
    kzn: str = "Казань"


dst = Destinations()

dct: dict = {"LED": "Санкт-Петербург", "AER": "Сочи", "KZN": "Казань"}
