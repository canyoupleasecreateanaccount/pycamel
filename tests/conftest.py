import os
import pytest
from typing import Optional
from pydantic import BaseModel
import requests

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
