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


def test_can_place_order(app, add_pizzas, add_toppings):
    """Test that an order can be placed, and displayed."""
    # 0. Setup
    add_pizzas
    add_toppings
    random.seed(42)
    # 1. Goes to page
    index = app.get("/")
    # 3. Select ONE pizza
    # 4. Select toppings
    form = index.forms[0]
    toppings = index.html.find_all("input", attrs={"name": "forms-0-toppings-toppings"})
    assert len(toppings) == 4
    assert form["forms-0-name"].value == "funghi"
    assert form["forms-1-name"].value == "margherita"
    assert form["forms-0-selected"].checked is False
    assert form["forms-1-selected"].checked is False
    form["forms-0-selected"] = True
    assert form["forms-0-selected"].checked is True
    form["forms-0-toppings-toppings"] = ["gorgonzola", "mozzarella", "scamorza"]
    assert form.get("forms-0-toppings-toppings", index=0).value
    assert form.get("forms-0-toppings-toppings", index=1).value
    assert not form.get("forms-0-toppings-toppings", index=2).value
    assert form.get("forms-0-toppings-toppings", index=3).value
    form["forms-0-selected"] = True
    assert form["forms-1-selected"].checked is False
    # 5. Submit order
    redir = form.submit("submit")
    # 6. Redirected to order confirmation
    assert redir.status_int == 302
    resp = redir.follow()
    # 7. Pizzas, toppings and  prices displayed.
    rhtml = resp.html
    items = rhtml.find_all("span", class_="line-item-name")
    expected_names = frozenset(["funghi", "scamorza", "gorgonzola", "mozzarella"])
    assert {item.string for item in items} == expected_names
    prices = rhtml.find_all("span", class_="line-item-price")
    expected_prices = frozenset(["8.49", "2.00", "1.00", "1.00"])
    assert {price.string for price in prices} == expected_prices
    # 8. Order reference is displayed.
    reference = rhtml.find("span", id="order-reference").string
    assert reference.isalpha()
    assert len(reference) == 6
