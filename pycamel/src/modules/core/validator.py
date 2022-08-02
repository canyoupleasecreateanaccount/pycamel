from typing import List, Any, Union

from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError

from pycamel.src.errors.ValidationErrors import (
    AbsentValidationItems, IncorrectValidationPath
)


class Validator:
    """
    Class responses for validation received object according to pydantic
    schema. After success validation gives possibility to get parsed
    instances of pydantic model with all data.
    """
    def __init__(
            self,
            schema,
            response_data: dict,
            validation_key: str = None
    ) -> None:
        """
        Constructor of validator.
        :param schema: Pydantic schema. BaseModel that will be applied
            to received data from BE for validation.
        :param response_data: Data received from BE
        :param validation_key: Validation key for getting concreate value from
            response data. Same parameter has CamelConfig class. Natively
            receiving this parameter in constructor has highly priority than
            parameter filled in the CamelConfig.
            For example: if you have dict like that:
            {"data": {"some": "data"}}, you can fill validation key with
            "data" value, so as a result, pydantic schema will be applied to
            the part of dict {"some": "data"}.
        """
        self.schema = schema
        self.response_data = response_data
        self.validation_key = validation_key

    def _iterator(
            self,
            searching_key: str,
            data_to_search: dict = None
    ) -> [None, dict, list]:
        """
        Recursive method that try to detect part of object that should be
        validated according to received key. In case when key is absent,
        returns None.
        :param searching_key: string that equal to searching key in dict
        :param data_to_search: dict with data
        :return: return data according to searching key. If key is absent,
            returns None.
        """
        if data_to_search is None:
            data_to_search = self.response_data
        if isinstance(data_to_search, dict):
            for key in data_to_search:
                if key == searching_key:
                    return data_to_search.get(key)
                elif isinstance(data_to_search.get(key), dict):
                    self._iterator(searching_key, data_to_search.get(key))
        return None

    def _data_searcher(self) -> Any:
        """
        According to set keys, try to get data from response data.
        If search key has been populated with more than 2 values, we try to
        get it without searching around of all data, if not, try to find needed
        data in dict by key.
        :return: Data for validation.
        """
        path = self.validation_key.split(':')
        if len(path) > 1:
            result = self.response_data
            for path_item in path:
                try:
                    result = result.get(path_item)
                except AttributeError as exception:
                    raise IncorrectValidationPath(
                        f"Check path to validation item. "
                        f"Current it isn't correct: {path}"
                    ) from exception
        else:
            result = self._iterator(*path)
        return result

    def _validate(self, data_to_validate: Union[dict, list]) -> List[BaseModel]:
        """
        Method applies pydantic schema for data_to_validate object. In case
        when it is an array, method will apply schema to each array item
        in loop. If data_to_validate will be equal to one of [], {}, None value
        it will raise AbsentValidationItems exception.

        :param data_to_validate: It could be dict or list.
        :return: list of instances of pydantic class BaseModel
        """
        result = []
        if data_to_validate not in ([], {}, None):
            if isinstance(data_to_validate, list):
                for item in data_to_validate:
                    result.append(self.schema.parse_obj(item))
            elif isinstance(data_to_validate, dict):
                result.append(self.schema.parse_obj(data_to_validate))
        else:
            raise AbsentValidationItems(
                'Nothing has been passed for validation.'
                'Validation data should not be equal to None, {} or []'
            )
        return result

    def fetch(self) -> List[BaseModel]:
        """
        Method that applies validation.
        :return: List of instances of class BaseModel
        """
        if self.validation_key is not None:
            data_to_validate = self._data_searcher()
        else:
            data_to_validate = self.response_data
        try:
            initiated_objects = self._validate(data_to_validate)
            return initiated_objects
        except ValidationError as exception:
            raise AssertionError(
                f"\n\nException: {exception}"
                f"\nData passed to validator: {data_to_validate}"
                f"\nValidation schema: {self.schema.schema_json()}"
            ) from exception
