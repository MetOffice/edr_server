import json

from tornado.web import HTTPError, RequestHandler


class AreaHandler(RequestHandler):
    """Handle area requests."""
    def get(self, collection_name):
        """Handle a 'get area' request."""
        # Not implemented!
        HTTPError(501, "Get area request is not implemented.")


class CorridorHandler(RequestHandler):
    """Handle corridor requests."""
    def get(self, collection_name):
        """Handle a 'get corridor' request."""
        # Not implemented!
        HTTPError(501, "Get corridor request is not implemented.")


class CubeHandler(RequestHandler):
    """Handle cube requests."""
    def get(self, collection_name):
        """Handle a 'get cube' request."""
        # Not implemented!
        HTTPError(501, "Get cube request is not implemented.")


class ItemsHandler(RequestHandler):
    """Handle items requests."""
    def get(self, collection_name):
        """Handle a 'get items' request."""
        self.write(f"Get items request called for collection {collection_name!r}.")


class LocationsHandler(RequestHandler):
    """Handle location requests."""
    def get(self, collection_name):
        """Handle a 'get locations' request."""
        self.write(f"Get locations request called for collection {collection_name!r}.")


class PositionHandler(RequestHandler):
    """Handle position requests."""
    def get(self, collection_name):
        """Handle a 'get position' request."""
        self.write(f"Get position request called for collection {collection_name!r}.")


class RadiusHandler(RequestHandler):
    """Handle radius requests."""
    def get(self, collection_name):
        """Handle a 'get radius' request."""
        # Not implemented!
        HTTPError(501, "Get radius request is not implemented.")


class TrajectoryHandler(RequestHandler):
    """Handle trajectory requests."""
    def get(self, collection_name):
        """Handle a 'get trajectory' request."""
        # Not implemented!
        HTTPError(501, "Get trajectory request is not implemented.")