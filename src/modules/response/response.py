from typing import List

import requests
from requests import JSONDecodeError


# TODO Add requested body into result of falling test
# TODO Add request time


class CamelResponse:

    def __init__(self, response: requests.Response, headers: dict) -> None:
        self.response = response
        self.headers = headers
        try:
            self.response_data = response.json()
        except JSONDecodeError:
            self.response_data = {}

    def assert_status_code(self, expected_status_code: List[int]) -> 'CamelResponse':
        assert self.response.status_code == expected_status_code, self
        return self

    def __str__(self) -> str:
        return f"\n\nRequest sent to: {self.response.url}\n" \
               f"Response status code: {self.response.status_code}\n" \
               f"Response data: {self.response_data}\n" \
               f"Headers: {self.headers}"


r = requests.get('https://www.ukr.net/ajax/currency.json?scr=9&_=1644425033014')
print(r.__getstate__())
print(r.url)

z = CamelResponse(r, {})
z.assert_status_code(201)
