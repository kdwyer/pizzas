import bottle

import shop

if __name__ == "__main__":
    bottle.run(shop.app, host="localhost", port=8000, debug=True)
