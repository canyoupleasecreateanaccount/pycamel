from enum import Enum


class CamelEnum(Enum):
    """
    Default inheritance from Enum class with possibility to get list of enums.
    """
    @classmethod
    def list(cls) -> list:
        """
        Method gets all values from Enum class and prepare array with them.
        For example, you have next enum class:
        class Example(CamelEnum):
            ACTIVE = 'Active'
            BANNED = 'Banned'

        and you want to get all values of the class, just type Example.list()
        and you will get result ['Active', 'Banned']. It is very useful for case
        parametrizing and response validation.

        :return: list of values of Enum instance
        """
        return list(map(lambda c: c.value, cls))
