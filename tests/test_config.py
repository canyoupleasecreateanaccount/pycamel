import os

from pycamel.src.modules.core.config import CamelConfig


def test_config_parameters(clear_project_validation_key):
    config = CamelConfig("http://localhost/", "computer")
    assert \
        os.environ['pc_project_validation_key'] == config.project_validation_key
    assert os.environ['pc_host'] == config.host


def test_project_key_doesnt_set_if_absent_value(clear_project_validation_key):
    CamelConfig("http://localhost/")
    assert os.getenv('pc_project_validation_key') is None
