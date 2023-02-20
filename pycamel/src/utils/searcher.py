from typing import Any, List, Union, Generator


def search_item(input_data: Union[list, dict], parameter: str) -> Generator:
    """
    Function for searching all needed parameters across the received object.
    If nothing was found on top level, it tries to find target on low levels
    using recursion.
    :param input_data: List or dict with items that should be checked.
    :param parameter: Target key that we try to find across the object.
    :return: Returns generator.
    """
    if isinstance(input_data, dict):
        for key, value in input_data.items():
            if key == parameter:
                yield value
            else:
                yield from search_item(value, parameter)
    elif isinstance(input_data, list):
        for item in input_data:
            yield from search_item(item, parameter)


def prepare_items(input_data: Any, parameter: str) -> List:
    """
    Function collects all found items that passed parameter condition.
    :param input_data: List or dict with items that should be checked.
    :param parameter: Target key that we try to find across the object.
    :return: Returns list of accepted condition values.
    """
    result = []
    for item in search_item(input_data, parameter):
        if isinstance(item, list):
            result.extend(item)
        else:
            result.append(item)
    return result
