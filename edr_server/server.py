from clean_air.data.storage import create_metadata_store
from tornado.web import Application, url

from . import admin
from . import collection
from . import handlers
from .config import config
from .paths import app_relative_path_to_absolute


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
            url(r"/collections/(.*)\/?", collection.CollectionsHandler,
                {"collections_cache_path": collections_cache_path},
                name="collection"),
            url(r"/collections\/?", collection.CollectionsHandler,
                {"collections_cache_path": collections_cache_path},
                name="collections"),
            url(r"/admin/refresh_collections\/?", admin.RefreshCollectionsHandler,
                {"collections_cache_path": collections_cache_path,
                 "metadata_store": metadata_store},
                name="refresh_collections"),
            # url(r"/api\/?", handlers.APIHandler, name="api"),
            url(r"/conformance\/?", handlers.ConformanceHandler, name="conformance"),
            url(r"\/?", handlers.RootHandler, name="root"),
        ],
        template_path=app_relative_path_to_absolute("templates"),
    )
