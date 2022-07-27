import json
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Tuple, Type

from ..models import EdrModel
from ..models.metadata import CollectionMetadata, CollectionMetadataList
from ..models.urls import EdrUrlResolver


def json_encode_collection(collection: CollectionMetadata, encoder: "EdrJsonEncoder") -> Dict[str, Any]:
    return {
        "links": [encoder.default(link) for link in collection.get_links(encoder.urls)],
        "id": collection.id,
        "title": collection.title,
        "description": collection.description,
        "keywords": collection.keywords,
        "extent": encoder.default(collection.extent),
        "data_queries": {dl.type: {"link": dl.to_json()}
                         for dl in collection.get_data_query_links(encoder.urls)},
        "crs_details": [str(collection.extent.spatial.crs)],
        "output_formats": collection.output_formats,
        "parameter_names": {param.id: encoder.default(param) for param in collection.parameters},
    }


def json_encode_collection_metadata_list(
        collection_list: CollectionMetadataList, encoder: "EdrJsonEncoder") -> Dict[str, Any]:
    return {
        "links": [encoder.default(link) for link in collection_list.get_links(encoder.urls)],
        "collections": [encoder.default(collection) for collection in collection_list.collections],
    }


def json_encode_datetime(dt: datetime, _encoder: Optional["EdrJsonEncoder"] = None) -> str:
    # Whilst wrapping this simple function call in a function may seem like overkill, it allows us to include it in
    # EdrJsonEncoder.ENCODER_MAP, so it gets hooked into the JSON Encoder correctly. Also, it documents that datetime
    # objects should be encoded using the ISO 8601 datetime format.

    # Is your serialisaed datetime missing a `Z` or other timezone designator?
    # You need to set the timezone on your datetimes, otherwise it is a timezone naive datetime and will not have
    # timezone information. E.g. datetime(2022,5,19, tzinfo=timezone.utc) or datetime.now().replace(tzinfo=timezone.utc)

    # This code is fine and correctly handles both timezone aware and timezone naive datetimes.
    return dt.isoformat()  # Did I mention that if you're having timezone serialisation issues, this code is fine?


class EdrJsonEncoder(json.JSONEncoder):
    def __init__(
            self, *, skipkeys: bool = False, ensure_ascii: bool = True, check_circular: bool = True,
            allow_nan: bool = True, sort_keys: bool = False, indent: Optional[int] = None,
            separators: Optional[Tuple[str, str]] = None, default: Optional[Callable[..., Any]] = None,
            urls: EdrUrlResolver) -> None:
        super().__init__(skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular,
                         allow_nan=allow_nan, sort_keys=sort_keys, indent=indent, separators=separators,
                         default=default)
        self.urls = urls

    ENCODER_MAP: Dict[Type, Callable[[Any, "EdrJsonEncoder"], Dict[str, Any]]] = {
        CollectionMetadata: json_encode_collection,
        CollectionMetadataList: json_encode_collection_metadata_list,
        datetime: json_encode_datetime,
    }

    def default(self, obj: Any) -> Any:
        """Return a JSON encodable version of objects that can't otherwise be serialised, or raise a TypeError"""
        if isinstance(obj, EdrModel):
            return obj.to_json()
        else:
            try:
                return self.ENCODER_MAP[type(obj)](obj, self)
            except KeyError:
                # Let the base class default method raise the TypeError
                return super().default(obj)
