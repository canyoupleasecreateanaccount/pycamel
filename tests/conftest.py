import pytest

from src.modules.core.config import CamelConfig
from src.modules.routing.router_maker import RouterMaker

CamelConfig(host='https://gorest.co.in')
public_maker = RouterMaker('/public/v1')

posts = public_maker.make_router('/users')


@pytest.fixture(scope='session')
def users_route():
    return posts

