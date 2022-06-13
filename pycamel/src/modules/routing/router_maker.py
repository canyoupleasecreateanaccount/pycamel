import os

from pycamel.src.modules.routing.router import Router


class RouterMaker:

    def __init__(self, service_host: str) -> None:
        """
        Class constructor.
        :param service_host: Receives part of url.
            For example, if main url looks like that:
            https://google.com/api-service/v1/some-endpoint
            router should have that part - api-service/v1
            After it, u can easy make any endpoints on that url
        """
        self.service_host = service_host

    def _build_url(self, route: str) -> str:
        """
        Build url from all parts of received data.
        :param route: String. Example of path /some-endpoint
        :return: String. Full path.
        """
        host = os.environ.get('pc_host')
        return f"{host}{self.service_host}{route}"

    def make_router(
            self,
            route: str,
            router_validation_key: str = None
    ) -> Router:
        """
        Returns Router object according to received path.
        Example of path /some-endpoint
        As a result u will get all REST methods with full functionality
        for that entity.
        :param route: String. Example /some-endpoint
        :return: Router object
        """
        path = self._build_url(route)
        return Router(path=path, router_validation_key=router_validation_key)
