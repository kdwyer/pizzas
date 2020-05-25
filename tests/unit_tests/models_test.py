import contextlib
import re

from pizza.orders import models
from sqlalchemy import orm


class TestInit:
    """Test cases for the orm init function."""

    # We monkeypatch engine and Session here because they get set
    # by the top-level database fixture.

    def test_sets_engine_on_module(self, monkeypatch):
        monkeypatch.setattr(models, "engine", None)
        models.init("sqlite:///")
        assert models.engine.name == "sqlite"

    def test_sets_session_factory_on_module(self, monkeypatch):
        monkeypatch.setattr(models, "engine", None)
        monkeypatch.setattr(models, "Session", None)
        models.init("sqlite:///")
        assert isinstance(
            models.Session, orm.scoping.scoped_session
        ), f"Session is a {type(models.Session)}."

    def test_binds_engine_to_session_factory(self, monkeypatch):
        monkeypatch.setattr(models, "engine", None)
        monkeypatch.setattr(models, "Session", None)
        models.init("sqlite:///")
        assert models.Session.bind == models.engine


class TestOrder:
    def test_sets_reference_when_initialised(self, monkeypatch):
        order = models.Order()
        assert re.fullmatch(r"[A-Za-z]{6}", order.reference)


def f():
    session = models.Session()
    pizza = models.Pizza(name="margherita", price=749)
    session.add(pizza)


def g():
    session = models.Session()
    pizza = models.Pizza(name="margherita", price=749)
    session.add(pizza)
    raise RuntimeError("Oops!")


class TestSessionManager:
    def test_commits_changes(self, monkeypatch):
        npizzas = 1
        models.manage_session(f)()
        session = models.Session()
        count_pizzas = session.query(models.Pizza).count()
        assert npizzas == count_pizzas

    def test_removes_session_from_registry(self, monkeypatch):
        sid1 = id(models.Session())
        models.manage_session(f)()
        sid2 = id(models.Session())
        # If the original session has been removed, we should get a different id.
        assert sid1 != sid2

    def test_rolls_back_changes_on_error(self, monkeypatch):
        npizzas = 0
        with contextlib.suppress(RuntimeError):
            models.manage_session(g)()
        session = models.Session()
        count_pizzas = session.query(models.Pizza).count()
        assert npizzas == count_pizzas
