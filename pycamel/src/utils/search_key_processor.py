import os


def search_key_processor(
        router_validation_key: str = None,
        response_validation_key: str = None
):
    env_key = os.getenv("pc_project_validation_key")
    if response_validation_key and response_validation_key != {}:
        return response_validation_key
    elif router_validation_key and router_validation_key != {}:
        return router_validation_key
    elif env_key and env_key != {}:
        return os.getenv("pc_project_validation_key")
    else:
        return None
