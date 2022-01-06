import json

from tornado.web import RequestHandler

import config


class CollectionsHandler(RequestHandler):
    """Handle collections requests."""
    def get(self):
        """Handle a 'get collections' request."""
        try:
            mime_type, = self.get_arguments("f")
        except ValueError:
            mime_type = "json"
        if mime_type == "json":
            collections_path = config.config.collections_json_path()
            with open(collections_path, "r") as ojfh:
                json_data = json.load(ojfh)
                # A Python dict will be sent with Content-Type: aaplication/json in the headers.
                self.write(dict(json_data))
        else:
            raise ValueError(f"Format {mime_type!r} is not supported.")
