Change log
----------
v2.1.0
------
Fixes:

# Fixed CamelConfig silently leaking stale settings between instances
  ``CamelConfig(...)`` stored its settings as env variables and only ever
  added to them, so a parameter left out of a later ``CamelConfig(...)``
  call (for example switching to a second service/host in the same
  process) used to keep whatever an earlier call had configured -
  ``retries``, ``backoff_factor``, ``default_timeout``,
  ``project_validation_key`` and ``auth_provider`` included. Each
  ``CamelConfig(...)`` call now fully replaces the previous configuration;
  a parameter left as ``None`` clears the matching setting instead of
  leaving it stale.

# Fixed Filter.build_filter not percent-encoding keys/values
  ``.set_filters({"q": "a&b=c d"})`` used to insert the value into the
  query string as-is, so characters like ``&``, ``=``, ``#`` or spaces
  could corrupt the URL or inject extra query parameters. Keys and values
  are now percent-encoded; the comma used to join array values (for
  example ``tag_in=[1, 2]`` -> ``tag_in=1,2``) is left unencoded.

# Fixed Router not clearing its state when ForbiddenParameter was raised
  Passing ``headers=``/``url=``/a positional argument to ``.get()``/
  ``.post()``/etc. raised ``ForbiddenParameter`` before the router's
  ``request_path``/``request_headers`` were reset, unlike every other
  failure path. The router is now always cleared back to its defaults,
  regardless of which error caused the request to fail.

# Fixed Router not being safe to share across threads
  A single ``Router`` instance builds one request at a time in its own
  mutable state (``request_path``/``request_headers``), from the first
  builder call (``.add_to_path``/``.set_headers``/``.set_filters``/
  ``.append_header``) through the terminal ``.get``/``.post``/``.put``/
  ``.patch``/``.delete`` call. If the same router was shared across
  threads, one thread's builder calls could interleave with another's and
  corrupt the in-flight request. That build-then-send sequence is now
  automatically serialized per thread: a second thread's chain blocks
  until the first one's request has actually been sent.

# Fixed the built wheel/sdist shipping the test suite as an installable
  top-level ``tests`` package
  ``setup.py`` used ``find_packages()`` without excluding ``tests``, so
  every install of pycamel also installed a top-level ``tests`` package
  into site-packages - liable to collide with a project's own ``tests``
  package.

Added:

# Added CamelConfig.reset()
  Clears every setting previously configured via ``CamelConfig``,
  including the project-wide ``auth_provider``. Mainly useful in test
  suites/fixtures that need a clean slate between modules or services.

v2.0.0
------
Breaking changes:

# Migrated to pydantic v2
  ``pydantic<2`` is no longer supported, ``install_requires`` now pins
  ``pydantic>=2,<3``. If your own validation schemas rely on the pydantic v1
  behavior where ``Optional[X]`` without a default implicitly meant
  ``= None``, you now need to set that default explicitly
  (``Optional[X] = None``), otherwise the field becomes required.

# Raised minimum supported Python version to 3.10
  Python 3.9 reached end of life and current dependencies (pydantic,
  requests and the dev toolchain) already require Python >= 3.10.

Fixes:

# Fixed validation key search silently failing for nested keys
  ``.validate(schema, 'key')`` (a single key, no colon-delimited path) used
  to always return nothing when the key was nested more than one level
  deep, incorrectly raising ``AbsentValidationItems`` even though the data
  was present. Nested keys are now found the same way ``assert_parameter``
  and ``get_items_by_key`` already did.

# Fixed a crash when filtering by an empty list
  ``.set_filters({"tag": []})`` used to raise ``IndexError``. It now
  produces an empty filter value instead.

# Raised a clear error when a router is built before CamelConfig
  Building a router without first calling ``CamelConfig(host=...)`` used to
  silently produce a URL like ``None/users``. It now raises
  ``MissingConfigError`` with a clear message.

# Raised ForbiddenParameter instead of a confusing TypeError
  Passing a positional argument to ``.get()``/``.post()``/etc. used to
  crash with an unrelated ``TypeError`` from the underlying requests call.
  It now raises the same ``ForbiddenParameter`` used for url/headers misuse.

# Exported ForbiddenParameter and RequestException from the pycamel package
  They can now be imported directly, for example
  ``from pycamel import RequestException``.

Added:

# Added auth_provider for dynamic, refreshable authentication headers
  ``CamelConfig``/``RouterMaker.make_router``/``Router`` now accept an
  ``auth_provider`` - a zero-argument callable returning a dict of headers.
  It is called again before every single request, so it naturally supports
  token refresh. Configure it once on ``CamelConfig`` as a project-wide
  default, or per router/service. Headers it returns can still be
  overridden per request with ``.append_header``/``.set_headers``.

# Session reuse, configurable retries and default timeout
  Each router now reuses a ``requests.Session`` for connection pooling. You
  can set ``default_timeout``, ``retries`` and ``backoff_factor`` on
  ``CamelConfig`` as project-wide defaults, or override them per router via
  ``RouterMaker.make_router(...)``/``Router(...)``. Retries apply to
  502/503/504 responses only.

# Added CamelResponse.assert_response_time(max_seconds)
  Asserts that the response was received within max_seconds, based on the
  existing ``response.elapsed``.

# Added pycamel/py.typed marker
  The package now ships a ``py.typed`` marker for type checkers.

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
