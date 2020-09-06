import bottle

if __name__ == "__main__":
    from orders import models

    # FIXME?
    models.init("postgresql+psycopg2:///orders")

    from orders import shop

    bottle.run(shop.app, host="localhost", port=8000, debug=True, reloader=True)
