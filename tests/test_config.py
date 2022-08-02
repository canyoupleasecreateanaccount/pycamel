import os

from pycamel.src.modules.core.config import CamelConfig


def test_config_parameters(clear_project_validation_key):
    """
    Check that host and project validation key has been set into env variables.
    """
    config = CamelConfig("http://localhost/", "computer")
    assert \
        os.environ['pc_project_validation_key'] == config.project_validation_key
    assert os.environ['pc_host'] == config.host


def test_absent_validation_key(clear_project_validation_key):
    """
    Check that host set into project variables and validation key is None when
    it didn't pass to CamelConfig.
    """
    config = CamelConfig("http://localhost/")
    assert os.getenv('pc_project_validation_key') is None
    assert os.environ['pc_host'] == config.host
