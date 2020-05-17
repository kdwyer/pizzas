import bottle

from orders import models
from orders import shop

if __name__ == "__main__":
    models.init("postgresql+psycopg2:///orders")
    bottle.run(shop.app, host="localhost", port=8000, debug=True)
