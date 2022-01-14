import logging

import tornado.ioloop
from clean_air.data.storage import create_metadata_store
from tornado.options import options, define
from tornado.web import Application, url

from . import  admin
from . import collection
from . import handlers
from .config import config
from .paths import app_relative_path_to_absolute


APP_LOGGER = logging.getLogger("tornado.application")

def make_app():
    collections_cache_path = config.collections_cache_path()
    metadata_store = create_metadata_store()
    return Application(
        [
            url(r"/collections/(.*)/area", handlers.AreaHandler),
            url(r"/collections/(.*)/corridor", handlers.CorridorHandler),
            url(r"/collections/(.*)/cube", handlers.CubeHandler),
            url(r"/collections/(.*)/items", handlers.ItemsHandler),
            url(r"/collections/(.*)/locations", handlers.LocationsHandler),
            url(r"/collections/(.*)/position", handlers.PositionHandler, name="position_query"),
            url(r"/collections/(.*)/radius", handlers.RadiusHandler),
            url(r"/collections/(.*)/trajectory", handlers.TrajectoryHandler),
            url(r"/collections\/?", collection.CollectionsHandler,
                {"collections_cache_path": collections_cache_path},
                name="collections"),
            url(r"/collections/(.*)\/?", collection.CollectionsHandler,
                {"collections_cache_path": collections_cache_path},
                name="collection"),
            url(r"/admin/refresh_collections\/?", admin.RefreshCollectionsHandler,
                {"collections_cache_path": collections_cache_path,
                 "metadata_store": metadata_store},
                name="refresh_collections"),
        ],
        template_path=app_relative_path_to_absolute("templates"),
    )


define("port", default=8808, help="port to listen on")

if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.ERROR)
    logging.getLogger("tornado").setLevel(options.logging.upper())

    app = make_app()
    app.listen(options.port)
    APP_LOGGER.info(f"Listening on port {options.port}...")

    tornado.ioloop.IOLoop.current().start()

