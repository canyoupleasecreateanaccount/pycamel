from typing import List

import pytest

from pydantic import BaseModel

from pycamel.src.modules.core.validator import Validator
from pycamel.src.errors.ValidationErrors import (
    AbsentValidationItems, IncorrectValidationPath
)


class GameBase(BaseModel):
    """Base pydantic schema shared by Game and Order test schemas."""
    game_name: str


class Game(GameBase):
    """Pydantic schema for a rated game, used to exercise validation."""
    game_rating: int


class Order(GameBase):
    """Pydantic schema for an ordered game, used to exercise validation."""
    order_count: int


class OrderGame(BaseModel):
    """Pydantic schema wrapping a single Order, used for path-based keys."""
    game: Order


class User(BaseModel):
    """Pydantic schema for a user with nested games and orders."""
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


def test_validation_with_nested_key_without_path():
    """
    Test validation with a single validation key (no colon-delimited path)
    that is nested more than one level deep. Regression test for a bug
    where the recursive key search discarded results found below the
    first nesting level.
    """
    result = Validator(Order, TEST_USER, "game").fetch()
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


def test_validation_key_not_found_raises_absent_validation_items():
    """
    Test that a single validation key (no colon-delimited path) that does
    not exist anywhere in the response data raises AbsentValidationItems,
    covering the branch where the recursive search finds nothing at all.
    """
    with pytest.raises(AbsentValidationItems):
        Validator(Game, TEST_USER, "no_such_key").fetch()


def test_validation_path_through_non_dict_raises_incorrect_validation_path():
    """
    Test that a colon-delimited path walking into a non-dict value raises
    IncorrectValidationPath, covering the AttributeError branch of
    _data_searcher.
    """
    with pytest.raises(IncorrectValidationPath):
        Validator(Game, {"name": "John"}, "name:sub_key").fetch()
