import requests

from pycamel.src.modules.core.filter import Filter
from pycamel.src.modules.response.response import CamelResponse


class Router:

    def __init__(self, path: str, router_validation_key: str = None) -> None:
        self.path = path
        self.router_validation_key = router_validation_key
        self.headers = {'Content-Type': 'application/json'}

        self.request_path = path
        self.request_headers = self.headers

        self._execution_method = None

    def get(self, *args, **kwargs) -> CamelResponse:
        """
        Request method based on :class:`Request` of requests lib.
        Gets request method as object and makes request.
        :param args: Dictionary, list of tuples or bytes to send
        in the query string for the :class:`Request`.
        :param kwargs: Optional arguments that ``request`` takes.
        :return: Result of execution _fetch method. class CamelResponse.
        """
        self._execution_method = requests.get
        return self._fetch(*args, **kwargs)

    def post(self, *args, **kwargs) -> CamelResponse:
        """
        Request method based on :class:`Request` of requests lib.
        Gets request method as object and makes request.
        :param args: Dictionary, list of tuples or bytes to send
        in the query string for the :class:`Request`.
        :param kwargs: Optional arguments that ``request`` takes.
        :return: Result of execution _fetch method. class CamelResponse.
        """
        self._execution_method = requests.post
        return self._fetch(*args, **kwargs)

    def put(self, *args, **kwargs) -> CamelResponse:
        """
        Request method based on :class:`Request` of requests lib.
        Gets request method as object and makes request.
        :param args: Dictionary, list of tuples or bytes to send
        in the query string for the :class:`Request`.
        :param kwargs: Optional arguments that ``request`` takes.
        :return: Result of execution _fetch method. class CamelResponse.
        """
        self._execution_method = requests.put
        return self._fetch(*args, **kwargs)

    def patch(self, *args, **kwargs) -> CamelResponse:
        """
        Request method based on :class:`Request` of requests lib.
        Gets request method as object and makes request.
        :param args: Dictionary, list of tuples or bytes to send
        in the query string for the :class:`Request`.
        :param kwargs: Optional arguments that ``request`` takes.
        :return: Result of execution _fetch method. class CamelResponse.
        """
        self._execution_method = requests.patch
        return self._fetch(*args, **kwargs)

    def delete(self, *args, **kwargs) -> CamelResponse:
        """
        Request method based on :class:`Request` of requests lib.
        Gets request method as object and makes request.
        :param args: Dictionary, list of tuples or bytes to send
        in the query string for the :class:`Request`.
        :param kwargs: Optional arguments that ``request`` takes.
        :return: Result of execution _fetch method. class CamelResponse.
        """
        self._execution_method = requests.delete
        return self._fetch(*args, **kwargs)

    def add_to_path(self, parameter: str) -> 'Router':
        self.request_path += parameter
        return self

    def set_headers(self, headers):
        self.request_headers = headers
        return self

    def set_filters(self, filters: dict) -> 'Router':
        self.request_path += Filter.build_filter(filters)
        return self

    def append_header(self, header_key, header_value):
        self.request_headers[header_key] = header_value
        return self

    def _clear(self) -> None:
        self.request_path = self.path
        self.request_headers = self.headers

    def _fetch(self, *args, **kwargs) -> CamelResponse:
        response = self._execution_method(
            url=self.request_path,
            headers=self.request_headers,
            *args,
            **kwargs
        )
        self._clear()
        return CamelResponse(
            response=response,
            headers=self.request_headers,
            router_validation_key=self.router_validation_key
        )
