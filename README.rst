pycamel
=======

|unittest passing| |codecov badge| |pypi version| |pypi downloads| |pypi pyversions|

.. |unittest passing| image:: https://github.com/canyoupleasecreateanaccount/pycamel/actions/workflows/unittest.yml/badge.svg?branch=main
   :target: https://github.com/canyoupleasecreateanaccount/pycamel/actions/workflows/unittest.yml

.. |codecov badge| image:: https://codecov.io/gh/canyoupleasecreateanaccount/pycamel/branch/main/graph/badge.svg?token=70GAEA6ZXL
   :target: https://codecov.io/gh/canyoupleasecreateanaccount/pycamel

.. |pypi version| image:: https://badge.fury.io/py/pycamel.svg
   :target: https://badge.fury.io/py/pycamel

.. |pypi downloads| image:: https://img.shields.io/pypi/dm/pycamel.svg
   :target: https://pypi.org/project/pycamel/

.. |pypi pyversions| image:: https://img.shields.io/pypi/pyversions/pycamel.svg
   :target: https://pypi.org/project/pycamel/

Requirements
------------

Python >= 3.10 and pydantic >= 2 (as of v2.0.0). If you already have
pydantic schemas written for pydantic v1, note that
``Optional[SomeType]`` no longer implies a default of ``None`` in
pydantic v2 - you need to write ``Optional[SomeType] = None`` explicitly.

Install
-------

According to your version of pip type in console

``pip3 install pycamel``

or

``pip install pycamel``

Quick start
-----------

- First, init CamelConfig in the main ``tests/conftest.py`` file

.. code-block:: python

    from pycamel import CamelConfig

    CamelConfig(host='https://localhost/')


This host will be used as the main project url.

For example, if you have a lot of services in your infrastructure

    - data-service
    - image-service

all of them will have the same host, but different paths according to the services and their api versions

    - http://localhost/data-service/v1/
    - http://localhost/image-service/v1/
    - http://localhost/image-service/v2/

We recommend you to create a separate sub folder for each service under the tests folder and init API maker for them

``tests/data_service/conftest.py``

.. code-block:: python

    from pycamel import RouterMaker

    data_service_maker_v1 = RouterMaker('/data-service/v1')

The same code should be used for another services. For cases with different API versions (v1, v2, etc.) it is up to you
to create different folders or to make one for both of them but with a router maker for each version.

So, for now we are ready to make some tests ^_^ Let's test endpoint on the data-service.

Add some code into our ``tests/data_service/conftest.py``

``tests/data_service/conftest.py``

.. code-block:: python

    import pytest
    from pycamel import RouterMaker

    data_service_maker_v1 = RouterMaker('/data-service/v1')

    cats_statistic = data_service_maker_v1.make_router('/cats-statistic')

    @pytest.fixture(scope='session')
    def statistic_route():
        return cats_statistic


In the tests below we will check only status codes. More information about the validation you can find in
the example project or in the official documentation.

Create a file for our tests. ``tests/data_service/test_statistic.py``

.. code-block:: python

    import pytest

    def test_getting_statistic(statistic_route):
        response = statistic_route.get()
        response.assert_status_code([200])


    @pytest.mark.parametrize("page", [1, 2, 3])
    def test_getting_statistic_with_pagination(page):
        response = statistic_route.set_filters({"page": page}).get()
        response.assert_status_code([200])


Usage guide
-----------

Headers
~~~~~~~

Every router starts with the ``Content-Type: application/json`` header.
You can change it in three ways:

.. code-block:: python

    # 1. Set default headers once, when the router is created
    admin_users = data_service_maker_v1.make_router(
        '/admin/users', default_headers={"X-Role": "admin"}
    )

    # 2. Replace all headers for the next request only
    statistic_route.set_headers({"Accept": "application/xml"}).get()

    # 3. Add/override a single header for the next request only
    statistic_route.append_header("X-Request-Id", "abc-123").get()

``set_headers``/``append_header`` only apply to the next request - the
router resets back to its default headers right after the request is sent.

Filters and query params
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # localhost/api/users?age=22&gender=male&name_in=Inna,Erich
    statistic_route.set_filters({
        "age": 22,
        "gender": "male",
        "name_in": ["Inna", "Erich"]
    }).get()

Anything the ``requests`` library accepts as a keyword argument works too,
for example ``.get(params={"page": 1})``, ``.post(json={...})``,
``.post(data={...})``, ``.get(timeout=5)``. The only kwargs you cannot pass
directly are ``url`` and ``headers`` - use ``.add_to_path()``/
``.set_filters()`` and ``.set_headers()``/``.append_header()`` instead.

Validating a response against a pydantic schema
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from typing import Optional
    from pydantic import BaseModel

    class User(BaseModel):
        user_id: int
        first_name: Optional[str] = None
        last_name: str

    response = statistic_route.get()
    response.validate(User)               # validates response.json() as is
    response.validate(User, 'data')        # validates response.json()['data']
    response.validate(User, 'data:user')   # validates response.json()['data']['user']

    users = response.get_validated_objects()  # List[User]

If you pass a single key without ``:`` (like ``'data'`` above), pycamel
searches for that key at any nesting level of the response, so it does not
matter how deep it is - you don't need to know or repeat the full path. A
``:``-separated path (like ``'data:user'``) instead walks that exact path
step by step. If most of your endpoints share the same response envelope
(for example ``{"data": {...}}``), set it once instead of repeating it on
every ``.validate()`` call:

.. code-block:: python

    CamelConfig(host='https://localhost/', project_validation_key='data')

Asserting a specific parameter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``assert_parameter`` looks up a key anywhere in the response body (same
nested-key search as above) and compares every match against an expected
value:

.. code-block:: python

    response.assert_parameter("status", "ACTIVE")                 # ==
    response.assert_parameter("status", ["ACTIVE", "BLOCKED"], "_in")  # in
    response.assert_parameter("age", 18, "_ge")                    # >=

======  ==========================
Filter  Meaning
======  ==========================
_eq     equal (default)
_in     value is in expected list
_lt     lower than
_gt     greater than
_le     lower or equal
_ge     greater or equal
======  ==========================

Reading values without asserting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    ids = response.get_items_by_key("id")   # List of every "id" value found
    raw = response.get_response_json()      # Untouched response.json()

Authentication
~~~~~~~~~~~~~~

Most real backends require an auth token, and that token usually expires
during a long test run. ``auth_provider`` is a callable that pycamel calls
again right before every single request, so it naturally supports refresh -
just make the callable check/renew the token whenever it needs to.

.. code-block:: python

    import time
    import requests

    _token_cache = {"value": None, "expires_at": 0}

    def get_auth_headers():
        if time.time() >= _token_cache["expires_at"]:
            resp = requests.post(
                "https://localhost/auth/login",
                json={"login": "qa", "password": "qa"}
            ).json()
            _token_cache["value"] = resp["access_token"]
            _token_cache["expires_at"] = time.time() + resp["expires_in"]
        return {"Authorization": f"Bearer {_token_cache['value']}"}

    # Applied to every router in the project:
    CamelConfig(host='https://localhost/', auth_provider=get_auth_headers)

    # Or scoped to a single router/router maker:
    admin_users = data_service_maker_v1.make_router(
        '/admin/users', auth_provider=get_auth_headers
    )

Headers returned by ``auth_provider`` can still be overridden for a single
request with ``.append_header``/``.set_headers``, which always win.

Timeouts and retries
~~~~~~~~~~~~~~~~~~~~~

By default a router has no enforced timeout and does not retry failed
requests, matching earlier versions. You can configure sane defaults for
the whole project on ``CamelConfig``, and override them for a specific
router when needed.

.. code-block:: python

    from pycamel import CamelConfig, RouterMaker

    CamelConfig(
        host='https://localhost/',
        default_timeout=10,     # seconds, applied to every request
        retries=3,               # retried only on 502/503/504 responses
        backoff_factor=0.5
    )

    data_service_maker_v1 = RouterMaker('/data-service/v1')
    # overrides the project-wide defaults for this router only
    cats_statistic = data_service_maker_v1.make_router(
        '/cats-statistic', timeout=5, retries=0
    )

A request can still override the default timeout by passing ``timeout=``
explicitly, e.g. ``statistic_route.get(timeout=1)``. Requests made from the
same router reuse a single ``requests.Session``, so connections are pooled.

Response time assertion
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    response = statistic_route.get()
    response.assert_response_time(2)  # fails if the response took over 2s

Handling errors
~~~~~~~~~~~~~~~

All exceptions below can be imported directly from ``pycamel``.

- ``ForbiddenParameter`` - ``url``/``headers``/a positional argument was
  passed to ``.get()``/``.post()``/etc. instead of the dedicated
  ``.set_headers()``/``.append_header()`` methods.
- ``RequestException`` - the underlying ``requests`` call raised (timeout,
  connection error, exhausted retries, etc.).
- ``MissingConfigError`` - a router was built before
  ``CamelConfig(host=...)`` was called.
- ``AbsentValidationItems`` - ``.validate()``/``.assert_parameter()``
  received nothing to work with (``None``, ``{}`` or ``[]``).
- ``IncorrectValidationPath`` - a ``:``-separated validation key path does
  not match the response structure.
- ``IncorrectAssertParameter`` - an unknown filter (not one of ``_eq``/
  ``_in``/``_lt``/``_gt``/``_le``/``_ge``) was passed to
  ``.assert_parameter()``.

Examples
--------
In the project you can find `examples <https://github.com/canyoupleasecreateanaccount/pycamel-examples>`_ of using the framework in test cases.


- Pylint

    Check if your code doesn't have any pylint errors.
- Submit your pull request

    In a pull request, describe your feature as clearly as possible and submit it, please.


Learn automation with us
-------------------------
Here you can find some youtube lessons about automation on python with
a common pytest framework and with pycamel. Enjoy it :)

https://www.youtube.com/c/SolveMeChannel

It is ready to use backend API where you can practice with automation case writing.

``https://send-request.me/``

Contact us
----------

Email: ``solveme.solutions@gmail.com``

Telegram: ``https://t.me/automation_testing_with_solveme``

Donation
---------
For people who would like to support us. God bless U ^_^

``BSC20``

``0x3EC81929e06950322d5125d8e6CA834F3d9B21f8``

DOGE | BNB | CAKE | ADA | BUSD | TRX | MATIC | AVAX | ATOM | DIA | DOT
