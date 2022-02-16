import pytest

from src.modules.core.config import CamelConfig
from src.modules.routing.router_maker import RouterMaker

CamelConfig(host='https://petstore.swagger.io')
public_maker = RouterMaker('/v2')

pets = public_maker.make_router('/pet')


@pytest.fixture(scope='session')
def get_pets():
    return pets


