from urllib.parse import quote


class Filter:
    """
    Aggregation class for functions that works with filtering and filter
    generation.
    """
    @classmethod
    def _prepare_array(cls, filter_in_items: list) -> str:
        """
        Method for deserializing array of Any to string, percent-encoding
        each item individually so a comma inside an item's own value is
        never confused with the comma used to separate array items.
        For example: List[1,2,3,4,5,] -> Str "1,2,3,4,5"
        :param filter_in_items: List of items
        :return: String row with concatenation of all array items.
        """
        return ",".join(quote(str(item), safe='') for item in filter_in_items)

    @classmethod
    def build_filter(cls, filters: dict) -> str:
        """
        Creates url filter according to received dict. Keys and values are
        percent-encoded, so characters like '&', '=', '#' or spaces in a
        filter value cannot corrupt the query string or inject extra
        parameters; the comma used to join array values is left unencoded.
        For example: {"age": 22, "gender": "male", "name_in": ["Inna", "Erich"]}
        to "?age=22&gender=male&name_in=Inna,Erich"

        :param filters: Dict with filter items.
        :return: Prepared filter string like that "?age=22&gender=male".
        """
        parts = []
        for key, value in filters.items():
            filter_value = (
                cls._prepare_array(value) if isinstance(value, list)
                else quote(str(value), safe='')
            )
            parts.append(f"{quote(str(key), safe='')}={filter_value}")
        return "?" + "&".join(parts)
