from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError
import os


class Validator:

    def __init__(self, schema: BaseModel, response_data: dict, validation_key: str = None):
        self.schema = schema
        self.response_data = response_data
        if validation_key is not None:
            self.validation_key = validation_key
        elif os.getenv("pc_project_validation_key") is not None:
            self.validation_key = os.getenv("pc_project_validation_key")
        else:
            self.validation_key = None

    def _iterator(self, searching_key, data_to_search=None):
        if data_to_search is None:
            data_to_search = self.response_data
        if isinstance(data_to_search, dict):
            for key in data_to_search:
                print(f"Key {key}, {searching_key}")
                if key == searching_key:
                    return data_to_search.get(key)
                self._iterator(searching_key, data_to_search.get(key))

    def _data_searcher(self):
        path = self.validation_key.split(':')
        if len(path) > 1:
            result = self.response_data
            for path_item in self.response_data:
                result = result.get(path_item)
        else:
            result = self._iterator(*path)
        return result

    def _validate(self, data_to_validate):
        result = []
        if isinstance(data_to_validate, list):
            for item in data_to_validate:
                result.append(self.schema.parse_obj(item))
        else:
            result.append(self.schema.parse_obj(data_to_validate))
        return result

    def fetch(self):
        if self.validation_key is not None:
            data_to_validate = self._data_searcher()
        else:
            data_to_validate = self.response_data
        try:
            initiated_objects = self._validate(data_to_validate)
            return initiated_objects
        except ValidationError as exception:
            raise AssertionError from exception





