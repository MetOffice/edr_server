"""Utilities related to the creation of EDR compliant response payloads, such as valid JSON responses"""
import logging
from pathlib import Path

from tornado.escape import json_encode
from tornado.web import RequestHandler, removeslash

APP_LOGGER = logging.getLogger("tornado.application")


# data_received is marked as abstract, but doesn't need to be implemented
# noinspection PyAbstractClass
class RefreshCollectionsHandler(RequestHandler):
    """Handles requests to regenerate the static collections JSON file"""

    collections_path: Path

    def initialize(self, collections_path: Path):
        self.collections_path = collections_path

    @removeslash
    def post(self):
        """Handle a refresh collections request."""
        collections_json = self.render_string("collections.json")
        with open(self.collections_path, "wb") as f:
            f.write(collections_json)
        APP_LOGGER.info(f"Updated collections.json at {self.collections_path}")
        APP_LOGGER.debug(f"collections.json={json_encode(collections_json.decode('utf-8'))}")
