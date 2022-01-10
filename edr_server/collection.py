import json
from pathlib import Path

from tornado.web import removeslash

from handlers import Handler


class CollectionsHandler(Handler):
    """Handle collections requests."""

    collections_path: Path

    def initialize(self, collections_path: Path):
        super().initialize()
        self.collections_path = collections_path

    @removeslash
    def get(self):
        """Handle a 'get collections' request."""
        super().get("")
        with open(self.collections_path, "r") as ojfh:
            json_data = json.load(ojfh)
            # A Python dict will be sent with Content-Type: application/json in the headers.
            self.write(dict(json_data))


class CollectionHandler(Handler):
    """Handle requests for a specific collection."""

    @removeslash
    def get(self, collection_id):
        self.write(f"Requested: {collection_id}")
