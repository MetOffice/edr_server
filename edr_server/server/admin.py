"""Utilities related to the creation of EDR compliant response payloads, such as valid JSON responses"""
import json
import logging
from pathlib import Path
from typing import List

from tornado.web import removeslash

from .handlers import Handler

APP_LOGGER = logging.getLogger("tornado.application")


# data_received is marked as abstract, but doesn't need to be implemented
# noinspection PyAbstractClass
class RefreshCollectionsHandler(Handler):
    """Handles requests to regenerate the static collections JSON file"""

    collections_cache_path: Path

    def initialize(self, data_interface, data_queries: List, collections_cache_path: Path):
        self.data_queries = data_queries
        self.interface = data_interface.RefreshCollections(self.data_queries)
        self.collections_cache_path = collections_cache_path

    def _save_cached_response(self, collection_name: str, rendered_template: bytes, cache_file_path: Path):
        # This has the added benefit of validating our JSON rendered from the template
        minified_rendered_template = json.dumps(json.loads(rendered_template)).encode("utf-8")
        with open(cache_file_path, "wb") as f:
            f.write(minified_rendered_template)
        APP_LOGGER.info(f"Wrote collection JSON for {collection_name} to {cache_file_path}")

    @removeslash
    def post(self):
        """Handle a refresh collections request."""
        collections_metadata = self.interface.data()

        # Store updated individual collection metadata files.
        collection_files = []
        for collection in collections_metadata:
            cache_file_path = self.collections_cache_path / Path(f"{collection.id}.json")
            collection_files.append(cache_file_path)
            render_kwargs = {
                "collection": collection,
                "data_queries": self.data_queries,
                "temporal_extent": self.interface.has_temporal_extent(),
                "vertical_extent": self.interface.has_vertical_extent(),
                "parameters": self.interface.get_parameters(collection.id),
            }
            rendered_template = self.render_string("collection.json", **render_kwargs)
            self._save_cached_response(collection.id, rendered_template, cache_file_path)

        # Store the updated metadata for all collections as well.
        cache_file_path = self.collections_cache_path / Path(f"collections.json")
        rendered_template = self.render_string("collections.json", collection_files=collection_files)
        self._save_cached_response("collections endpoint", rendered_template, cache_file_path)

        self.write(f"Refreshed cache with {len(collections_metadata)} collections")
