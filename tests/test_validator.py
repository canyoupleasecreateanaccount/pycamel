from typing import List

from pydantic import BaseModel

from pycamel.src.modules.core.validator import Validator


class GameBase(BaseModel):
    game_name: str


class Game(GameBase):
    game_rating: int


class Order(GameBase):
    order_count: int


class OrderGame(BaseModel):
    game: Order


class User(BaseModel):
    name: str
    games: List[Game]
    orders: OrderGame


TEST_USER = {
    "name": "John",
    "games": [
        {"game_name": "CSGO", "game_rating": 5},
        {"game_name": "Diablo", "game_rating": 5}
    ],
    "orders": {
        "game": {
            "game_name": "CSGO", "order_count": 4
        }
    }
}


def test_validation_without_validation_key():
    result = Validator(User, TEST_USER).fetch()
    for item in result:
        assert isinstance(item, User) is True


def test_validation_with_validation_key():
    result = Validator(Game, TEST_USER, 'games').fetch()
    for item in result:
        assert isinstance(item, Game) is True


def test_validation_with_received_path():
    result = Validator(Order, TEST_USER, "orders:game").fetch()
    for item in result:
        assert isinstance(item, Order)


def test_validation_error_if_something_went_wrong():
    try:
        Validator(Game, TEST_USER).fetch()
        int('This row of wrong code for case when row '
            'above did not return Assertion error'
            )
    except AssertionError:
        pass
