import os

from typing import Optional


def search_key_processor(
        router_validation_key: str = None,
        response_validation_key: str = None
) -> Optional[str]:
    """
    Functions detects all validation keys and according to priority
    returns the highest prioritized key.
    :param router_validation_key: Key that has been received from router
    declaration. That key responses for all routes under one router maker.
    :param response_validation_key: Key that has been received from validation
    method. It has the highest priority and applies to only one data object
    in specific case.
    :return: Returns string or None if key did not find.
    """
    env_key = os.getenv("pc_project_validation_key")
    if response_validation_key is not None:
        if response_validation_key == '':
            return None
        return response_validation_key
    elif router_validation_key is not None:
        if router_validation_key != '':
            return router_validation_key
        return None
    elif env_key:
        return os.getenv("pc_project_validation_key")
    return None
