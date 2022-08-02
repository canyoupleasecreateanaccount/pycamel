Change log
----------

v1.0.2
------

# Added exception for case when nothing has been passed to validate method (response.validate) and for (assert_parameter)
  For example: If you received empty object from backend and apply for it validation schema
  you will get AbsentValidationItems exception

# Added validation parameters to .assert_parameter method
    For now, you can apply filter during asserting some parameter
    List of filters:

        EQUAL = '_eq'

        IN = '_in'

        LOWER_THAN = '_lt'

        GREATER_THAN = '_gt'

        LOWER_OR_EQUAL = '_le'

        GREATER_OR_EQUAL = '_ge'

    For example, you need to check, that all items from backend after filtering
    has statuses ['ACTIVE', 'BLOCKED'], just type
    ``` .assert_parameter("status", ['ACTIVE', 'BLOCKED'], '_in') ```
    Default parameter for filter is '_eq'

# Fixed description for methods and classes of pycamel package
    For now each package, method, function and class has actual description.

# Fixed issue with recursion
    It happens when object doesn't have any sub objects like arrays or dictionaries during execution of .validate method

# Fixed tests and added additional coverage
    Added some additional cases for package cover and added description for each autotest.