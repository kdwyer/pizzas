def test_can_place_order(app):
    # 1. goto page
    index = app.get("/")
    # 2. pizzas and prices displayed
    ihtml = index.html
    labels = ihtml("label")
    assert "Margherita" in [label.string for label in labels]
    prices = ihtml.find_all("span", class_="item-price")
    assert "7.99" in [price.string for price in prices]
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
