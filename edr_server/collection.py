import json

import config
from handlers import Handler


class CollectionsHandler(Handler):
    """Handle collections requests."""
    def get(self):
        """Handle a 'get collections' request."""
        super().get("")
        collections_path = config.config.collections_json_path()
        with open(collections_path, "r") as ojfh:
            json_data = json.load(ojfh)
            # A Python dict will be sent with Content-Type: application/json in the headers.
            self.write(dict(json_data))
