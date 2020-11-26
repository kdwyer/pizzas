"""
Global test config (pytest)

Most of the database session fixtures here are taken from / inspired
by https://stackoverflow.com/a/58662370/5320906
"""

import pytest
import webtest
from pizza import orders
from pizza.orders import models


@pytest.fixture(scope="module")
def app():
    return webtest.TestApp(orders.application)


def pytest_addoption(parser):
    parser.addoption(
        "--dburl",
        action="store",
        default="sqlite://",
        help="url of the database to use for tests",
    )


@pytest.fixture(scope="session")
def db_engine(request):
    """yields a SQLAlchemy engine which is suppressed after the test session"""
    db_url = request.config.getoption("--dburl")
    models.init(db_url)
    engine_ = models.engine

    yield engine_

    engine_.dispose()


@pytest.fixture(scope="function")
def clean_db(db_engine):
    """Drop and create tables."""
    models.Base.metadata.drop_all(bind=db_engine)
    models.Base.metadata.create_all(bind=db_engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Manage a session."""
    session_ = models.Session()

    yield session_

    session_.rollback()
    models.Session.remove()
