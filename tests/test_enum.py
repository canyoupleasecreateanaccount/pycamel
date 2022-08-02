import pytest

from pycamel.src.utils.camel_enum import CamelEnum


class Statuses(CamelEnum):
    """Testing Enum with string"""
    ACTIVE = "ACTIVE"
    BANNED = "BANNED"


class RandomNumbers(CamelEnum):
    """Testing enum with numbers"""
    ONE = 1
    TWO = 2
    FIVE = 5


class RandomArrays(CamelEnum):
    """Testing enum with arrays"""
    NUMBERS = [1, 2, 3, 4]
    STATUSES = ['ACTIVE', 'BANNED']


@pytest.mark.parametrize("enum_class, expected_array", [
    (Statuses, ['ACTIVE', 'BANNED']),
    (RandomNumbers, [1, 2, 5]),
    (RandomArrays, [[1, 2, 3, 4], ['ACTIVE', 'BANNED']])
])
def test_getting_list_of_enums(enum_class, expected_array):
    """
    In the case we check that method returns valid arrays of enum values.
    """
    assert isinstance(enum_class.list(), list)
    assert enum_class.list() == expected_array
