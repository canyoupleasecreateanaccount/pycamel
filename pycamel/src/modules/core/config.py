import os

from typing import Callable, Optional


class CamelConfig:
    """
    Configuration class responses for project configuration.
    Parameters of the class decides how it will work.
    """
    _auth_provider: Optional[Callable[[], dict]] = None
    _ENV_FIELDS = (
        'host', 'project_validation_key', 'default_timeout', 'retries',
        'backoff_factor'
    )

    def __init__(
            self,
            host: str,
            project_validation_key: str = None,
            *,
            default_timeout: float = None,
            retries: int = None,
            backoff_factor: float = None,
            auth_provider: Callable[[], dict] = None
    ) -> None:
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
        :param default_timeout: It is not mandatory parameter. Default
            timeout (in seconds) applied to every request sent from any
            router, unless a router or a request overrides it.
        :param retries: It is not mandatory parameter. Default number of
            retries applied to every router for requests that fail with a
            gateway/service-unavailable status code, unless a router
            overrides it.
        :param backoff_factor: It is not mandatory parameter. Default
            backoff factor applied between retries, unless a router
            overrides it.
        :param auth_provider: It is not mandatory parameter. A zero-argument
            callable that returns a dict of headers (for example
            {"Authorization": "Bearer <token>"}). It is called again before
            every single request sent by any router, so it naturally
            supports token refresh - just make the callable fetch or renew
            the token whenever it is needed. Headers it returns are applied
            to every router unless a router sets its own auth_provider, and
            can still be overridden per request with .append_header/
            .set_headers.

        Each CamelConfig(...) call fully replaces the previously configured
        values: a parameter left as None here clears the matching setting
        (env variable, or the class-wide auth_provider) instead of leaving
        behind whatever an earlier CamelConfig(...) call configured. This
        keeps two consecutive configs (for example against two different
        services/environments in the same process) from silently leaking
        settings into each other.
        """
        self.host = host
        self.project_validation_key = project_validation_key
        self.default_timeout = default_timeout
        self.retries = retries
        self.backoff_factor = backoff_factor
        self._set_env_properties()
        CamelConfig._auth_provider = auth_provider

    def _set_env_properties(self) -> None:
        """
        Sets all project configuration variables as env variables. A
        property left as None clears the matching env variable rather than
        leaving a stale value behind from a previous CamelConfig(...) call.
        :return: None
        """
        for variable in self._ENV_FIELDS:
            env_key = f"pc_{variable}"
            value = getattr(self, variable)
            if value is not None:
                os.environ[env_key] = str(value)
            else:
                os.environ.pop(env_key, None)

    @staticmethod
    def get_auth_provider() -> Optional[Callable[[], dict]]:
        """
        Returns the project-wide auth_provider set on CamelConfig, if any.
        :return: Callable or None.
        """
        return CamelConfig._auth_provider

    @classmethod
    def reset(cls) -> None:
        """
        Clears every setting previously configured via CamelConfig: every
        pc_* env variable it manages and the class-wide auth_provider.
        Mainly useful in test suites/fixtures that need a clean slate
        between modules or services without relying on process exit to
        drop stale configuration.
        :return: None
        """
        for variable in cls._ENV_FIELDS:
            os.environ.pop(f"pc_{variable}", None)
        cls._auth_provider = None
