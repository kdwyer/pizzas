import typing
from urllib import parse

import bottle
import wtforms

from . import models


app = bottle.Bottle()


# FIXME deprecation warning about absolute template paths.
@app.route("/", name="index", method=["GET", "POST"])
@bottle.jinja2_view("index", template_lookup=["pizza/templates"])
def index() -> typing.Dict[str, typing.Any]:
    class Form(wtforms.Form):
        submit = wtforms.SubmitField()

    # mypy doesn't like that models.Session is None initially.
    session = models.Session()  # type: ignore[misc]
    pizzas = session.query(models.Pizza).order_by(models.Pizza.name).all()
    for pizza in pizzas:
        setattr(Form, pizza.name, wtforms.BooleanField(default=False))
    session.close()
    form = Form(bottle.request.POST)
    if bottle.request.method == "POST" and form.validate():
        selected = form.data.copy()
        del selected["submit"]
        drop = [k for k, v in selected.items() if not v]
        for k in drop:
            del selected[k]
        q = parse.urlencode([("name", name) for name in selected.keys()])
        bottle.redirect(f"/display-order/?{q}")
    return {
        "app": app,
        "title": "Pizza Shop",
        "form": form,
        "pizzas": {p.name: p for p in pizzas},
    }


@app.route("/display-order/")
@bottle.jinja2_view("display-order", template_lookup=["pizza/templates"])
def display_order() -> typing.Dict[str, typing.Any]:
    # mypy doesn't like that models.Session is None initially.
    session = models.Session()  # type: ignore[misc]
    names = bottle.request.query.getall("name")
    pizzas = (
        session.query(models.Pizza)
        .filter(models.Pizza.name.in_(names))
        .order_by(models.Pizza.name)
        .all()
    )
    session.close()
    total = sum(p.price for p in pizzas)
    return {"title": "Pizza Shop", "total": total, "order_items": pizzas}
