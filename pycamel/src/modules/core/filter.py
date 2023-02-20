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
            return str(filter_in_items[0])
        return ','.join(str(item) for item in filter_in_items)

    @classmethod
    def build_filter(cls, filters: dict) -> str:
        """
        Creates url filter according to received dict.
        For example: {"age": 22, "gender": "male", "name_in": ["Inna", "Erich"]}
        to "?age=22&gender=male&name_in=Inna,Erich"

        :param filters: Dict with filter items.
        :return: Prepared filter string like that "?age=22&gender=male".
        """
        filter_items = []
        for item, value in filters.items():
            filter_item = cls._prepare_array(value) \
                if isinstance(value, list) else str(value)
            filter_items.append(f"{item}={filter_item}")
        return '?' + '&'.join(filter_items) if filter_items else ''
