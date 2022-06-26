pycamel
=======

Quick start
-----------

- Firstly, init CamelConfig in main ``tests/conftest.py`` file

.. code-block:: python

    from pycamel import CamelConfig

    CamelConfig(host='https://localhost/')


This host will be used as a main project url.

For example, if you have a lot of services in your infrastructure

    - data-service
    - image-service

All of them will have same host, but different path according to service and their api versions

    - http://localhost/data-service/v1/
    - http://localhost/image-service/v1/
    - http://localhost/image-service/v2/

We recommend you create for each service separate sub folder under tests folder and init their
API maker

``tests/data_service/conftest.py``

.. code-block:: python

    from pycamel import RouterMaker

    data_service_maker_v1 = RouterMaker('/data-service/v1')

Same code should be for another services. For cases with different API versions (v1, v2, etc.) it is up to you
create different folders or make one for both of them but with two router makers for each version.

So, for now we ready to make some tests ^_^ Lets test endpoint on data-service.

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


In tests below we will check only status codes. More information about validation you can find in
example project or on official documentation.

Create file for our tests. ``tests/data_service/test_statistic.py``

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
- Validate of your code and run tests.

    There should be 100% pass rate and all of your code should have a coverage by tests.

    Execute commands below for get info about current coverage

``coverage run -m pytest -s -v tests/``

and after it

``coverage report -m``


- Pylint

    Check that your code doesn't have any pylint errors.
- Submit your pull request

    In pull request please, describe your feature as clearly as it possible and submit it.


Learn automation with us
-------------------------
Here is you can find youtube lessons about automation on python with 
common pytest framework and with pycamel. Enjoy it :)

https://www.youtube.com/c/SolveMeChannel

Donation
---------
For people, who would like to support us. God bless U ^_^

``BSC20``

``0x3EC81929e06950322d5125d8e6CA834F3d9B21f8``

    DOGE | BNB | CAKE | ADA | BUSD