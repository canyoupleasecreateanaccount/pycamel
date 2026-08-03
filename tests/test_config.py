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


def test_timeout_and_retry_parameters(clear_project_validation_key):
    """
    Check that default_timeout, retries and backoff_factor are set into env
    variables so routers created afterwards can pick them up.
    """
    CamelConfig(
        "http://localhost/", default_timeout=3.5, retries=2, backoff_factor=1.2
    )
    assert os.environ['pc_default_timeout'] == '3.5'
    assert os.environ['pc_retries'] == '2'
    assert os.environ['pc_backoff_factor'] == '1.2'
    del os.environ['pc_default_timeout']
    del os.environ['pc_retries']
    del os.environ['pc_backoff_factor']


def test_timeout_and_retry_parameters_absent_by_default(
        clear_project_validation_key
):
    """
    Check that default_timeout, retries and backoff_factor are not set into
    env variables when they haven't been passed to CamelConfig.
    """
    CamelConfig("http://localhost/")
    assert os.getenv('pc_default_timeout') is None
    assert os.getenv('pc_retries') is None
    assert os.getenv('pc_backoff_factor') is None
