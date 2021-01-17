import typing

import bottle
import sqlalchemy as sa

from . import forms, models

app = bottle.Bottle()
app.add_hook("after_request", models.remove_session)


# FIXME deprecation warning about absolute template paths.
@app.route("/", name="index", method=["GET", "POST"])
@models.manage_session
@bottle.jinja2_view("index", template_lookup=["pizza/orders/templates"])
def index():
    session = models.Session()
    form = forms.OrderForm(bottle.request.POST)
    if bottle.request.method == "POST" and form.validate():
        order = form.create_obj(session)
        session.flush()
        bottle.redirect(f"/display-order/{order.reference}/")
    q = session.execute(sa.select(models.Pizza.name).order_by(models.Pizza.name))
    names = [{"name": name} for (name,) in q]
    data = {"forms": names}
    if bottle.request.method == "POST":
        mf = form
    else:
        mf = forms.OrderForm(data=data)
    return {
        "app": app,
        "title": "Pizza Shop",
        "form": mf,
    }


@app.route("/display-order/<order_reference:re:[A-Za-z]{6}>/")
@models.manage_session
@bottle.jinja2_view("display-order", template_lookup=["pizza/orders/templates"])
def display_order(*, order_reference: str) -> typing.Dict[str, typing.Any]:
    session = models.Session()  # type: ignore[misc]
    order = (
        session.execute(
            sa.select(models.Order).where(models.Order.reference == order_reference)
        )
        .scalars()
        .one()
    )
    return {
        "app": app,
        "title": "Pizza Shop",
        "order": order,
    }
