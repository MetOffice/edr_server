"""
These functions are used by passing them as object_hook parameters to `json.loads()`

E.g. `json.loads(encoded_collection, object_hook=json_decode_collection)`
"""
from datetime import datetime
from typing import Any, Dict

from ..models.links import Link
from ..models.metadata import CollectionMetadata, CollectionMetadataList


def json_decode_collection_metadata_list(encoded_collection_list: Dict[str, Any]) -> CollectionMetadataList:
    kwargs = {
        "links": [Link.from_json(encoded_link) for encoded_link in encoded_collection_list["links"]],
        "collections": [
            CollectionMetadata.from_json(encoded_collection)
            for encoded_collection in encoded_collection_list["collections"]
        ],
    }

    return CollectionMetadataList(**kwargs)


def json_decode_datetime(dt_str: str) -> datetime:
    # Whilst wrapping this simple function call in a function may seem like overkill, it allows us to include it in
    # EdrJsondecoder.decodeR_MAP, so it gets hooked into the JSON decoder correctly. Also, it documents that datetime
    # objects should be decoded using the ISO 8601 datetime format.
    return datetime.fromisoformat(dt_str)
