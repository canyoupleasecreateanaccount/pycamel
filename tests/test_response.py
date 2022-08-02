import pytest

import requests

from tests.conftest import User

from pycamel.src.modules.response.response import CamelResponse
from pycamel.src.errors.ValidationErrors import (
    IncorrectValidationPath, AbsentValidationItems, IncorrectAssertParameter
)


@pytest.mark.parametrize("status_codes", [
    ([200]),
    ([200, 201])
])
def test_status_code_assert(get_response, status_codes):
    """
    Validate that assertion of status code works fine for single value in
    array and for a few values
    """
    get_response.assert_status_code(status_codes)


def test_wrong_status_code(get_response):
    """
    Check that assert will be triggered in case when actual status code is
    not equal to expected.
    """
    try:
        get_response.assert_status_code([500])
        int('For case when assert error will not be triggered')
    except AssertionError:
        pass


@pytest.mark.parametrize("wrong_status_types", [
    '200',
    200,
    {"status": 200}
])
def test_incorrect_status_code_type(get_response, wrong_status_types):
    """
    In case we check raising ValueError exception, when expected status code
    does not conform to hint List[int]
    """
    try:
        get_response.assert_status_code(wrong_status_types)
        int('For case when assert error will not be triggered')
    except ValueError:
        pass


def test_getting_response_as_json(get_response):
    """
    Test getting raw response data from response object.
    """
    response_data = {"id": 12, "name": "John"}
    get_response.response_data = response_data
    assert get_response.get_response_json() == response_data


def test_getting_empty_response():
    """
    Check that response json catch JSONDecodeError and return empty dict
    as a result.
    """
    response = requests.get('https://google.com/')
    c_response = CamelResponse(
        response=response,
        headers={'Content-Type': 'application/json'}
    )
    assert c_response.get_response_json() == {}


def test_validation_method(get_response):
    """
    Positive case of validation, when schema is valid and user is presented
    """
    get_response.validate(User, 'data')


def test_wrong_validation_path(get_response):
    """
    In case we check that exception will be triggered for case when
    wrong path to validation object has been sent.
    """
    try:
        get_response.validate(User, 'data:structure')
        int('For case when assert error will not be triggered')
    except IncorrectValidationPath:
        pass


def test_empty_validation_error(get_response):
    """
    Check that exception will be raised when nothing has been passed to
    validate method.
    """
    get_response.response_data = {'data': {}}
    try:
        get_response.validate(User, 'data')
        int('For case when assert error will not be triggered')
    except AbsentValidationItems:
        pass


def test_any_parameter_assertion(get_response):
    """
    Test common asserting of parameter. Without any filters.
    """
    get_response.assert_parameter("limit", 3)


def test_when_parameter_not_found(get_response):
    """
    Testing case when data didn't find in response object according
    to received key. So, as a result we have nothing and have to raise
    exception.
    """
    try:
        get_response.assert_parameter("TV", "LG")
        int('For case when row above did not trigger assertion')
    except AbsentValidationItems:
        pass


def test_incorrect_filter_applied(get_router):
    """
    Check case when incorrect assert parameter has been passed into function.
    """
    response = get_router.add_to_path('/1').get()
    try:
        response.assert_parameter('first_name', 'data', '_ad')
        int('For case when row above did not trigger assertion')
    except IncorrectAssertParameter:
        pass


@pytest.mark.parametrize("filter_param, expected_value", [
    ("_eq", 3),
    ("_in", [2, 3, 4]),
    ("_lt", 4),
    ("_gt", 2),
    ("_le", 4),
    ("_le", 3),
    ("_ge", 2),
    ("_ge", 3)
])
def test_common_filter_params(get_response, filter_param, expected_value):
    """
    Testing filtering with common int values.
    """
    get_response.assert_parameter("limit", expected_value, filter_param)


@pytest.mark.parametrize("filter_param, expected_value", [
        ("_eq", 5),
        ("_in", [2, 4]),
        ("_lt", 2),
        ("_gt", 10),
        ("_le", 2),
        ("_ge", 5),
    ])
def test_assertion_on_filters(get_response, expected_value, filter_param):
    """
    Test that we will raise exception when something went wrong.
    """
    try:
        get_response.assert_parameter("limit", expected_value, filter_param)
        int('For case when row above did not trigger assertion')
    except AssertionError:
        pass


@pytest.mark.parametrize("data, expected_value, filter_param", [
    ({"name": "Antony"}, "Antony", "_eq"),
    ({"name": "Antony"}, ["John", "Antony"], "_in"),
    ({"name": [10, 11]}, [10, 11], "_eq")
])
def test_filter_assertion_with_diff_types(
        get_response,
        data,
        expected_value,
        filter_param
):
    """
    In case we check that filters works with common data types.
    """
    get_response.response_data = data
    get_response.assert_parameter("name", expected_value, filter_param)


def test_getting_items_by_key(get_response):
    """
    Test that get method returns array with all found items.
    """
    result = get_response.get_items_by_key('limit')
    assert isinstance(result, list) is True
    assert result == [3]


def test_get_absent_param_in_data(get_response):
    """
    Check that method returns empty array in case when nothing has been found.
    """
    result = get_response.get_items_by_key('TV')
    assert result == []
