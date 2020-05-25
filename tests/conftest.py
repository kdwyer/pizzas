import pytest
import webtest
from pizza import orders
from pizza.orders import models


@pytest.fixture(scope="module")
def app():
    return webtest.TestApp(orders.application)


@pytest.fixture(autouse=True)
def set_engine():
    models.init("sqlite:///")
    models.Base.metadata.create_all(bind=models.engine)
    models.Session.configure(bind=models.engine)
    yield
    models.engine.dispose()
