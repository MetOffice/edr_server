from tornado.web import Application, url

from . import admin
from . import collection
from . import handlers
from .config import config
from .paths import app_relative_path_to_absolute


def make_app():
    collections_cache_path = config.collections_cache_path()
    data_interface = config.data_interface()
    supported_data_queries = config.data_queries()

    return Application(
        [
            url(r"/collections/(.*)/area", handlers.AreaHandler, name="area_query"),
            url(r"/collections/(.*)/corridor", handlers.CorridorHandler),
            url(r"/collections/(.*)/cube", handlers.CubeHandler),
            url(r"/collections/(.*)/items", handlers.ItemsHandler,
                {"data_interface": data_interface},
                name="items_query"),
            url(r"/collections/(.*)/locations/(.*)", handlers.LocationHandler,
                {"data_interface": data_interface},
                name="location_query"),
            url(r"/collections/(.*)/locations", handlers.LocationsHandler,
                {"data_interface": data_interface},
                name="locations_query"),
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
                {"data_interface": data_interface,
                 "data_queries": supported_data_queries,
                 "collections_cache_path": collections_cache_path},
                name="refresh_collections"),
            # url(r"/api\/?", handlers.APIHandler,
            #     {"data_interface": data_interface},
            #     name="api"),
            url(r"/conformance\/?", handlers.ConformanceHandler,
                {"data_interface": data_interface},
                name="conformance"),
            url(r"/service/description\.html", handlers.ServiceHandler,
                {"data_interface": data_interface},
                name="service-desc"),
            url(r"/service/license\.html", handlers.ServiceHandler,
                {"data_interface": data_interface},
                name="service-license"),
            url(r"/service/terms-and-conditions\.html", handlers.ServiceHandler,
                {"data_interface": data_interface},
                name="service-terms"),
            url(r"\/?", handlers.RootHandler,
                {"data_interface": data_interface},
                name="root"),
        ],
        template_path=app_relative_path_to_absolute("templates"),
    )
