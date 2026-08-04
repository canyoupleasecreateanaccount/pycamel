import threading
from datetime import timedelta
from unittest.mock import Mock

import pytest
import requests

from tests.conftest import BASE, User, fake_response

from pycamel.src.errors.SystemErrors import ForbiddenParameter, RequestException
from pycamel.src.modules.core.config import CamelConfig
from pycamel.src.modules.routing.router import Router

PATH = f'{BASE}/users'


@pytest.fixture
def reset_auth_provider():
    """Reset CamelConfig's class-level auth_provider after a test runs."""
    yield
    CamelConfig._auth_provider = None


def _fake_get_factory(calls):
    """Build a fake session.get that records the headers it was called with."""
    def fake_get(url, headers, **kwargs):
        """Stand in for session.get, no network involved."""
        calls.append(dict(headers))
        response = Mock()
        response.json.return_value = {}
        response.elapsed = timedelta(seconds=0)
        response.status_code = 200
        return response
    return fake_get


def _fake_get_kwargs_factory(calls):
    """Build a fake session.get that records the kwargs it was called with."""
    def fake_get(url, headers, **kwargs):
        """Stand in for session.get, no network involved."""
        calls.append(kwargs)
        response = Mock()
        response.json.return_value = {}
        response.elapsed = timedelta(seconds=0)
        response.status_code = 200
        return response
    return fake_get


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


def test_router_default_timeout_is_injected_into_request_kwargs():
    """
    Check that a configured default timeout is actually passed through to
    the underlying request when the caller does not pass their own.
    """
    calls = []
    router = Router(PATH, timeout=3.5)
    router.session.get = _fake_get_kwargs_factory(calls)
    router.get()
    assert calls[0]["timeout"] == 3.5


def test_explicit_request_timeout_overrides_router_default():
    """
    Check that a timeout passed explicitly to .get() is not overridden by
    the router's default timeout.
    """
    calls = []
    router = Router(PATH, timeout=3.5)
    router.session.get = _fake_get_kwargs_factory(calls)
    router.get(timeout=1)
    assert calls[0]["timeout"] == 1


def test_auth_provider_is_called_fresh_for_every_request():
    """
    Check that a router-level auth_provider is invoked again before each
    request (so it naturally supports token refresh) and that its headers
    are merged with the router's default headers.
    """
    calls = []
    token_box = {"n": 0}

    def provider():
        """Return a new bearer token header on every call."""
        token_box["n"] += 1
        return {"Authorization": f"Bearer token-{token_box['n']}"}

    router = Router(PATH, auth_provider=provider)
    router.session.get = _fake_get_factory(calls)
    router.get()
    router.get()
    assert calls[0]["Authorization"] == "Bearer token-1"
    assert calls[1]["Authorization"] == "Bearer token-2"
    assert calls[0]["Content-Type"] == "application/json"


def test_explicit_header_overrides_auth_provider():
    """
    Check that a header explicitly set via append_header/set_headers takes
    priority over the same header returned by auth_provider.
    """
    calls = []
    router = Router(
        PATH, auth_provider=lambda: {"Authorization": "Bearer from-provider"}
    )
    router.session.get = _fake_get_factory(calls)
    router.append_header("Authorization", "Bearer manual-override")
    router.get()
    assert calls[0]["Authorization"] == "Bearer manual-override"


def test_camel_config_auth_provider_is_used_as_project_wide_default(
        reset_auth_provider
):
    """
    Check that an auth_provider configured on CamelConfig is picked up by
    routers created afterward that don't set their own.
    """
    calls = []
    CamelConfig(
        "http://localhost/", auth_provider=lambda: {"X-Api-Key": "global-key"}
    )
    router = Router(PATH)
    router.session.get = _fake_get_factory(calls)
    router.get()
    assert calls[0]["X-Api-Key"] == "global-key"


def test_router_auth_provider_overrides_camel_config_default(
        reset_auth_provider
):
    """
    Check that a router-level auth_provider takes priority over the one
    configured on CamelConfig.
    """
    calls = []
    CamelConfig(
        "http://localhost/", auth_provider=lambda: {"X-Api-Key": "global-key"}
    )
    router = Router(PATH, auth_provider=lambda: {"X-Api-Key": "router-key"})
    router.session.get = _fake_get_factory(calls)
    router.get()
    assert calls[0]["X-Api-Key"] == "router-key"


def test_auth_provider_error_is_wrapped_as_request_exception():
    """
    Check that an exception raised by auth_provider (for example a failed
    network call to fetch a token) is wrapped into RequestException instead
    of leaking a raw, inconsistent exception type to the caller.
    """
    def failing_provider():
        raise ConnectionError("token endpoint unreachable")

    router = Router(PATH, auth_provider=failing_provider)
    with pytest.raises(RequestException):
        router.get()


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


def test_default_get_request(get_router, stub_session):
    """
    Test default get request.
    """
    stub_session(get_router, status_code=200)
    response = get_router.get()
    response.assert_status_code([200])


def test_default_post_request(get_router, stub_session):
    """
    Test default post request.
    """
    stub_session(get_router, status_code=201)
    user_data = {
        "last_name": "morpheus"
    }
    response = get_router.post(json=user_data)
    response.assert_status_code([201])


def test_default_put_request(get_router, stub_session):
    """
    Test default put request.
    """
    stub_session(get_router, status_code=200)
    user_data = {
        "last_name": "morpheus",
        "first_name": "Jony"
    }
    response = get_router.add_to_path("/1").put(json=user_data)
    response.assert_status_code([200])


def test_default_patch_request(get_router, stub_session):
    """
    Test default patch request.
    """
    stub_session(get_router, status_code=200)
    user_data = {
        "name": "morpheus",
        "job": "zion resident"
    }
    get_router.add_to_path("/1").patch(json=user_data)


def test_default_delete_request(get_router, stub_session):
    """
    Test default delete request.
    """
    stub_session(get_router, status_code=202)
    response = get_router.add_to_path("/1").delete()
    response.assert_status_code([202])


def test_router_clear_method(get_router):
    """
    Test clear method that uses each time after request send.
    """
    get_router.add_to_path('/100')
    assert get_router.request_path == f"{PATH}/100"
    get_router._clear()
    assert get_router.request_path == PATH


def test_getting_validated_objects(get_router, stub_session):
    """
    Test that after .validate method, user can get validated object as
    instances of BaseModel
    """
    stub_session(
        get_router, json_data={"user_id": 1, "last_name": "morpheus"}
    )
    response = get_router.add_to_path("/1").get()
    response.validate(User, '')
    validated_objects = response.get_validated_objects()
    assert isinstance(*validated_objects, User) is True


def test_header_propagation_to_response_class_from_set_header(
        get_router, stub_session
):
    """
    Test that added header could be in the response class.
    """
    stub_session(get_router)
    header = {"APP": "TEST"}
    response = get_router.set_headers(header).get()
    assert response.headers == header


def test_header_propagation_to_response_class_from_append_header(
        get_router, stub_session
):
    """
    Test that added header could be in the response class.
    """
    stub_session(get_router)
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


def test_case_with_throw_exception_during_request(
        get_issues_router, stub_session
):
    """
    Test that a RequestException from a failed request still leaves the
    router's path/headers state cleared, matching the state-clean behavior
    documented for exceptions raised during request execution.
    """
    stub_session(
        get_issues_router,
        side_effect=requests.exceptions.Timeout("simulated timeout")
    )
    try:
        get_issues_router.add_to_path('/companies/1').get(timeout=1)
        int("For case when row above did throw exception")
    except RequestException:
        pass
    assert get_issues_router.request_path == f'{BASE}/issues'
    assert get_issues_router.request_headers == {
        'Content-Type': 'application/json'
    }


@pytest.mark.parametrize("verb", ["post", "put", "patch", "delete"])
def test_request_json_is_captured_on_response(get_router, stub_session, verb):
    """
    Check that CamelResponse carries the json= payload that was sent,
    leaving request_data empty (ported from the old network-backed
    test_request_json_for_* tests in test_response.py).
    """
    stub_session(get_router)
    request_json = {"some": "body"}
    response = getattr(get_router, verb)(json=request_json)
    assert response.request_data is None
    assert response.request_json == request_json


@pytest.mark.parametrize("verb", ["post", "put", "patch", "delete"])
def test_request_data_is_captured_on_response(get_router, stub_session, verb):
    """
    Check that CamelResponse carries the data= payload that was sent,
    leaving request_json empty (ported from the old network-backed
    test_request_data_for_* tests in test_response.py).
    """
    stub_session(get_router)
    request_data = {"some": "body"}
    response = getattr(get_router, verb)(data=request_data)
    assert response.request_data == request_data
    assert response.request_json is None


def test_request_body_and_json_are_none_for_get(get_router, stub_session):
    """
    Check that CamelResponse has no data/json for a plain GET request
    (ported from test_request_body_and_json_for_get in test_response.py).
    """
    stub_session(get_router)
    response = get_router.get()
    assert response.request_data is None
    assert response.request_json is None


def test_forbidden_parameter_still_clears_router_state():
    """
    Regression test: ForbiddenParameter used to be raised before the
    try/finally that clears request_path/request_headers, so a rejected
    call left the router's mutated state (from an earlier add_to_path/
    set_headers/etc.) dangling instead of resetting it like every other
    failure path does.
    """
    router = Router(PATH)
    router.add_to_path('/1').append_header('X-Test', 'value')
    try:
        router.get(headers={"some": "header"})
        int("For case when row above did throw exception")
    except ForbiddenParameter:
        pass
    assert router.request_path == PATH
    assert router.request_headers == {'Content-Type': 'application/json'}


def test_failed_builder_call_releases_chain_lock():
    """
    Regression test for _chain_guard's exception path: a builder call that
    raises before the terminal get/post/etc. must release the chain lock
    it just acquired, otherwise the router would deadlock forever on the
    next request. set_filters(None) is not a dict, so Filter.build_filter
    raises AttributeError before .set_filters returns.
    """
    calls = []
    router = Router(PATH)
    router.session.get = _fake_get_factory(calls)

    with pytest.raises(AttributeError):
        router.set_filters(None)

    done = threading.Event()

    def run():
        router.get()
        done.set()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    deadlock_message = "router.get() deadlocked after a failed builder call"
    assert done.wait(timeout=2), deadlock_message
    assert len(calls) == 1


def test_concurrent_chains_are_serialized_per_router():
    """
    Regression test for thread-safety: two threads sharing one Router
    instance must never interleave their add_to_path/.../get() chains.
    Thread A's chain is held open (via a fake session.get that blocks
    until released) while thread B attempts its own chain; B's builder
    call must block until A's request has actually been sent and the
    router state cleared, proving A's in-flight request can't be
    corrupted by B's concurrent mutations.
    """
    router = Router(f'{BASE}/race')
    seen_urls = []
    a_in_flight = threading.Event()
    release_a = threading.Event()

    def blocking_get(url, headers, **kwargs):
        seen_urls.append(url)
        a_in_flight.set()
        assert release_a.wait(timeout=2), "test setup: release_a never set"
        return fake_response()

    router.session.get = blocking_get

    def run_a():
        router.add_to_path('/a').get()

    thread_a = threading.Thread(target=run_a)
    thread_a.start()
    a_never_started_message = "thread A never reached the network call"
    assert a_in_flight.wait(timeout=2), a_never_started_message

    b_finished = threading.Event()

    def run_b():
        router.add_to_path('/b').get()
        b_finished.set()

    thread_b = threading.Thread(target=run_b)
    thread_b.start()

    # Thread B's add_to_path must block behind A's still-open chain, so the
    # router's path stays exactly what A set it to for as long as A is
    # in flight.
    assert not b_finished.wait(timeout=0.2)
    assert router.request_path == f'{BASE}/race/a'

    release_a.set()
    thread_a.join(timeout=2)
    thread_b.join(timeout=2)

    assert b_finished.is_set()
    assert seen_urls == [f'{BASE}/race/a', f'{BASE}/race/b']
    assert router.request_path == f'{BASE}/race'
