import bottle
import wtforms


app = bottle.Bottle()


# FIXME deprecation warning about absolute template paths.
@app.route("/", name="index")
@bottle.jinja2_view("index", template_lookup=["pizza/templates"])
def index():
    pizzas = [("margherita", 799), ("bianca", 899)]

    class Form(wtforms.Form):
        submit = wtforms.SubmitField()

    for pizza, _ in pizzas:
        setattr(Form, pizza, wtforms.BooleanField())
    form = Form()
    return {"app": app, "title": "Pizza Shop", "form": form, "pizzas": pizzas}
