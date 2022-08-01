import os


class CamelConfig:
    """
    Configuration class responses for project configuration.
    Parameters of the class decides how it will work.
    """
    def __init__(self, host: str, project_validation_key: str = None) -> None:
        """
        :param host: Base url for all services and endpoints.
            If we have something like that:
            https://google.com/v2/api/get_urls?is_public=true
            so, url for that property will be https://google.com/
        :param project_validation_key: It is not mandatory parameter.
            Receives string that needs for getting data from response object.
            Validation method get that parameter in case when it didn't set
            for concreate endpoint or validation function didn't receive it
            directly.
            For example, if in your backend project you have stable contract
            like that:
            {"meta": {"some":"data"}, "data": {"some": "data"}}
            You don't need to get key "data" all time from response.json(),
            all that you need, just put your key here and for all endpoints we
            will try to get data by that key.
            For cases when you need to get data from lower level, you can
            set list of keys as string with :.
            Like that - "data:some:needed:"
        """
        self.host = host
        self.project_validation_key = project_validation_key
        self._set_env_properties()

    def _set_env_properties(self) -> None:
        """
        Sets all project configuration variables as env variables.
        All properties that don't have values, will not be set.
        :return: None
        """
        env_variables = self.__dict__
        for variable in env_variables:
            if env_variables.get(variable) is not None:
                os.environ[f"pc_{variable}"] = env_variables.get(variable)
