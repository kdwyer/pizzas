import typing
from urllib import parse

import bottle
import wtforms


app = bottle.Bottle()


pizzas: typing.List[typing.Tuple[str, int]] = [("margherita", 799), ("bianca", 899)]


# FIXME deprecation warning about absolute template paths.
@app.route("/", name="index", method=["GET", "POST"])
@bottle.jinja2_view("index", template_lookup=["pizza/templates"])
def index() -> typing.Dict[str, typing.Any]:
    class Form(wtforms.Form):
        submit = wtforms.SubmitField()

    for pizza, _ in pizzas:
        setattr(Form, pizza, wtforms.BooleanField(default=False))
    form = Form(bottle.request.POST)
    if bottle.request.method == "POST" and form.validate():
        selected = form.data.copy()
        del selected["submit"]
        drop = [k for k, v in selected.items() if not v]
        for k in drop:
            del selected[k]
        q = parse.urlencode([("name", name) for name in selected.keys()])
        bottle.redirect(f"/display-order/?{q}")
    return {"app": app, "title": "Pizza Shop", "form": form, "pizzas": dict(pizzas)}


@app.route("/display-order/")
@bottle.jinja2_view("display-order", template_lookup=["pizza/templates"])
def display_order() -> typing.Dict[str, typing.Any]:
    order_items = [
        (name, price)
        for name, price in pizzas
        if name in bottle.request.query.getall("name")
    ]
    total = sum(price for (_, price) in order_items)
    return {"title": "Pizza Shop", "total": total, "order_items": order_items}
