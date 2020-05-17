import pytest
import webtest

import pizza


@pytest.fixture(scope="module")
def app():
    return webtest.TestApp(pizza.application)
