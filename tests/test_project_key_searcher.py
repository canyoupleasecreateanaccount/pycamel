import os
import pytest

from pycamel.src.utils.search_key_processor import search_key_processor


def test_empty_key_if_nothing_was_found(clear_project_validation_key):
    """
    Check that searcher returns None in case when nothing has been passed to
    all project validation key parameters on Config/Router/Route stages.
    """
    validation_key = search_key_processor()
    assert validation_key is None


@pytest.mark.parametrize("router_key, response_key, expected_result", [
    ("name", None, "name"),
    (None, "surname", "surname"),
    ("name", "surname", "surname"),
    ('', "last_name", 'last_name'),
    ('middle_name', '', None),
    (None, None, 'data'),
    ('', None, None)
])
def test_key_priority(
        clear_project_validation_key,
        router_key,
        response_key,
        expected_result
):
    """
    Validating prioritization of project keys on each level Config/Router/Route
    """
    os.environ['pc_project_validation_key'] = 'data'
    validation_key = search_key_processor(router_key, response_key)
    assert validation_key == expected_result
