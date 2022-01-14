"""Utilities related to the creation of EDR compliant response payloads, such as valid JSON responses"""
import json
import logging
from pathlib import Path
from typing import List

from clean_air.data.storage import S3FSMetadataStore
from clean_air.models import Metadata
from tornado.escape import json_encode, squeeze
from tornado.web import RequestHandler, removeslash

APP_LOGGER = logging.getLogger("tornado.application")


# data_received is marked as abstract, but doesn't need to be implemented
# noinspection PyAbstractClass
class RefreshCollectionsHandler(RequestHandler):
    """Handles requests to regenerate the static collections JSON file"""

    collections_cache_path: Path
    metadata_store: S3FSMetadataStore

    def initialize(self, collections_cache_path: Path, metadata_store: S3FSMetadataStore):
        self.collections_cache_path = collections_cache_path
        self.metadata_store = metadata_store

    def _save_cached_response(self, collection_name: str, rendered_template: bytes, cache_file_path: Path):
        # This has the added benefit of validating our JSON rendered from the template
        minified_rendered_template = json.dumps(json.loads(rendered_template)).encode("utf-8")
        with open(cache_file_path, "wb") as f:
            f.write(minified_rendered_template)
        APP_LOGGER.info(f"Wrote collection JSON for {collection_name} to {cache_file_path}")

    @removeslash
    def post(self):
        """Handle a refresh collections request."""

        collections_metadata: List[Metadata] = []
        for collection_name in self.metadata_store.available_datasets():
            collection = self.metadata_store.get(collection_name)
            collections_metadata.append(collection)

            cache_file_path = self.collections_cache_path / Path(f"{collection.id}.json")
            rendered_template = self.render_string("collection.json", collection=collection)
            self._save_cached_response(collection_name, rendered_template, cache_file_path)

        # Now write the combined collections response
        cache_file_path = self.collections_cache_path / Path(f"collections.json")
        rendered_template = self.render_string("collections.json", collections=collections_metadata)
        self._save_cached_response("collections endpoint", rendered_template, cache_file_path)

        self.write(f"Refreshed cache with {len(collections_metadata)} collections")
