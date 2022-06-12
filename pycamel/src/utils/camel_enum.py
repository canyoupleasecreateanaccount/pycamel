from enum import Enum


class CamelEnum(Enum):
    """
    Default inheritance from Enum class with possibility to get list of enums.
    """
    @classmethod
    def list(cls) -> list:
        """
        Method gets all values from Enum class and prepare array with them.
        :return: list of values of Enum instance
        """
        return list(map(lambda c: c.value, cls))
