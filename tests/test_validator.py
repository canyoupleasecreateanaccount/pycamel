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
    """
    Test common validation using pydantic model.
    """
    result = Validator(User, TEST_USER).fetch()
    for item in result:
        assert isinstance(item, User) is True


def test_validation_with_validation_key():
    """
    Test validation with validation key, when only first step has been sent.
    """
    result = Validator(Game, TEST_USER, 'games').fetch()
    for item in result:
        assert isinstance(item, Game) is True


def test_validation_with_received_path():
    """
    Test validation with validation key, when more than one step has been sent.
    """
    result = Validator(Order, TEST_USER, "orders:game").fetch()
    for item in result:
        assert isinstance(item, Order)


def test_validation_if_data_is_wrong():
    """
    Test when data is invalid and schema could not be applied to it.
    """
    try:
        Validator(Game, TEST_USER).fetch()
        int('For case when row above did not trigger assertion')
    except AssertionError:
        pass
