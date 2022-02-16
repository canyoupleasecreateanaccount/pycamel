import requests
from requests import JSONDecodeError

from src.modules.core.filter import Filter
from src.modules.response.response import CamelResponse
# TODO
# 2. Add console prints for executing if it is needed


class Router:

    def __init__(self, path: str) -> None:
        self.path = path
        self.headers = {'Content-Type': 'application/json'}

        self.request_path = path
        self.request_headers = self.headers

        self._execution_method = None

    def get(self, *args, **kwargs):
        self._execution_method = requests.get
        return self._fetch(*args, **kwargs)

    def post(self, *args, **kwargs):
        self._execution_method = requests.post
        return self._fetch(*args, **kwargs)

    def put(self, *args, **kwargs):
        self._execution_method = requests.put
        return self._fetch(*args, **kwargs)

    def patch(self, *args, **kwargs):
        self._execution_method = requests.patch
        return self._fetch(*args, **kwargs)

    def delete(self, *args, **kwargs):
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

    def _fetch(self, is_raw_response_needed=False, *args, **kwargs):
        response = self._execution_method(
            url=self.request_path,
            headers=self.request_headers, *args, **kwargs
        )
        self._clear()
        if is_raw_response_needed:
            try:
                return response.json()
            except JSONDecodeError:
                return {}
        else:
            return CamelResponse(
                response=response, headers=self.request_headers
            )
