Change log
----------
v1.0.4
------
# Fixed issue with state clean when exception happens on send request stage
  In case when you send request to backend and get exception, for example TimeOut Error,
  state of route did not update, so as a result you can get wrong initial params for
  request properties.

v1.0.3
------
# Fixed docstring for REST API methods and added Exception
  There was a row that you can pass any params that accept requests lib, from now it is not a truth.
  You can not pass URL and header params to the REST method, these params could be changed or updated
  only by specific methods like .append_headers, .set_headers, etc.

# Added possibility to set default header for router
  From now, you can set the default header for any router, it could be useful for cases when you
  will test admin routes or routes with required AUTH headers for each request, so, you can just set it
  once for some route and enjoy.

# Added JSON and DATA params into Response report.
  From now, you can see additional useful information about your failed test because there
  will be presented json or/and data that has been sent to backend.

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
