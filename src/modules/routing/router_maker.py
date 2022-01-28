import os

from src.modules.routing.router import Router


class RouterMaker:

    def __init__(self, service_host: str) -> None:
        self.service_host = service_host

    def _build_url(self, route: str) -> str:
        host = os.environ.get('pc_host')
        return f"{host}{self.service_host}{route}"

    def make_router(self, route: str) -> Router:
        path = self._build_url(route)
        return Router(path=path)
