import os

from pycamel.src.modules.routing.router import Router


class RouterMaker:
    """
    Class for specific service path, that will generate routes for the
    service. For example: you have services data-service and image-service, so
    each of them has some routes, all that you need it is just type service
    host. For now, you can create as much as you need numbers of
    endpoints.
    """

    def __init__(self, service_host: str) -> None:
        """
        Class constructor.
        :param service_host: Receives part of url.
            For example, if main url looks like that:
            https://google.com/api-service/v1/some-endpoint
            router should have that part - api-service/v1
            After it u can easily make any endpoints on that url
        """
        self.service_host = service_host

    def _build_url(self, route: str) -> str:
        """
        Builds url from all parts of received data.
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
        :param router_validation_key: value that will be used as validation
        key for validator method. If something has been populated for
        project key validation in config, router validation key will have
        the highest priority and will be applied to validation.
        :param route: String. Example /some-endpoint
        :return: Router object
        """
        path = self._build_url(route)
        return Router(path=path, router_validation_key=router_validation_key)
