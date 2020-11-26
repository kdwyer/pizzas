import typing

import bottle
import wtforms

from . import models

app = bottle.Bottle()
app.add_hook("after_request", models.remove_session)


# FIXME deprecation warning about absolute template paths.
@app.route("/", name="index", method=["GET", "POST"])
@models.manage_session
@bottle.jinja2_view("index", template_lookup=["pizza/orders/templates"])
def index():
    class Form(wtforms.Form):
        submit = wtforms.SubmitField()

    session = models.Session()
    pizzas = session.query(models.Pizza).order_by(models.Pizza.name).all()
    for pizza in pizzas:
        setattr(Form, pizza.name, wtforms.BooleanField(default=False))
    form = Form(bottle.request.POST)
    if bottle.request.method == "POST" and form.validate():
        selected = form.data.copy()
        del selected["submit"]
        drop = [k for k, v in selected.items() if not v]
        for k in drop:
            del selected[k]
        selected_pizzas = session.query(models.Pizza).filter(
            models.Pizza.name.in_(selected.keys())
        )
        order = models.Order()
        items = [models.Item(pizza=pizza) for pizza in selected_pizzas]
        order.items = items
        session.add(order)
        # Flush the session to ensure that order reference is unique.
        # FIXME we should handle recovering from a duplicate!
        session.flush()
        bottle.redirect(f"/display-order/{order.reference}/")
    return {
        "app": app,
        "title": "Pizza Shop",
        "form": form,
        "pizzas": {p.name: p for p in pizzas},
    }


@app.route("/display-order/<order_reference:re:[A-Za-z]{6}>/")
@models.manage_session
@bottle.jinja2_view("display-order", template_lookup=["pizza/orders/templates"])
def display_order(*, order_reference: str) -> typing.Dict[str, typing.Any]:
    session = models.Session()  # type: ignore[misc]
    order = (
        session.query(models.Order)
        .filter(models.Order.reference == order_reference)
        .one()
    )
    total = sum(i.pizza.price for i in order.items)
    order_items = sorted(order.items, key=lambda i: i.pizza.name)
    return {
        "title": "Pizza Shop",
        "total": total,
        "order_items": order_items,
        "reference": order_reference,
    }
