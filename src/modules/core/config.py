import os


class CamelConfig:

    def __init__(self, host: str) -> None:
        self.host = host
        self.project_validation_key = None
        self._set_env_properties()

    def _set_env_properties(self) -> None:
        env_variables = self.__dict__
        for variable in env_variables:
            if env_variables.get(variable) is not None:
                os.environ[f"pc_{variable}"] = env_variables.get(variable)
