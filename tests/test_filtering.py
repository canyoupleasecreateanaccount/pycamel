import pytest

from pycamel.src.modules.core.filter import Filter


@pytest.mark.parametrize(
    "filter_value, expected_filter", [
        ({"gender": "male", "age": 18}, "?gender=male&age=18"),
        ({"page-limit": 100, "page_offset": 20, "tag": ["teamTag"]},
         "?page-limit=100&page_offset=20&tag=teamTag"),
        ({"flat_id_in": [2, 34, 45, 6], "human_name_in": ['Alice', 'Ann']},
         "?flat_id_in=2,34,45,6&human_name_in=Alice,Ann"),
        ({}, "")
    ], ids=str)
def test_filter_build(filter_value, expected_filter):
    """
    In the case we validate that filter builder creates without any problems
    search query from string, number, array of strings and array of numbers.
    """
    generated_filter = Filter.build_filter(filter_value)
    assert generated_filter == expected_filter


@pytest.mark.parametrize("parameter, expected_value", [
    ([1, 2, 3, 4, 5], "1,2,3,4,5"),
    ([], "")
], ids=str)
def test_filter_prepare_array(parameter, expected_value):
    """
    Test that the _prepare_array() method correctly deserializes a list of
    values into a comma-separated string.
    """
    result = Filter._prepare_array(parameter)
    assert result == expected_value
