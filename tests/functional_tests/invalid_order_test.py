import random

import pytest
from pizza.orders import models


@pytest.fixture
def add_pizzas(db_engine, clean_db):
    data = [{"name": "funghi", "price": 849}, {"name": "margherita", "price": 799}]
    with db_engine.connect() as conn:
        with conn.begin():
            conn.execute(models.Pizza.__table__.insert(), data)


@pytest.fixture
def add_toppings(db_engine, clean_db):
    data = [
        {"name": "scamorza", "price": 200},
        {"name": "mozzarella", "price": 100},
        {"name": "gorgonzola", "price": 100},
        {"name": "mushrooms", "price": 50},
    ]
    with db_engine.connect() as conn:
        with conn.begin():
            conn.execute(models.Topping.__table__.insert(), data)


def test_displays_errors(app, add_pizzas, add_toppings):
    """Test that an order can be placed, and displayed."""
    # 0. Setup
    add_pizzas
    add_toppings
    random.seed(42)
    # 1. Goes to page
    index = app.get("/")
    # 2. Select toppings
    form = index.forms[0]
    toppings = index.html.find_all("input", attrs={"name": "forms-0-toppings-toppings"})
    assert len(toppings) == 4
    # Select toppings.
    form["forms-0-toppings-toppings"] = ["gorgonzola", "mozzarella", "scamorza"]
    assert form["forms-0-selected"].checked is False
    assert form.get("forms-0-toppings-toppings", index=0).checked
    assert form.get("forms-0-toppings-toppings", index=1).checked
    assert not form.get("forms-0-toppings-toppings", index=2).checked
    assert form.get("forms-0-toppings-toppings", index=3).checked
    assert form["forms-1-selected"].checked is False
    assert not form.get("forms-1-toppings-toppings", index=0).checked
    assert not form.get("forms-1-toppings-toppings", index=1).checked
    assert not form.get("forms-1-toppings-toppings", index=2).checked
    assert not form.get("forms-1-toppings-toppings", index=3).checked
    # 3. Submit order
    resp = form.submit("submit")
    # 4. Field contents are preserved
    form = resp.forms[0]
    toppings = resp.html.find_all("input", attrs={"name": "forms-0-toppings-toppings"})
    # Select toppings.
    form["forms-0-toppings-toppings"] = ["gorgonzola", "mozzarella", "scamorza"]
    assert form["forms-0-selected"].checked is False
    assert form.get("forms-0-toppings-toppings", index=0).checked
    assert form.get("forms-0-toppings-toppings", index=1).checked
    assert not form.get("forms-0-toppings-toppings", index=2).checked
    assert form.get("forms-0-toppings-toppings", index=3).checked
    assert form["forms-1-selected"].checked is False
    assert not form.get("forms-1-toppings-toppings", index=0).checked
    assert not form.get("forms-1-toppings-toppings", index=1).checked
    assert not form.get("forms-1-toppings-toppings", index=2).checked
    assert not form.get("forms-1-toppings-toppings", index=3).checked
    # TODO error message display
    errors = resp.html.find_all("p", "form-errors")
    assert len(errors) == 1
    assert errors[0].string == "You must select a pizza as well as toppings"
