from typing import List

import requests
from requests import JSONDecodeError

from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError
from src.modules.core.validator import Validator


# TODO Add requested body into result of falling test

class CamelResponse:

    def __init__(
            self,
            response: requests.Response,
            headers: dict,
            router_validation_key: str = None
    ) -> None:
        self.response = response
        self.headers = headers
        self.validated_objects = []
        self.router_validation_key = router_validation_key
        try:
            self.response_data = response.json()
        except JSONDecodeError:
            self.response_data = {}

    def assert_status_code(
            self,
            expected_status_code: List[int]
    ) -> 'CamelResponse':
        assert self.response.status_code == expected_status_code, self
        return self

    def get_response_json(self) -> dict:
        return self.response_data

    def validate(
            self,
            schema: BaseModel,
            validation_key: str = None
    ) -> 'CamelResponse':
        if not validation_key:
            validation_key = self.router_validation_key
        try:
            self.validated_objects = Validator(
                schema, self.response_data, validation_key
            ).fetch()
            return self
        except ValidationError as validation_exception:
            raise AssertionError(
                "Received objects could not be mapped to schema"
            ) from validation_exception

    def get_validated_objects(self) -> list:
        return self.validated_objects

    def __str__(self) -> str:
        return f"\n\nRequest sent to: {self.response.url}\n" \
               f"Response status code: {self.response.status_code}\n" \
               f"Response data: {self.response_data}\n" \
               f"Headers: {self.headers}\n" \
               f"Request time took: {self.response.elapsed}"


# r = requests.get('https://www.ukr.net/ajax/currency.json?scr=9&_=1644425033014')
#
#
# z = CamelResponse(r, {})
# z.assert_status_code(200)
# print(r.__getstate__())
# print(r.elapsed)
