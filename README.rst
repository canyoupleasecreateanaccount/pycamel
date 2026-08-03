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


Timeouts and retries
--------------------

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
------------------------

.. code-block:: python

    response = statistic_route.get()
    response.assert_response_time(2)  # fails if the response took over 2s

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
