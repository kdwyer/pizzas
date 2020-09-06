import collections.abc as cabc

import pytest
import webtest
from pizza.orders import models


@pytest.fixture
def add_pizzas(clean_db, db_session):
    for name, price in [("funghi", 849), ("margherita", 799)]:
        pizza = models.Pizza(name=name, price=price)
        db_session.add(pizza)


@pytest.fixture
def add_toppings():
    session = models.Session()
    for name, price in [
        ("scamorza", 200),
        ("mozzarella", 100),
        ("gorgonzola", 100),
        ("mushrooms", 50),
    ]:
        topping = models.Topping(name=name, price=price)
        session.add(topping)
    session.commit()
    models.Session.remove()


def test_title(app, clean_db):
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


def test_form_fields_are_displayed(app, add_pizzas, add_toppings):
    def flatten(list_):
        for el in list_:
            if isinstance(el, cabc.Iterable) and not isinstance(el, (str, bytes)):
                yield from flatten(el)
            else:
                yield el

    resp = app.get("/")
    form = resp.form
    expected_names = frozenset(["name", "selected", "toppings"])
    forms_values = flatten(form.fields.values())
    names = {v.name.rpartition("-")[2] for v in forms_values if v.name != "submit"}
    assert names >= expected_names
    prefixes = ("forms-0-", "forms-1-")
    # We should have one outer "form", and two inner forms
    for field in form.fields:
        if field == "submit":
            continue
        assert field.startswith(prefixes)
    # Each inner form has (pizza-)name, selected, toppings
    assert isinstance(form["forms-0-name"], webtest.forms.Text)
    assert form["forms-0-name"].value == "funghi"
    assert isinstance(form["forms-1-name"], webtest.forms.Text)
    assert form["forms-1-name"].value == "margherita"
    for prefix in prefixes:
        assert isinstance(form[f"{prefix}selected"], webtest.forms.Checkbox)
        assert not form[f"{prefix}selected"].value
        toppings = form.fields.get(f"{prefix}toppings-toppings")
        assert not toppings[0].value
        assert not toppings[1].value
        assert not toppings[2].value
        assert not toppings[3].value
    # Each toppings has gorgonzola/mozzarella/mushrooms/scamorza
    # Each pizza & topping label should include formatted price
