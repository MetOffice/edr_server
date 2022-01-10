import tornado.ioloop
from tornado.web import Application, url

import admin
import collection
import handlers


def make_app():
    return Application(
        [
            url(r"/collections/(.*)/area", handlers.AreaHandler),
            url(r"/collections/(.*)/corridor", handlers.CorridorHandler),
            url(r"/collections/(.*)/cube", handlers.CubeHandler),
            url(r"/collections/(.*)/items", handlers.ItemsHandler),
            url(r"/collections/(.*)/locations", handlers.LocationsHandler),
            url(r"/collections/(.*)/position", handlers.PositionHandler),
            url(r"/collections/(.*)/radius", handlers.RadiusHandler),
            url(r"/collections/(.*)/trajectory", handlers.TrajectoryHandler),
            url(r"/collections\/?", collection.CollectionsHandler, name="collections"),
            url(r"/collections/([a-z0-9]+)\/?", collection.CollectionHandler, name="collection"),
            url(r"/admin/refresh_collections\/?", admin.RefreshCollectionsHandler, name="refresh_collections"),
        ]
    )


if __name__ == "__main__":
    port = 8808
    print(f"Listening on port {port}...")
    app = make_app()
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()
