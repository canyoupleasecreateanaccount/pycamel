from pycamel.src.utils.camel_enum import CamelEnum


class AssertConditions(CamelEnum):
    """
    List of possible variants of assertions for .assert_parameter method.
    """
    EQUAL = '_eq'
    IN = '_in'
    LOWER_THAN = '_lt'
    GREATER_THAN = '_gt'
    LOWER_OR_EQUAL = '_le'
    GREATER_OR_EQUAL = '_ge'
