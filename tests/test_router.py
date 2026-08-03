from tests.conftest import BASE, User

from pycamel.src.errors.SystemErrors import ForbiddenParameter, RequestException
from pycamel.src.modules.routing.router import Router

PATH = f'{BASE}/users'


def test_router_has_no_timeout_or_retries_by_default():
    """
    Check that a router without explicit timeout/retries keeps the previous
    behavior: no enforced timeout and no retry adapter mounted.
    """
    router = Router(PATH)
    assert router.timeout is None
    assert router.retries == 0
    adapter = router.session.get_adapter(PATH)
    assert adapter.max_retries.total in (0, False)


def test_router_applies_explicit_timeout_and_retries():
    """
    Check that explicit timeout/retries/backoff_factor are stored on the
    router and a retry-enabled adapter is mounted on its session.
    """
    router = Router(PATH, timeout=2.5, retries=3, backoff_factor=1.1)
    assert router.timeout == 2.5
    assert router.retries == 3
    adapter = router.session.get_adapter(PATH)
    assert adapter.max_retries.total == 3
    assert adapter.max_retries.backoff_factor == 1.1
    assert adapter.max_retries.status_forcelist == [502, 503, 504]


def test_path_setter(get_router):
    """
    Test that add to path method works correct and has new path.
    """
    get_router.add_to_path('/1')
    assert get_router.request_path == f"{PATH}/1"
    get_router._clear()


def test_header_setter(get_router):
    """
    Test that set header drops all headers and put new one.
    """
    header = {"TEST_HEADER": "APP"}
    get_router.set_headers(header)
    assert get_router.request_headers == header
    get_router._clear()


def test_that_setter_override_default_headers(get_router_with_default_headers):
    """
    In test we validate that headers changes according to sent values and
    overrides default headers. Additional validation for _clean method that
    triggers when request has been sent.
    """
    default_headers = {
        "nice": "header", 'Content-Type': 'application/json'
    }
    assert get_router_with_default_headers.headers == default_headers

    new_header = {"TEST_HEADER": "APP"}
    get_router_with_default_headers.set_headers(new_header)
    assert get_router_with_default_headers.request_headers == new_header

    get_router_with_default_headers._clear()
    assert get_router_with_default_headers.headers == default_headers
    assert get_router_with_default_headers.request_headers == default_headers


def test_that_append_adds_headers_to_default(get_router_with_default_headers):
    """
    In test we validate that headers changes according to sent values and
    appends headers. Additional validation for _clean method that
    triggers when request has been sent.
    """
    default_headers = {
        "nice": "header", 'Content-Type': 'application/json'
    }
    assert get_router_with_default_headers.headers == default_headers

    get_router_with_default_headers.append_header("TEST_HEADER", "APP")
    assert get_router_with_default_headers.request_headers == {
        "nice": "header", 'Content-Type': 'application/json',
        "TEST_HEADER": "APP"
    }

    get_router_with_default_headers._clear()
    assert get_router_with_default_headers.headers == default_headers
    assert get_router_with_default_headers.request_headers == default_headers


def test_filter_setter(get_router):
    """
    Check that after filter build it adds to request path.
    """
    req_filter = {"limit": 2}
    get_router.set_filters(req_filter)
    assert get_router.request_path == f"{PATH}?limit=2"
    get_router._clear()


def test_header_append(get_router):
    """
    Check that new header has been added to default headers.
    """
    get_router.append_header("TEST_HEADER", "APP")
    assert get_router.request_headers == {
        'Content-Type': 'application/json', 'TEST_HEADER': 'APP'
    }
    get_router._clear()


def test_default_get_request(get_router):
    """
    Test default get request.
    """
    response = get_router.get()
    response.assert_status_code([200])


def test_default_post_request(get_router):
    """
    Test default post request.
    """
    user_data = {
        "last_name": "morpheus"
    }
    response = get_router.post(json=user_data)
    response.assert_status_code([201])


def test_default_put_request(get_router, create_user):
    """
    Test default put request.
    """
    user_data = {
        "last_name": "morpheus",
        "first_name": "Jony"
    }
    response = get_router.add_to_path(
        f"/{create_user.get('user_id')}").put(json=user_data)
    response.assert_status_code([200])


def test_default_patch_request(get_router, create_user):
    """
    Test default patch request.
    """
    user_data = {
        "name": "morpheus",
        "job": "zion resident"
    }
    get_router.add_to_path(
        f"/{create_user.get('user_id')}").patch(json=user_data)


def test_default_delete_request(get_router, create_user):
    """
    Test default delete request.
    """
    response = get_router.add_to_path(
        f"/{create_user.get('user_id')}").delete()
    response.assert_status_code([202])


def test_router_clear_method(get_router):
    """
    Test clear method that uses each time after request send.
    """
    get_router.add_to_path('/100')
    assert get_router.request_path == f"{PATH}/100"
    get_router._clear()
    assert get_router.request_path == PATH


def test_getting_validated_objects(get_router, create_user):
    """
    Test that after .validate method, user can get validated object as
    instances of BaseModel
    """
    response = get_router.add_to_path(
        f"/{create_user.get('user_id')}").get()
    response.validate(User, '')
    validated_objects = response.get_validated_objects()
    assert isinstance(*validated_objects, User) is True


def test_header_propagation_to_response_class_from_set_header(get_router):
    """
    Test that added header could be in the response class.
    """
    header = {"APP": "TEST"}
    response = get_router.set_headers(header).get()
    assert response.headers == header


def test_header_propagation_to_response_class_from_append_header(get_router):
    """
    Test that added header could be in the response class.
    """
    expected_headers = {'Content-Type': 'application/json', 'APP': 'TEST'}
    response = get_router.append_header("APP", "TEST").get()
    assert response.headers == expected_headers


def test_that_user_can_not_pass_forbidden_params_for_get(get_router):
    """
    In test we check that method throw error when user try to pass header or
    url without using of set methods.
    """
    try:
        get_router.get(headers={"some": "header"})
        int("For case when row above did throw exception")
    except ForbiddenParameter:
        pass
    try:
        get_router.get(url="https://google.com")
        int("For case when row above did throw exception")
    except ForbiddenParameter:
        pass


def test_that_user_can_not_pass_positional_arguments(get_router):
    """
    Check that a positional argument raises a clear ForbiddenParameter
    instead of leaking a confusing TypeError from the underlying requests
    call (regression test, positional args always collided with the
    explicit url= keyword passed internally).
    """
    try:
        get_router.get({"page": 1})
        int("For case when row above did throw exception")
    except ForbiddenParameter:
        pass


def test_that_user_can_not_pass_forbidden_params_for_post(get_router):
    """
    In test we check that method throw error when user try to pass header or
    url without using of set methods.
    """
    try:
        get_router.post(headers={"some": "header"})
        int("For case when row above did throw exception")
    except ForbiddenParameter:
        pass
    try:
        get_router.post(url="https://google.com")
        int("For case when row above did throw exception")
    except ForbiddenParameter:
        pass


def test_that_user_can_not_pass_forbidden_params_for_put(get_router):
    """
    In test we check that method throw error when user try to pass header or
    url without using of set methods.
    """
    try:
        get_router.put(headers={"some": "header"})
        int("For case when row above did throw exception")
    except ForbiddenParameter:
        pass
    try:
        get_router.put(url="https://google.com")
        int("For case when row above did throw exception")
    except ForbiddenParameter:
        pass


def test_that_user_can_not_pass_forbidden_params_for_patch(get_router):
    """
    In test we check that method throw error when user try to pass header or
    url without using of set methods.
    """
    try:
        get_router.patch(headers={"some": "header"})
        int("For case when row above did throw exception")
    except ForbiddenParameter:
        pass
    try:
        get_router.patch(url="https://google.com")
        int("For case when row above did throw exception")
    except ForbiddenParameter:
        pass


def test_that_user_can_not_pass_forbidden_params_for_delete(get_router):
    """
    In test we check that method throw error when user try to pass header or
    url without using of set methods.
    """
    try:
        get_router.delete(headers={"some": "header"})
        int("For case when row above did throw exception")
    except ForbiddenParameter:
        pass
    try:
        get_router.delete(url="https://google.com")
        int("For case when row above did throw exception")
    except ForbiddenParameter:
        pass


def test_case_with_throw_exception_during_request(get_issues_router):
    try:
        get_issues_router.add_to_path('/companies/1').get(timeout=1)
        int("For case when row above did throw exception")
    except RequestException:
        pass
    assert get_issues_router.request_path == 'https://send-request.me/api/issues'
    assert get_issues_router.request_headers == {
        'Content-Type': 'application/json'
    }
