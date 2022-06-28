from pycamel.src.utils.camel_enum import CamelEnum


class Statuses(CamelEnum):
    ACTIVE = "ACTIVE"
    BANNED = "BANNED"


class RandomNumbers(CamelEnum):
    one = 1
    two = 2
    five = 5


def test_getting_list_of_attributes():
    assert isinstance(Statuses.list(), list)
    assert Statuses.list() == ['ACTIVE', 'BANNED']


def test_getting_list_of_numbers():
    assert isinstance(RandomNumbers.list(), list)
    assert RandomNumbers.list() == [1, 2, 5]
