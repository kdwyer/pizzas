import webtest

import pizza


app = webtest.TestApp(pizza.application)


def test_title():
    resp = app.get("/")
    html = resp.html
    assert html.title.string == "Pizza Shop"
