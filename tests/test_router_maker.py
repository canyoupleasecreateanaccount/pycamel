import os

import pytest

from pycamel.src.modules.routing.router_maker import RouterMaker
from pycamel.src.modules.routing.router import Router


@pytest.mark.parametrize("default_header, expected_value", [
    (None, {'Content-Type': 'application/json'}),
    (
        {"some": "header"},
        {'Content-Type': 'application/json', "some": "header"}
    ),
    (
        {"some": "header", "second_some": 1},
        {'Content-Type': 'application/json', "some": "header", "second_some": 1}
    ),
])
def test_router_generation(
        clear_project_validation_key, default_header, expected_value
):
    """Check functionality of route generation"""
    os.environ['pc_host'] = 'https://google.com'
    maker = RouterMaker('/v1').make_router(
        route='/api/images',
        router_validation_key='images_array',
        default_headers=default_header
    )
    assert isinstance(maker, Router) is True
    assert maker.path == 'https://google.com/v1/api/images'
    assert maker.router_validation_key == 'images_array'
    assert maker.headers == expected_value
