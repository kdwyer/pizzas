def test_contains_expected_html(app):
    resp = app.get("/display-order/")
    html = resp.html
    assert html.title.string == "Pizza Shop"
    assert html.find("p", id="confirmation-title").string == "your order"
    assert html("ul")
    total = html.find("p", id="total")
    assert total.find("span").string == "0.00"


def test_contains_order_details(app):
    resp = app.get("/display-order/?name=margherita&name=bianca")
    html = resp.html
    item_names = html.find_all("span", class_="line-item-name")
    assert item_names[0].string == "margherita"
    assert item_names[1].string == "bianca"
    item_prices = html.find_all("span", class_="line-item-price")
    assert item_prices[0].string == "7.99"
    assert item_prices[1].string == "8.99"
    total = html.find("p", id="total")
    assert total.find("span").string == "16.98"
