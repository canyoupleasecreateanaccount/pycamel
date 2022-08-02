import os

from pycamel.src.modules.routing.router_maker import RouterMaker
from pycamel.src.modules.routing.router import Router


def test_router_generation(clear_project_validation_key):
    """Check functionality of route generation"""
    os.environ['pc_host'] = 'https://google.com'
    maker = RouterMaker('/v1').make_router(
        route='/api/images', router_validation_key='images_array')
    assert isinstance(maker, Router) is True
    assert maker.path == 'https://google.com/v1/api/images'
    assert maker.router_validation_key == 'images_array'
