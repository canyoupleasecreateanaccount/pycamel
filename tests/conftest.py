import os
from datetime import timedelta
from typing import Optional
from unittest.mock import Mock

import pytest

from pydantic import BaseModel

from pycamel.src.modules.routing.router import Router


BASE = 'https://api.example.test'

USERS_ROUTER = Router(f'{BASE}/users')
USERS_ROUTER_WITH_DEFAULT_HEADER = Router(
    f'{BASE}/users', default_headers={"nice": "header"}
)
ISSUE_ROUTER = Router(f'{BASE}/issues')


class UserBase(BaseModel):
    """Base pydantic schema for a user, shared by tests across the suite."""
    first_name: Optional[str] = None
    last_name: str
    company_id: Optional[int] = None


class User(UserBase):
    """Pydantic schema for a user, shared by tests across the suite."""
    user_id: int


@pytest.fixture
def clear_project_validation_key():
    """Remove pc_project_validation_key from the env before a test runs."""
    if 'pc_project_validation_key' in os.environ:
        del os.environ['pc_project_validation_key']


@pytest.fixture(scope='session')
def get_issues_router():
    """Return the shared Router for the /issues endpoint."""
    return ISSUE_ROUTER


@pytest.fixture(scope='session')
def get_router():
    """Return the shared Router for the /users endpoint."""
    return USERS_ROUTER


@pytest.fixture(scope='session')
def get_router_with_default_headers():
    """Return a /users Router pre-configured with a default header."""
    return USERS_ROUTER_WITH_DEFAULT_HEADER


def fake_response(json_data=None, status_code=200, elapsed_seconds=0.0):
    """Build a Mock standing in for requests.Response, no network involved."""
    response = Mock()
    response.json.return_value = json_data if json_data is not None else {}
    response.status_code = status_code
    response.elapsed = timedelta(seconds=elapsed_seconds)
    return response


@pytest.fixture
def stub_session():
    """
    Patch every HTTP verb on a router's session so tests exercise Router and
    CamelResponse without touching the network. Returns a function that
    patches a given router and gives back the list of recorded calls
    (each entry has the url/headers/kwargs a real request would have seen).
    """
    def _stub(router, json_data=None, status_code=200, side_effect=None):
        calls = []

        def make_verb():
            def verb(url, headers, **kwargs):
                calls.append({"url": url, "headers": headers, **kwargs})
                if side_effect is not None:
                    raise side_effect
                return fake_response(
                    json_data=json_data, status_code=status_code
                )
            return verb

        for name in ("get", "post", "put", "patch", "delete"):
            setattr(router.session, name, make_verb())
        return calls

    return _stub
