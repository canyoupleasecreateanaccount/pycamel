from src.modules.core.filter import Filter


def test_filter_build():
    filter_dict = {"gender": "male", "age": 18}
    generated_filter = Filter.build_filter(filter_dict)
    assert generated_filter == "?gender=male&age=18"

