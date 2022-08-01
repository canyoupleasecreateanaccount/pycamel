from typing import Any

import requests

from pycamel.src.modules.core.filter import Filter
from pycamel.src.modules.response.response import CamelResponse


class Router:
    """
    Default router class that gives possibility to send requests as it
    implemented in base requests lib, but with some additionally functionality.
    """
    def __init__(self, path: str, router_validation_key: str = None) -> None:
        """
        :param path: Concreate router path. For example /users
        :param router_validation_key: Key that will be used for each request
        and type of request under that route for .validate method.
        """
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
        :return: Result of execution _fetch method. CamelResponse class.
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
        :return: Result of execution _fetch method. CamelResponse class.
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
        :return: Result of execution _fetch method. CamelResponse class.
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
        :return: Result of execution _fetch method. CamelResponse class.
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
        :return: Result of execution _fetch method. CamelResponse class.
        """
        self._execution_method = requests.delete
        return self._fetch(*args, **kwargs)

    def add_to_path(self, parameter: str) -> 'Router':
        """
        Method adds to request path any received string.
        For example, if you need to send request to localhost/api/users/12
        all that you have to do it just .add_to_path('/12').
        :param parameter: Any string.
        :return: returns self
        """
        self.request_path += parameter
        return self

    def set_headers(self, headers: dict) -> 'Router':
        """
        Method switch default application/json header to received dict with
        headers.
        :param headers: dictionary with needed headers.
        :return: returns self
        """
        self.request_headers = headers
        return self

    def set_filters(self, filters: dict) -> 'Router':
        """
        Method receives dictionary with needed filters, transform it into string
        and add to request url. For example: base url is localhost/api/users,
        and you set filters {"page": 1}, for now your request url will be
        localhost/api/users?page=1
        :param filters: dictionary with filters
        :return: returns self
        """
        self.request_path += Filter.build_filter(filters)
        return self

    def append_header(self, header_key: str, header_value: Any) -> 'Router':
        """
        Method appends to default headers, received key and value.
        For example: default header is {'Content-Type': 'application/json'},
        after append header key-APP, value-TEST, it will look like
        {'Content-Type': 'application/json', 'APP': 'TEST'}.
        :param header_key: any string value
        :param header_value: any value
        :return: returns self
        """
        self.request_headers[header_key] = header_value
        return self

    def _clear(self) -> None:
        """
        Method updates router object to default after each fetched request.
        :return: Nothing
        """
        self.request_path = self.path
        self.request_headers = self.headers

    def _fetch(self, *args, **kwargs) -> CamelResponse:
        """
        Method receives any default values from requests lib and push them into
        execution method. After request execution it returns CamelResponse.
        :param args: Any
        :param kwargs: Any
        :return: CamelResponse
        """
        response = self._execution_method(
            url=self.request_path,
            headers=self.request_headers,
            *args,
            **kwargs
        )
        _previous_headers = self.request_headers
        self._clear()
        return CamelResponse(
            response=response,
            headers=_previous_headers,
            router_validation_key=self.router_validation_key
        )
