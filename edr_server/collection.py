import json

from tornado.web import removeslash

import config
from handlers import Handler


class CollectionsHandler(Handler):
    """Handle collections requests."""

    @removeslash
    def get(self):
        """Handle a 'get collections' request."""
        super().get("")
        collections_path = config.config.collections_json_path()
        with open(collections_path, "r") as ojfh:
            json_data = json.load(ojfh)
            # A Python dict will be sent with Content-Type: application/json in the headers.
            self.write(dict(json_data))


class CollectionHandler(Handler):
    """Handle requests for a specific collection."""

    @removeslash
    def get(self, collection_id):
        self.write(f"Requested: {collection_id}")
