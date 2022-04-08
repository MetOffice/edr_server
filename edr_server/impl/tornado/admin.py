"""Utilities related to the creation of EDR compliant response payloads, such as valid JSON responses"""
import logging
from pathlib import Path
from typing import Optional, Awaitable

from tornado.web import removeslash

from .handlers import BaseRequestHandler
from ...core import AbstractCollectionsMetadataDataInterface

APP_LOGGER = logging.getLogger("tornado.application")


class RefreshCollectionsHandler(BaseRequestHandler):
    """Handles requests to regenerate the static collections JSON file"""

    collections_cache_path: Path

    collections_interface: AbstractCollectionsMetadataDataInterface

    def initialize(self, collections_interface: AbstractCollectionsMetadataDataInterface, collections_cache_path: Path):
        super().initialize()
        self.collections_interface = collections_interface
        self.collections_cache_path = collections_cache_path

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        # This is an abstract method on the base class, but when running,
        return super().data_received(chunk)  # TODO can just pass/return None?

    @staticmethod
    def _save_cached_response(collection_name: str, rendered_template: bytes, cache_file_path: Path):
        with open(cache_file_path, "wb") as f:
            f.write(rendered_template)
        APP_LOGGER.debug(f"Wrote collection JSON for {collection_name} to {cache_file_path}")

    @removeslash
    def post(self):
        """Handle a refresh collections request."""
        collections_metadata = self.collections_interface.all()

        # # clear existing cached files
        for f in self.collections_cache_path.iterdir():
            f.unlink()  # Despite the name, this will delete the file (or symlink)

        # Store updated individual collection metadata files.
        collection_files = []
        for collection in collections_metadata:
            cache_file_path = self.collections_cache_path / Path(f"{collection.id}.json")
            collection_files.append(cache_file_path)
            rendered_template = self.json_encoder.encode(collection).encode("utf-8")
            self._save_cached_response(collection.id, rendered_template, cache_file_path)

        # Store the updated metadata for all collections as well.
        cache_file_path = self.collections_cache_path / Path(f"collections.json")
        rendered_template = self.render_string("collections.json", collection_files=collection_files)
        self._save_cached_response("collections endpoint", rendered_template, cache_file_path)

        msg = f"Refreshed cache with {len(collections_metadata)} collections"
        APP_LOGGER.info(msg)
        self.write(msg)
