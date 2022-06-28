import pytest
import os

import requests

from pycamel.src.modules.routing.router import Router
from pycamel.src.modules.response.response import CamelResponse
from pydantic import BaseModel


class User(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    avatar: str

PATH = 'https://reqres.in/api/users'


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