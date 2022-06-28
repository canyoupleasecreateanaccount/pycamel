from typing import List, Any

from json import JSONDecodeError

import requests

from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError
from pycamel.src.modules.core.validator import Validator

from pycamel.src.utils.searcher import search_item, prepare_items
from pycamel.src.utils.search_key_processor import search_key_processor


class CamelResponse:
    """
    Class helps to work with default request.Response class.
    By default, parse some params from an object and as a result has
    functionality for validation.
    """
    def __init__(
            self,
            response: requests.Response,
            headers: dict,
            router_validation_key: str = None
    ) -> None:
        """
        :param response: Default response from requests lib.
        :param headers: requested headers needed for displaying in __str__
        inst representation.
        :param router_validation_key: validation key that has been set for
        router and will be used as default if another keys will not be sent.
        """
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
        """
        Validation method for response status code. Check that status code
        in list of expected status codes.
        :param expected_status_code: Receives array of status codes.
        :return: returns self
        """
        if not isinstance(expected_status_code, List):
            raise ValueError("Expected list of integers")
        assert self.response.status_code in expected_status_code, self
        return self

    def get_response_json(self) -> dict:
        """
        Method returns raw json response without any changes.
        :return: dict
        """
        return self.response_data

    def validate(
            self,
            schema: BaseModel,
            response_validation_key: str = None
    ) -> 'CamelResponse':
        """
        Method validates that to response data we can apply pydantic schema
        that has been sent to method.
        :param schema: Pydantic schema
        :param response_validation_key: Key for getting target data from
        response data. The key has the highest priority from another.
        :return: returns self
        """
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
        """
        Method for validation any parameters in body. It tries to find all
        params and compare it with expected value. Params can be parsed from
        different level of response json.
        :param parameter: Searched parameter
        :param expected_value: Expected value for it.
        :return: returns self
        """
        params_iterator = search_item(self.response_data, parameter)
        parameter_found = False
        while True:
            try:
                item = params_iterator.__next__()
                assert item == expected_value, self
                parameter_found = True
            except StopIteration:
                break
        if parameter_found is False:
            raise AssertionError(
                'Searched parameter is not presented in dictionary'
            )
        return self

    def get_items_by_key(self, parameter: str) -> List:
        """
        It is not validation method. It helps to get all values by key from
        response object with level ignore.
        :param parameter: Searched parameter.
        :return: returns list of values or empty list if nothing was found.
        """
        return prepare_items(self.response_data, parameter)

    def get_validated_objects(self) -> List:
        """
        If validation method ended with successful you can get all your
        validated objects that
        :return:
        """
        return self.validated_objects

    def __str__(self) -> str:
        """
        Sting representation of response that contains base info about request
        and response.
        :return: String info about class params.
        """
        return f"\n\nRequest sent to: {self.response.url}\n" \
               f"Response status code: {self.response.status_code}\n" \
               f"Response data: {self.response_data}\n" \
               f"Headers: {self.headers}\n" \
               f"Request time took: {self.response.elapsed}"
