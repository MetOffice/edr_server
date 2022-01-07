import tornado.ioloop
from tornado.web import Application

import collection
import handlers


def make_app():
    return Application([
        (r"/collections/(.*)/area", handlers.AreaHandler),
        (r"/collections/(.*)/corridor", handlers.CorridorHandler),
        (r"/collections/(.*)/cube", handlers.CubeHandler),
        (r"/collections/(.*)/items", handlers.ItemsHandler),
        (r"/collections/(.*)/locations", handlers.LocationsHandler),
        (r"/collections/(.*)/position", handlers.PositionHandler),
        (r"/collections/(.*)/radius", handlers.RadiusHandler),
        (r"/collections/(.*)/trajectory", handlers.TrajectoryHandler),
        (r"/collections\/?", collection.CollectionsHandler),
    ])


if __name__ == "__main__":
    port = 8808
    print(f"Listening on port {port}...")
    app = make_app()
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()