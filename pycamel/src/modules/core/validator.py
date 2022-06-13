from typing import List

from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError


class Validator:
    """
    Class responses for validation received object according to pydantic
    schema. After success validation gives possibility to get parsed
    instance os pydantic base class with all sent data.
    """
    def __init__(
            self,
            schema: BaseModel,
            response_data: dict,
            validation_key: str = None
    ) -> None:
        """
        Constructor of validator.
        :param schema: Pydantic schema. class BaseModel that will be applied
            to received data from BE for validation it.
        :param response_data: data received from BE
        :param validation_key: Validation key for getting concreate value from
            response data. Same parameter has class CamelConfig. Natively
            receiving this parameter in constructor has highly priority than
            parameter filled in the CamelConfig.
            For example: if you have dict like that:
            {"data": {"some": "data"}}, you can fill validation key with
            "data" value, so as a result, pydantic schema will be applied to
            this part of dict {"some": "data"}.
        """
        self.schema = schema
        self.response_data = response_data
        self.validation_key = validation_key

    def _iterator(
            self,
            searching_key,
            data_to_search=None
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
                self._iterator(searching_key, data_to_search.get(key))
        return None

    def _data_searcher(self) -> dict:
        """
        According to set keys, try to get data from response data.
        If search key has been populated for more than 2 value, we try to
        get it without searching of around all data, if not, try to find needed
        data in dict by key.
        :return: Dict with concreate data for validation.
        """
        path = self.validation_key.split(':')
        if len(path) > 1:
            result = self.response_data
            for path_item in self.response_data:
                result = result.get(path_item)
        else:
            result = self._iterator(*path)
        return result

    def _validate(self, data_to_validate) -> List[BaseModel]:
        """
        Method check if data that he has is array or not, after it try
        to apply for each item pydantic schema. Instances of objects
        returns as array.
        :param data_to_validate: It could be dict or list.
        :return: list of instances of pydantic class BaseModel
        """
        result = []
        if isinstance(data_to_validate, list):
            for item in data_to_validate:
                result.append(self.schema.parse_obj(item))
        else:
            result.append(self.schema.parse_obj(data_to_validate))
        return result

    def fetch(self):
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
