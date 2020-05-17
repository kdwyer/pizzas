import pytest
import webtest

from pizza import orders


@pytest.fixture(scope="module")
def app():
    return webtest.TestApp(orders.application)
