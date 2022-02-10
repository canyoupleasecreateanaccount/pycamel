from enum import Enum


class CamelEnum(Enum):

    @classmethod
    def list(cls) -> list:
        return list(map(lambda c: c.value, cls))
