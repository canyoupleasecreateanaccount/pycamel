import os

import pytest

from pycamel.src.modules.routing.router_maker import RouterMaker
from pycamel.src.modules.routing.router import Router
from pycamel.src.errors.SystemErrors import MissingConfigError


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


def test_router_generation_without_configured_host(clear_project_validation_key):
    """
    Check that a clear error is raised when routes are built before
    CamelConfig has been initiated with a host, instead of silently
    building a URL like 'None/api/images'.
    """
    os.environ.pop('pc_host', None)
    try:
        RouterMaker('/v1').make_router(route='/api/images')
        int('For case when row above did not raise MissingConfigError')
    except MissingConfigError:
        pass
