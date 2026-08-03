import os
from typing import Optional

import pytest
import requests

from pydantic import BaseModel

from pycamel.src.modules.routing.router import Router
from pycamel.src.modules.response.response import CamelResponse


BASE = 'https://send-request.me/api'

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
    """Pydantic schema for a user as returned by the practice backend."""
    user_id: int


@pytest.fixture
def clear_project_validation_key():
    """Remove pc_project_validation_key from the env before a test runs."""
    if 'pc_project_validation_key' in os.environ:
        del os.environ['pc_project_validation_key']


@pytest.fixture(scope='session')
def get_issues_router():
    """Return the shared Router for the practice API's /issues endpoint."""
    return ISSUE_ROUTER


@pytest.fixture(scope='session')
def get_router():
    """Return the shared Router for the practice API's /users endpoint."""
    return USERS_ROUTER


@pytest.fixture(scope='session')
def get_router_with_default_headers():
    """Return a /users Router pre-configured with a default header."""
    return USERS_ROUTER_WITH_DEFAULT_HEADER


@pytest.fixture(scope='session')
def make_request():
    """Perform a real GET /users request against the practice backend."""
    response = requests.get(f'{BASE}/users')
    return response


@pytest.fixture
def get_response(make_request):
    """Wrap the shared /users response into a CamelResponse instance."""
    c_response = CamelResponse(
        response=make_request,
        headers={'Content-Type': 'application/json'}
    )
    return c_response


@pytest.fixture
def create_user(get_router):
    """Create a user on the practice backend and return its JSON body."""
    user_data = {
        "last_name": "morpheus"
    }
    response = get_router.post(json=user_data)
    response.assert_status_code([201])
    return response.get_response_json()
