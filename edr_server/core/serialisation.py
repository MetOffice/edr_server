import json
from datetime import datetime
from typing import Any, Dict, Callable, Type, Optional, Tuple

from .models import TemporalExtent, CollectionMetadata
from .urls import EdrUrlResolver


def json_encode_datetime(dt: datetime, _urls: EdrUrlResolver) -> str:
    # Whilst wrapping this simple function call in a function may seem like overkill, it allows us to include it in
    # EdrJsonEncoder.ENCODER_MAP, so it gets hooked into the JSON Encoder correctly. Also, it documents that datetimes
    # should be encoded as ISO 8601 datetimes
    return dt.isoformat()


def json_encode_temporal_extent(temporal_extent: TemporalExtent, _urls: EdrUrlResolver) -> Dict[str, Any]:
    return {
        "name": temporal_extent.trs.name,
        "trs": temporal_extent.trs.wkt,
        "interval": [temporal_extent.bounds],
        "values": list(map(json_encode_datetime, temporal_extent.values)) + list(map(str, temporal_extent.intervals))
    }


def json_encode_collection(collection: CollectionMetadata, urls: EdrUrlResolver) -> Dict[str, Any]:
    return {
        "links": collection.get_links(urls),
        "id": collection.id,
        "title": collection.title,
        "description": collection.description,
        "keywords": collection.keywords,
        "extent": {
            "spatial": {
                "bbox": list(collection.extent.spatial.bounds),
                "crs": str(collection.extent.spatial.crs),
                "name": collection.crs.name,
            },
            "temporal": json_encode_temporal_extent(collection.extent.temporal, urls),
            # TODO: Vertical extent
        },
        "data_queries": collection.get_data_query_links(urls),  # TODO - Serialise these objects
        "crs": [str(collection.extent.spatial.crs)],
        "output_formats": collection.output_formats,
        "parameter_names": [],  # TODO - implement this part of the serialisation
    }


class EdrJsonEncoder(json.JSONEncoder):
    def __init__(
            self, *, skipkeys: bool = ..., ensure_ascii: bool = ..., check_circular: bool = ...,
            allow_nan: bool = ..., sort_keys: bool = ..., indent: Optional[int] = ...,
            separators: Optional[Tuple[str, str]] = ..., default: Optional[Callable[..., Any]] = ...,
            urls: EdrUrlResolver) -> None:
        super().__init__(skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular,
                         allow_nan=allow_nan, sort_keys=sort_keys, indent=indent, separators=separators,
                         default=default)
        self.urls = urls

    ENCODER_MAP: Dict[Type, Callable[[Any, EdrUrlResolver], Dict[str, Any]]] = {
        datetime: json_encode_datetime,
        TemporalExtent: json_encode_temporal_extent,
    }

    def default(self, obj: Any) -> Any:
        try:
            # We try the super method first, because this is the most common code path, since most things
            # can be encoded by the json library
            return super().default(obj)
        except TypeError as type_err:
            try:
                return self.ENCODER_MAP[type(obj)](obj, self.urls)
            except KeyError:
                raise type_err  # Re-raise original error, it's more appropriate than a Key Error
