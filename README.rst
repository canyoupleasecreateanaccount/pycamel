pycamel
=======

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


Examples
--------
In the project you can find `examples <https://github.com/canyoupleasecreateanaccount/pycamel-examples>`_ of using the framework in test cases.


Contribution
------------
- Validate your code and run tests.

    There should be 100% pass rate and all your code should have a coverage by tests.

    Execute the commands below for getting the info about current code coverage

``coverage run -m pytest -s -v tests/``

and after it

``coverage report -m``


- Pylint

    Check if your code doesn't have any pylint errors.
- Submit your pull request

    In a pull request, describe your feature as clearly as possible and submit it, please.


Learn automation with us
-------------------------
Here you can find some youtube lessons about automation on python with
a common pytest framework and with pycamel. Enjoy it :)

https://www.youtube.com/c/SolveMeChannel

Donation
---------
For people who would like to support us. God bless U ^_^

``BSC20``

``0x3EC81929e06950322d5125d8e6CA834F3d9B21f8``

    DOGE | BNB | CAKE | ADA | BUSD