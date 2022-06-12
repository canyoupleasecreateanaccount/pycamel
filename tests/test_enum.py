from pycamel.src.utils.camel_enum import CamelEnum


class Statuses(CamelEnum):
    ACTIVE = "ACTIVE"
    BANNED = "BANNED"


def test_getting_list_of_attributes():
    assert isinstance(Statuses.list(), list)
    assert Statuses.list() == ['ACTIVE', 'BANNED']
