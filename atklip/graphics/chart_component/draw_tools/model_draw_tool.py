from dataclasses import dataclass


@dataclass
class Line:
    pos: list
    item: object
    color: tuple|str
    brush: tuple|str
    show: bool