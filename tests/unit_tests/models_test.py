import contextlib
import re

import pytest
from pizza.orders import models
from sqlalchemy import exc, orm


@pytest.fixture
def patch_models_init(monkeypatch):
    # We monkeypatch engine and Session here because they get set
    # by the top-level database fixture.
    monkeypatch.setattr(models, "engine", None)
    monkeypatch.setattr(models, "Session", None)
    models.init("sqlite://")


@pytest.mark.usefixtures("patch_models_init")
class TestInit:
    """Test cases for the orm init function."""

    def test_sets_engine_on_module(self, monkeypatch):
        assert models.engine.name == "sqlite"

    def test_sets_session_factory_on_module(self, monkeypatch):
        assert isinstance(
            models.Session, orm.scoping.scoped_session
        ), f"Session is a {type(models.Session)}."

    def test_binds_engine_to_session_factory(self, monkeypatch):
        assert models.Session.bind == models.engine


@pytest.mark.usefixtures("clean_db")
class TestOrder:
    def test_sets_reference_when_initialised(self):
        order = models.Order()
        assert re.fullmatch(r"[A-Za-z]{6}", order.reference)


def f():
    session = models.Session()
    pizza = models.Pizza(name="not-a-pizza", price=749)
    session.add(pizza)


def g():
    session = models.Session()
    pizza = models.Pizza(name="also-not-a-pizza", price=749)
    session.add(pizza)
    raise RuntimeError("Oops!")


@pytest.mark.usefixtures("clean_db")
class TestSessionManager:
    def test_commits_changes(self):
        npizzas = 1
        models.manage_session(f)()
        session = models.Session()
        count_pizzas = session.query(models.Pizza).filter_by(name="not-a-pizza").count()
        assert npizzas == count_pizzas

    def test_rolls_back_changes_on_error(self):
        npizzas = 0
        with contextlib.suppress(RuntimeError):
            models.manage_session(g)()
        session = models.Session()
        count_pizzas = (
            session.query(models.Pizza).filter_by(name="also-not-a-pizza").count()
        )
        assert npizzas == count_pizzas


@pytest.mark.usefixtures("clean_db")
class TestPizza:
    def test_names_are_unique(self, db_session):
        ps = [models.Pizza(name="A") for _ in range(2)]
        db_session.add_all(ps)
        with pytest.raises(exc.IntegrityError):
            db_session.commit()
