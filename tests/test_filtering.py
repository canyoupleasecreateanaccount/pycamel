import pytest

from pycamel.src.modules.core.filter import Filter


@pytest.mark.parametrize(
    "filter_value, expected_filter", [
        ({"gender": "male", "age": 18}, "?gender=male&age=18"),
        ({"page-limit": 100, "page_offset": 20, "tag": ["teamTag"]},
         "?page-limit=100&page_offset=20&tag=teamTag"),
        ({"flat_id_in": [2, 34, 45, 6], "human_name_in": ['Alice', 'Ann']},
         "?flat_id_in=2,34,45,6&human_name_in=Alice,Ann"),
        ({"tag": []}, "?tag="),
        ({}, "?"),
        ({"q": "a&b=c d"}, "?q=a%26b%3Dc%20d"),
        ({"tag": ["a,b", "c&d"]}, "?tag=a%2Cb,c%26d"),
        ({"city": "Kyiv Обл"}, "?city=Kyiv%20%D0%9E%D0%B1%D0%BB"),
    ])
def test_filter_build(filter_value, expected_filter):
    """
    In the case we validate that filter builder creates without any problems
    search query from string, number, array of strings and array of numbers.
    Also covers percent-encoding of values containing '&', '=', spaces,
    commas and non-ASCII characters, so they cannot corrupt the query
    string or inject extra parameters.
    """
    generated_filter = Filter.build_filter(filter_value)
    assert generated_filter == expected_filter
