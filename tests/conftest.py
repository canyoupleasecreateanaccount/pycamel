import os
from typing import Optional

import pytest
import requests

from pydantic import BaseModel

from pycamel.src.modules.routing.router import Router
from pycamel.src.modules.response.response import CamelResponse


class UserBase(BaseModel):
    first_name: Optional[str]
    last_name: str
    company_id: Optional[int]


class User(UserBase):
    user_id: int


PATH = 'https://send-request.me/api/users'


@pytest.fixture
def clear_project_validation_key():
    if 'pc_project_validation_key' in os.environ:
        del os.environ['pc_project_validation_key']


@pytest.fixture
def get_router():
    test_router = Router(PATH)
    return test_router


@pytest.fixture(scope='session')
def make_request():
    response = requests.get(PATH)
    return response


@pytest.fixture
def get_response(make_request):
    c_response = CamelResponse(
        response=make_request,
        headers={'Content-Type': 'application/json'}
    )
    return c_response


@pytest.fixture
def create_user(get_router):
    user_data = {
        "last_name": "morpheus"
    }
    response = get_router.post(json=user_data)
    response.assert_status_code([201])
    return response.get_response_json()
