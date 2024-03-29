import logging
from pathlib import Path

from tornado.web import removeslash

from .handlers import Handler

APP_LOGGER = logging.getLogger("tornado.application")


class CollectionsHandler(Handler):
    """Handle collections requests."""

    def _get_render_args(self):
        pass

    collections_cache_path: Path

    def initialize(self, collections_cache_path: Path):
        super().initialize()
        self.collections_cache_path = collections_cache_path

    @removeslash
    def get(self, collection_id=None):
        """Handle a 'get collections' request."""
        super().get(collection_id)

    def render_template(self):
        cache_filename = Path(f"{self.collection_id if self.collection_id else 'collections'}.json")
        cache_path = Path(self.collections_cache_path) / cache_filename

        try:
            with open(cache_path, "r") as ojfh:
                self.set_header("Content-Type", "application/json")
                self.write(ojfh.read())
        except FileNotFoundError as e:
            APP_LOGGER.info(f"Failed to load {cache_path}: {e}")
            if self.collection_id:
                msg = (
                    f"Collection '{cache_filename}' not found. Does the collections cache require updating? "
                    f"Send a POST request to {self.application.reverse_url('refresh_collections')} to refresh the cache"
                )
                self.send_error(404, reason=msg)
            else:
                self.send_error(500, reason="Unable to load collections data")
