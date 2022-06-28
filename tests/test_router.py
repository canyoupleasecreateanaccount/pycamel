from tests.conftest import PATH, User


def test_path_setter(get_router):
    get_router.add_to_path('/1')
    assert get_router.request_path == f"{PATH}/1"


def test_header_setter(get_router):
    header = {"TEST_HEADER": "APP"}
    get_router.set_headers(header)
    assert get_router.request_headers == header


def test_filter_setter(get_router):
    req_filter = {"page": 2}
    get_router.set_filters(req_filter)
    assert get_router.request_path == f"{PATH}?page=2"


def test_header_append(get_router):
    get_router.append_header("TEST_HEADER", "APP")
    assert get_router.request_headers == {
        'Content-Type': 'application/json', 'TEST_HEADER': 'APP'
    }


def test_default_get_request(get_router):
    response = get_router.get()
    response.assert_status_code([200])


def test_default_post_request(get_router):
    user_data = {
        "name": "morpheus",
        "job": "leader"
    }
    response = get_router.post(json=user_data)
    response.assert_status_code([201])


def test_default_put_request(get_router):
    user_data = {
        "name": "morpheus",
        "job": "zion resident"
    }
    response = get_router.add_to_path('/2').put(json=user_data)
    response.assert_status_code([200])


def test_default_patch_request(get_router):
    user_data = {
        "name": "morpheus",
        "job": "zion resident"
    }
    response = get_router.add_to_path('/2').patch(json=user_data)
    response.assert_status_code([200])


def test_default_delete_request(get_router):
    response = get_router.add_to_path('/2').delete()
    response.assert_status_code([204])


def test_router_clear_method(get_router):
    get_router.add_to_path('/100')
    assert get_router.request_path == f"{PATH}/100"
    get_router._clear()
    assert get_router.request_path == PATH


def test_getting_assert_error_with_wrong_schema(get_router):
    response = get_router.get()
    try:
        response.validate(User, '')
        int('For case when assertion did not trigger for row above')
    except AssertionError:
        pass


def test_getting_validated_objects(get_router):
    response = get_router.add_to_path('/1').get()
    response.validate(User, 'data')
    validated_objects = response.get_validated_objects()
    assert isinstance(*validated_objects, User) is True
