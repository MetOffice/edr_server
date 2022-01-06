import tornado.ioloop
from tornado.web import Application

import collection
import items
import location
import position


def make_app():
    return Application([
        (r"/collections/(.*)/position", position.PositionHandler),
        (r"/collections/(.*)/locations", location.LocationsHandler),
        (r"/collections/(.*)/items", items.ItemsHandler),
        (r"/collections\/?", collection.CollectionsHandler),
    ])


if __name__ == "__main__":
    port = 8808
    print(f"Listening on port {port}...")
    app = make_app()
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()