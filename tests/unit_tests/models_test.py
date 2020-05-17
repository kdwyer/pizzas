from sqlalchemy import orm
from pizza import models


class TestInit:
    """Test cases for the orm init function."""

    def test_sets_engine_on_module(self, monkeypatch):
        # FIXME not sure why we need to monkeypatch here
        # maybe another fixture is run before this test?
        monkeypatch.setattr(models, "engine", None)
        models.init("sqlite:///")
        assert models.engine.name == "sqlite"

    def test_sets_session_factory_on_module(self, monkeypatch):
        # FIXME not sure why we need to monkeypatch here
        # maybe another fixture is run before this test?
        monkeypatch.setattr(models, "engine", None)
        monkeypatch.setattr(models, "Session", None)
        models.init("sqlite:///")
        assert isinstance(
            models.Session, orm.scoping.scoped_session
        ), f"Session is a {type(models.Session)}."

    def test_binds_engine_to_session_factory(self, monkeypatch):
        # FIXME not sure why we need to monkeypatch here
        # maybe another fixture is run before this test?
        monkeypatch.setattr(models, "engine", None)
        monkeypatch.setattr(models, "Session", None)
        models.init("sqlite:///")
        assert models.Session.bind == models.engine
