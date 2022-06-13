from typing import List, Any

import requests
from json import JSONDecodeError

from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError
from pycamel.src.modules.core.validator import Validator

from pycamel.src.utils.searcher import search_item, prepare_items
from pycamel.src.utils.search_key_processor import search_key_processor


class CamelResponse:

    def __init__(
            self,
            response: requests.Response,
            headers: dict,
            router_validation_key: str = None
    ) -> None:
        self.router_validation_key = router_validation_key
        self.response = response
        self.headers = headers
        self.validated_objects = []
        try:
            self.response_data = response.json()
        except JSONDecodeError:
            self.response_data = {}

    def assert_status_code(
            self,
            expected_status_code: List[int]
    ) -> 'CamelResponse':
        if not isinstance(expected_status_code, List):
            raise ValueError("Expected list of integers")
        else:
            assert self.response.status_code in expected_status_code, self
            return self

    def get_response_json(self) -> dict:
        return self.response_data

    def validate(
            self,
            schema: BaseModel,
            response_validation_key: str = None
    ) -> 'CamelResponse':
        validation_key = search_key_processor(
            self.router_validation_key, response_validation_key
        )
        try:
            self.validated_objects = Validator(
                schema, self.response_data, validation_key
            ).fetch()
            return self
        except ValidationError as validation_exception:
            raise AssertionError(
                "Received objects could not be mapped to schema"
            ) from validation_exception

    def assert_parameter(
                self,
                parameter: str,
                expected_value: Any
    ) -> 'CamelResponse':
        params_iterator = search_item(self.response_data, parameter)
        while True:
            try:
                item = params_iterator.__next__()
                assert item == expected_value, self
            except StopIteration:
                break
        return self

    def get_items_by_key(self, parameter: str) -> List:
        return prepare_items(self.response_data, parameter)

    def get_validated_objects(self) -> List:
        return self.validated_objects

# TODO Refactor error log. Split request and response data.
# TODO Add to error log request body if it was sent.
    def __str__(self) -> str:
        return f"\n\nRequest sent to: {self.response.url}\n" \
               f"Response status code: {self.response.status_code}\n" \
               f"Response data: {self.response_data}\n" \
               f"Headers: {self.headers}\n" \
               f"Request time took: {self.response.elapsed}"
