from tests.conftest import User


def test_status_code_assert(get_response):
    get_response.assert_status_code([200])


def test_wrong_status_code(get_response):
    try:
        get_response.assert_status_code([500])
        int('For case when assert error will not be triggered')
    except AssertionError:
        pass


def test_incorrect_status_code_type(get_response):
    try:
        get_response.assert_status_code(200)
        assert 1 == 2, "Value error did not trigger for row above"
    except ValueError:
        pass


def test_getting_response_as_json(get_response):
    response_data = {"id": 12, "name": "John"}
    get_response.response_data = response_data
    assert get_response.get_response_json() == response_data


def test_validation_method(get_response):
    get_response.validate(User, 'data')


def test_any_parameter_assertion(get_response):
    get_response.assert_parameter("page", 1)


def test_when_parameter_not_found_for_assertion(get_response):
    try:
        get_response.assert_parameter("TV", "LG")
        int('For case when row above did not trigger assertion')
    except AssertionError:
        pass


def test_getting_items_by_key(get_response):
    result = get_response.get_items_by_key('page')
    assert isinstance(result, list) is True
    assert result == [1]


def test_getting_absent_parameter_in_response(get_response):
    result = get_response.get_items_by_key('TV')
    assert result == []
