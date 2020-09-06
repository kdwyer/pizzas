import random

import bottle
import pytest
from pizza.orders import models

bottle.DEBUG = True


@pytest.fixture(scope="function")
def add_pizzas(clean_db, db_session):
    pizza_data = [("funghi", 849), ("margherita", 799)]
    topping_data = [("gorgonzola", 100), ("scamorza", 200)]
    pizzas = [models.Pizza(name=name, price=price) for (name, price) in pizza_data]
    toppings = [
        models.Topping(name=name, price=price) for (name, price) in topping_data
    ]
    db_session.add_all(pizzas)
    db_session.add_all(toppings)
    p1, p2 = pizzas
    t1, t2 = toppings
    random.seed(42)
    order = models.Order()
    order.items = [models.Item(pizza=p) for p in pizzas]
    order.items.append(models.Item(pizza=p1, topping=t2))
    order.items.append(models.Item(pizza=p2, topping=t1))
    order.items.append(models.Item(pizza=p2, topping=t2))
    db_session.add(order)


def test_contains_expected_html(app, add_pizzas):
    resp = app.get("/display-order/OhbVrp/")
    html = resp.html
    assert html.title.string == "Pizza Shop"
    assert html.find("p", id="confirmation-title").string == "your order"
    # FIXME duplicated in func test.
    reference = html.find("span", id="order-reference").string
    assert reference.isalpha()
    assert len(reference) == 6
    assert html("ul")
    total = html.find("p", id="total")
    assert total.find("span").string == "21.48"


def test_contains_order_details(app, add_pizzas):
    resp = app.get("/display-order/OhbVrp/")
    html = resp.html
    item_names = html.find_all("span", class_="line-item-name")
    assert item_names[0].string == "funghi"
    assert item_names[1].string == "scamorza"
    assert item_names[2].string == "margherita"
    assert item_names[3].string == "gorgonzola"
    assert item_names[4].string == "scamorza"
    item_prices = html.find_all("span", class_="line-item-price")
    assert item_prices[0].string == "8.49"
    assert item_prices[1].string == "2.00"
    assert item_prices[2].string == "7.99"
    assert item_prices[3].string == "1.00"
    assert item_prices[4].string == "2.00"
    total = html.find("p", id="total")
    assert total.find("span").string == "21.48"
