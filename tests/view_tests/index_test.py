import pytest
from pizza.orders import models


@pytest.fixture
def add_pizzas(clean_db, db_session):
    for name, price in [("funghi", 849), ("margherita", 799)]:
        pizza = models.Pizza(name=name, price=price)
        db_session.add(pizza)


def test_title(app):
    resp = app.get("/")
    html = resp.html
    assert html.title.string == "Pizza Shop"


def test_form_is_post(app):
    resp = app.get("/")
    form = resp.form
    assert form.method == "POST"


def test_form_action(app):
    resp = app.get("/")
    form = resp.form
    assert form.action == "/"


def test_form_has_submit_button(app):
    resp = app.get("/")
    form = resp.form
    assert "submit" in form.fields


def test_pizzas_are_displayed(app, add_pizzas):
    resp = app.get("/")
    form = resp.form
    expected_names = frozenset(["margherita", "funghi"])
    names = {v.name for v, in form.fields.values() if v.name != "submit"}
    assert names >= expected_names
