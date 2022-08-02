import pytest
from pycamel.src.utils.searcher import prepare_items


TEST_ITEM = {
    "time": "26.02.2022",
    "name": "SolveMe",
    "age": 92,
    "games": [
        {"game_name": "Diablo"},
        {"game_name": "CSGO"},
        {"game_name": "Dota 2"}
    ],
    "friends": [
        {"name": "Erich", "age": 42},
        {"name": "Artur", "age": 35}
    ],
    "job": {
        "status": "ACTIVE",
        "title": "AQA"
    },
    "best_numbers": [1, 7, 0, 3]
}


@pytest.mark.parametrize("search_key, expected_result", [
    ("games", [
        {'game_name': 'Diablo'},
        {'game_name': 'CSGO'},
        {'game_name': 'Dota 2'}
    ]),  # array of dictionaries
    ("age", [92, 42, 35]),  # values of keys from different levels
    ("job", [{"status": "ACTIVE", "title": "AQA"}]),  # top level dictionary
    ("title", ["AQA"]),  # string from low level
    ("best_numbers", [1, 7, 0, 3]),  # array of numbers
    ("time", ["26.02.2022"]),  # string from top level
    ("datetime", [])  # case for absent key in object
])
def test_get_diff_types_of_data(search_key, expected_result):
    """Check that searcher could find on any levels any types of data"""
    result = prepare_items(TEST_ITEM, search_key)
    assert result == expected_result
