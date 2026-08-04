"""
Network-independent unit tests for CamelResponse. These exercise the same
behavior as tests/test_response.py but build a fake requests.Response with
unittest.mock instead of hitting a real backend, so they run deterministically
in any environment (offline sandboxes, restricted CI runners, etc.) and keep
CamelResponse's own logic fully covered regardless of network availability.
"""
from datetime import timedelta
from json import JSONDecodeError
from unittest.mock import Mock

import pytest

from pydantic import BaseModel

from pycamel.src.modules.response.response import CamelResponse
from pycamel.src.errors.ValidationErrors import (
    AbsentValidationItems, IncorrectAssertParameter, IncorrectValidationPath
)


class Game(BaseModel):
    """Minimal pydantic schema used to exercise CamelResponse.validate()."""
    game_name: str
    game_rating: int


TEST_DATA = {
    "limit": 3,
    "games": [
        {"game_name": "CSGO", "game_rating": 5},
        {"game_name": "Diablo", "game_rating": 5}
    ]
}


def make_response(
        json_data=None,
        status_code=200,
        elapsed_seconds=0.1,
        url="https://example.com/users",
        raise_json_error=False
):
    """Build a Mock standing in for requests.Response, no network involved."""
    response = Mock()
    if raise_json_error:
        response.json.side_effect = JSONDecodeError("msg", "doc", 0)
    else:
        response.json.return_value = json_data if json_data is not None else {}
    response.status_code = status_code
    response.elapsed = timedelta(seconds=elapsed_seconds)
    response.url = url
    return response


def make_camel_response(**kwargs):
    """Build a CamelResponse wrapping a fake response, no network involved."""
    return CamelResponse(response=make_response(**kwargs), headers={})


def test_response_data_defaults_to_empty_dict_on_invalid_json():
    """
    Check that a response whose body cannot be parsed as JSON does not
    crash CamelResponse, and response_data falls back to an empty dict.
    """
    response = make_camel_response(raise_json_error=True)
    assert response.get_response_json() == {}


def test_assert_status_code_passes_for_matching_code():
    """Check that assert_status_code does not raise for a matching code."""
    response = make_camel_response(json_data=TEST_DATA, status_code=200)
    response.assert_status_code([200, 201])


def test_assert_status_code_fails_for_non_matching_code():
    """Check that assert_status_code raises for a non-matching code."""
    response = make_camel_response(json_data=TEST_DATA, status_code=500)
    with pytest.raises(AssertionError):
        response.assert_status_code([200])


def test_assert_status_code_raises_value_error_for_wrong_type():
    """Check that a non-list expected_status_codes raises ValueError."""
    response = make_camel_response(json_data=TEST_DATA, status_code=200)
    with pytest.raises(ValueError):
        response.assert_status_code(200)


def test_assert_response_time_passes_for_generous_threshold():
    """Check that assert_response_time does not raise for a generous max."""
    response = make_camel_response(json_data=TEST_DATA, elapsed_seconds=0.1)
    response.assert_response_time(1)


def test_assert_response_time_fails_for_tiny_threshold():
    """Check that assert_response_time raises when elapsed exceeds max."""
    response = make_camel_response(json_data=TEST_DATA, elapsed_seconds=1)
    with pytest.raises(AssertionError):
        response.assert_response_time(0.01)


def test_validate_success():
    """Check that validate() parses matching data into schema instances."""
    response = make_camel_response(json_data=TEST_DATA)
    response.validate(Game, 'games')
    validated = response.get_validated_objects()
    assert len(validated) == 2
    assert all(isinstance(item, Game) for item in validated)


def test_validate_failure_raises_assertion_error():
    """Check that validate() raises AssertionError for schema mismatches."""
    response = make_camel_response(json_data={"games": [{"game_name": "CSGO"}]})
    with pytest.raises(AssertionError):
        response.validate(Game, 'games')


def test_validate_wrong_path_raises_incorrect_validation_path():
    """
    Check that a colon-delimited validation path whose intermediate segment
    resolves to a list (which has no .get()) raises IncorrectValidationPath
    instead of an unrelated AttributeError.
    """
    response = make_camel_response(json_data={"games": [{"game_name": "CSGO"}]})
    with pytest.raises(IncorrectValidationPath):
        response.validate(Game, 'games:rating')


def test_validate_empty_data_raises_absent_validation_items():
    """Check that validate() raises AbsentValidationItems for empty data."""
    response = make_camel_response(json_data={"games": []})
    with pytest.raises(AbsentValidationItems):
        response.validate(Game, 'games')


@pytest.mark.parametrize("filter_param, expected_value", [
    ("_eq", 3),
    ("_in", [2, 3, 4]),
    ("_lt", 4),
    ("_gt", 2),
    ("_le", 3),
    ("_ge", 3),
])
def test_assert_parameter_passes_for_all_conditions(filter_param, expected_value):
    """Check that assert_parameter passes for every supported filter."""
    response = make_camel_response(json_data=TEST_DATA)
    response.assert_parameter("limit", expected_value, filter_param)


@pytest.mark.parametrize("filter_param, expected_value", [
    ("_eq", 5),
    ("_in", [2, 4]),
    ("_lt", 2),
    ("_gt", 10),
])
def test_assert_parameter_fails_for_all_conditions(filter_param, expected_value):
    """Check that assert_parameter raises when the condition is not met."""
    response = make_camel_response(json_data=TEST_DATA)
    with pytest.raises(AssertionError):
        response.assert_parameter("limit", expected_value, filter_param)


def test_assert_parameter_raises_for_unknown_key():
    """Check that assert_parameter raises AbsentValidationItems when the
    parameter is not found anywhere in the response."""
    response = make_camel_response(json_data=TEST_DATA)
    with pytest.raises(AbsentValidationItems):
        response.assert_parameter("missing_key", 1)


def test_assert_parameter_raises_for_unknown_condition():
    """Check that assert_parameter raises IncorrectAssertParameter for an
    unsupported filter condition."""
    response = make_camel_response(json_data=TEST_DATA)
    with pytest.raises(IncorrectAssertParameter):
        response.assert_parameter("limit", 3, "_unknown")


def test_get_items_by_key_returns_matches():
    """Check that get_items_by_key collects every matching value."""
    response = make_camel_response(json_data=TEST_DATA)
    assert response.get_items_by_key("game_name") == ["CSGO", "Diablo"]


def test_get_items_by_key_returns_empty_list_when_absent():
    """Check that get_items_by_key returns [] when the key is not found."""
    response = make_camel_response(json_data=TEST_DATA)
    assert response.get_items_by_key("missing_key") == []


def test_str_representation_contains_request_and_response_info():
    """Check that __str__ includes request/response details for reports."""
    response = CamelResponse(
        response=make_response(
            json_data=TEST_DATA, url="https://example.com/users"
        ),
        headers={'Content-Type': 'application/json'},
        request_json={"some": "body"},
        request_data=None
    )
    text = str(response)
    assert "https://example.com/users" in text
    assert "200" in text
    assert "some" in text
