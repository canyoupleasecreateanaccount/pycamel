
class Filter:

    @classmethod
    def _prepare_array(cls, filter_in_items: list) -> str:
        if len(filter_in_items) == 1:
            return str(filter_in_items)
        filter_result = ""
        for index, item in enumerate(filter_in_items[:-1]):
            filter_result += f"{item},"
        filter_result += str(filter_in_items[-1])
        return filter_result

    @classmethod
    def build_filter(cls, filters: dict) -> str:
        final_filter_row = ""
        for item in filters.keys():
            final_filter_row += f"&{item}={filters[item]}"
        final_filter_row = final_filter_row[:0] + "?" + final_filter_row[1:]
        return final_filter_row
