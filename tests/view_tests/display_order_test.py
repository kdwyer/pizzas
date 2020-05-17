import pytest

from pizza.orders import models


@pytest.fixture(autouse=True)
def set_engine():
    models.init("sqlite:///")
    models.Base.metadata.create_all(bind=models.engine)
    models.Session.configure(bind=models.engine)
    yield
    models.engine.dispose()


@pytest.fixture
def add_pizzas():
    session = models.Session()
    for name, price in [("funghi", 849), ("margherita", 799)]:
        pizza = models.Pizza(name=name, price=price)
        session.add(pizza)
    session.commit()
    models.Session.remove()


def test_contains_expected_html(app):
    resp = app.get("/display-order/")
    html = resp.html
    assert html.title.string == "Pizza Shop"
    assert html.find("p", id="confirmation-title").string == "your order"
    assert html("ul")
    total = html.find("p", id="total")
    assert total.find("span").string == "0.00"


def test_contains_order_details(app, add_pizzas):
    resp = app.get("/display-order/?name=margherita&name=funghi")
    html = resp.html
    item_names = html.find_all("span", class_="line-item-name")
    assert item_names[0].string == "funghi"
    assert item_names[1].string == "margherita"
    item_prices = html.find_all("span", class_="line-item-price")
    assert item_prices[0].string == "8.49"
    assert item_prices[1].string == "7.99"
    total = html.find("p", id="total")
    assert total.find("span").string == "16.48"
