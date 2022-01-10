"""Utilities related to the creation of EDR compliant response payloads, such as valid JSON responses"""

from tornado.web import RequestHandler, removeslash


# data_received is marked as abstract, but doesn't need to be implemented
# noinspection PyAbstractClass
class RefreshCollectionsHandler(RequestHandler):
    """Handles requests to regenerate the static collections JSON file"""

    @removeslash
    def post(self):
        """Handle a refresh collections request."""
        self.write("ok")
