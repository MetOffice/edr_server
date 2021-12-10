import json

from tornado.escape import json_encode
from tornado.web import RequestHandler

import config


class CollectionsHandler(RequestHandler):

    def get(self):
        mime_type, = self.get_arguments("f")
        if mime_type == "json":
            collections_path = config.config.collections_json_path()
            with open(collections_path, "r") as ojfh:
                json_data = json.load(ojfh)
                self.write(json_encode(json_data))
        else:
            raise ValueError(f"Format {mime_type!r} is not supported.")
