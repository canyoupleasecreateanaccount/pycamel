class Filter:
    """
    Aggregation class for functions that works with filtering and filter
    generation.
    """
    @classmethod
    def _prepare_array(cls, filter_in_items: list) -> str:
        """
        Method for deserializing array of Any to string.
        For example: List[1,2,3,4,5,] -> Str "1,2,3,4,5"
        :param filter_in_items: List of items
        :return: String row with concatenation of all array items.
        """
        if len(filter_in_items) == 1:
            return str(*filter_in_items)
        filter_result = ""
        for item in filter_in_items[:-1]:
            filter_result += f"{item},"
        filter_result += str(filter_in_items[-1])
        return filter_result

    @classmethod
    def build_filter(cls, filters: dict) -> str:
        """
        Creates url filter according to received dict.
        For example: {"age": 22, "gender": "male", "name_in": ["Inna", "Erich"]}
        to "?age=22&gender=male&name_in=Inna,Erich"

        :param filters: Dict with filter items.
        :return: Prepared filter string like that "?age=22&gender=male".
        """
        final_filter_row = ""
        for item in filters.keys():
            if isinstance(filters[item], list):
                filter_item = Filter._prepare_array(filters[item])
            else:
                filter_item = filters[item]
            final_filter_row += f"&{item}={filter_item}"
        final_filter_row = final_filter_row[:0] + "?" + final_filter_row[1:]
        return final_filter_row
