import bottle


app = bottle.Bottle()


# FIXME deprecation warning about absolute template paths.
@app.route("/")
@bottle.jinja2_view("index", template_lookup=["pizza/templates"])
def index():
    return {"title": "Pizza Shop"}
