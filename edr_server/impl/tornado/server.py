from tornado.web import Application, url

from edr_server.utils.paths import app_relative_path_to_absolute

from ...core import EdrDataInterface
from . import admin, collection, handlers
from .config import config


def make_app(data_interface: EdrDataInterface) -> Application:
    collections_cache_path = config.collections_cache_path()

    return Application(
        [
            url(r"/collections/(.*)/area", handlers.AreaHandler,
                {"data_interface": data_interface},
                name="area_query"),
            url(r"/collections/(.*)/corridor", handlers.CorridorHandler),
            url(r"/collections/(.*)/cube", handlers.CubeHandler),
            url(r"/collections/(.*)/items/(.*)", handlers.ItemHandler,
                {"data_interface": data_interface},
                name="item_query"),
            url(r"/collections/(.*)/items", handlers.ItemsHandler,
                {"data_interface": data_interface},
                name="items_query"),
            url(r"/collections/(.*)/locations/(.*)", handlers.LocationHandler,
                {"data_interface": data_interface},
                name="location_query"),
            url(r"/collections/(.*)/locations", handlers.LocationsHandler,
                {"data_interface": data_interface},
                name="locations_query"),
            url(r"/collections/(.*)/position", handlers.PositionHandler,
                {"data_interface": data_interface},
                name="position_query"),
            url(r"/collections/(.*)/radius", handlers.RadiusHandler,
                {"data_interface": data_interface},
                name="radius_query"),
            url(r"/collections/(.*)/trajectory", handlers.TrajectoryHandler),
            url(r"/collections/([^/.]*)\/?", collection.CollectionsHandler,
                {"collections_cache_path": collections_cache_path},
                name="collection"),
            url(r"/collections\/?", collection.CollectionsHandler,
                {"collections_cache_path": collections_cache_path},
                name="collections"),
            url(r"/admin/refresh_collections\/?", admin.RefreshCollectionsHandler,
                {"collections_interface": data_interface.collections,
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
