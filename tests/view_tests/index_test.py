import webtest

import pizza


app = webtest.TestApp(pizza.application)


def test_title():
    resp = app.get("/")
    html = resp.html
    assert html.title.string == "Pizza Shop"


def test_form_is_post():
    resp = app.get("/")
    form = resp.form
    assert form.method == "POST"


def test_form_action():
    resp = app.get("/")
    form = resp.form
    assert form.action == "/"


def test_form_has_submit_button():
    resp = app.get("/")
    form = resp.form
    assert "submit" in form.fields


def test_pizzas_are_displayed():
    resp = app.get("/")
    form = resp.form
    expected_names = frozenset(["margherita", "bianca"])
    names = {v.name for v, in form.fields.values() if v.name != "submit"}
    assert names >= expected_names
