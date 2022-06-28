def search_item(input_data, parameter):
    if isinstance(input_data, dict):
        for key, value in input_data.items():
            if key == parameter:
                yield value
            else:
                yield from search_item(value, parameter)
    elif isinstance(input_data, list):
        for item in input_data:
            yield from search_item(item, parameter)


def prepare_items(input_data, parameter):
    result = []
    params_iterator = search_item(input_data, parameter)
    while True:
        try:
            item = params_iterator.__next__()
            if isinstance(item, list):
                for i in item:
                    result.append(i)
            else:
                result.append(item)
        except StopIteration:
            break
    return result
