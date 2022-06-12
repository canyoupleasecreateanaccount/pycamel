import pytest

from pycamel.src.modules.core.filter import Filter


@pytest.mark.parametrize(
    "filter_value, expected_filter", [
        ({"gender": "male", "age": 18}, "?gender=male&age=18"),
        ({"page-limit": 100, "page_offset": 20},
         "?page-limit=100&page_offset=20"),
        ({"flat_id_in": [2, 34, 45, 6], "human_id_in": [411]},
         "?flat_id_in=2,34,45,6&human_id_in=411")
    ])
def test_filter_build(filter_value, expected_filter):
    generated_filter = Filter.build_filter(filter_value)
    assert generated_filter == expected_filter
