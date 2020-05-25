import random

import pytest
from pizza.orders import models


@pytest.fixture
def add_pizzas():
    session = models.Session()
    for name, price in [("funghi", 849), ("margherita", 799)]:
        pizza = models.Pizza(name=name, price=price)
        session.add(pizza)
    session.commit()
    models.Session.remove()


def test_can_place_order(app, add_pizzas):
    # 0. Setup
    add_pizzas
    random.seed(42)
    # 1. goto page
    index = app.get("/")
    # 2. pizzas and prices displayed
    ihtml = index.html
    labels = ihtml("label")
    assert len(labels) == 2
    assert ["Funghi", "Margherita"] == [label.string for label in labels]
    prices = ihtml.find_all("span", class_="item-price")
    assert len(prices) == 2
    assert ["8.49", "7.99"] == [price.string for price in prices]
    # 2.1 select pizza
    form = index.forms[0]
    assert form["margherita"].checked is False
    form["margherita"] = True
    assert form["margherita"].checked is True
    # 3. submitted
    redir = form.submit("submit")
    # 4. redirect to order conf
    assert redir.status_int == 302
    resp = redir.follow()
    # 5. order & price displayed
    rhtml = resp.html
    items = rhtml.find_all("span", class_="line-item-name")
    assert len(items) == 1
    assert items[0].string == "margherita"
    prices = rhtml.find_all("span", class_="line-item-price")
    assert prices[0].string == "7.99"
    # 6. Order reference displayed.
    reference = rhtml.find("span", id="order-reference").string
    assert reference.isalpha()
    assert len(reference) == 6
