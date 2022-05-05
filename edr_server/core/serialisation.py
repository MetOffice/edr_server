import json
from datetime import datetime
from typing import Any, Dict, Callable, Type, Optional, Tuple

from .models.extents import TemporalExtent
from .models.links import Link, DataQuery, DataQueryLink
from .models.metadata import CollectionMetadata, CollectionMetadataList
from .models.urls import EdrUrlResolver


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
                "crs_details": str(collection.extent.spatial.crs),
                "name": collection.crs.name,
            },
            "temporal": json_encode_temporal_extent(collection.extent.temporal, urls),
            # TODO: Vertical extent
        },
        "data_queries": collection.get_data_query_links(urls),
        "crs_details": [str(collection.extent.spatial.crs)],
        "output_formats": collection.output_formats,
        "parameter_names": [],  # TODO - implement this part of the serialisation
    }


def json_encode_collection_metadata_list(
        collection_list: CollectionMetadataList, urls: EdrUrlResolver) -> Dict[str, Any]:
    return {
        "links": [json_encode_link(link, urls) for link in collection_list.get_links(urls)],
        "collections": [json_encode_collection(c, urls) for c in collection_list.collections]
    }


def json_encode_link(link: Link, _urls: Optional[EdrUrlResolver] = None) -> Dict[str, Any]:
    encoded_link = {
        "href": link.href,
        "rel": link.rel,
    }

    # Optional stuff
    if link.title:
        encoded_link["title"] = link.title
    if link.type:
        encoded_link["type"] = link.type
    if link.hreflang:
        encoded_link["hreflang"] = link.hreflang
    if link.length:
        encoded_link["length"] = link.length

    return encoded_link


def json_encode_data_query_link(dq_link: DataQueryLink, _urls: Optional[EdrUrlResolver] = None) -> Dict[str, Any]:
    encoded_link = {
        "href": dq_link.href,
        "rel": dq_link.rel,
    }

    # Optional stuff
    if dq_link.variables:
        encoded_link["variables"] = json_encode_data_query(dq_link.variables)
    if dq_link.title:
        encoded_link["title"] = dq_link.title
    if dq_link.type:
        encoded_link["type"] = dq_link.type
    if dq_link.hreflang:
        encoded_link["hreflang"] = dq_link.hreflang
    if dq_link.length:
        encoded_link["length"] = dq_link.length
    if dq_link.templated:
        encoded_link["templated"] = dq_link.templated

    return encoded_link


def json_encode_data_query(dq: DataQuery, _urls: Optional[EdrUrlResolver] = None) -> Dict[str, Any]:
    encoded_dq = {
        "title": dq.title,
        "descriptions": dq.description,
        "query_type": dq.query_type.name.lower(),
        "output_formats": dq.output_formats,
        "default_output_format": dq.default_output_format,
        "crs_details": [{"crs_details": crs.name, "wkt": str(crs)} for crs in dq.crs_details]
    }

    if dq.height_units:
        encoded_dq["height_units"] = dq.height_units
    if dq.width_units:
        encoded_dq["width_units"] = dq.width_units
    if dq.within_units:
        encoded_dq["within_units"] = dq.within_units

    return encoded_dq


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

    ENCODER_MAP: Dict[Type, Callable[[Any, EdrUrlResolver], Dict[str, Any]]] = {
        datetime: json_encode_datetime,
        TemporalExtent: json_encode_temporal_extent,
        # TODO Check all models are present here, Extent and VerticalExtent are definitely missing
        CollectionMetadata: json_encode_collection,
        CollectionMetadataList: json_encode_collection_metadata_list,
        Link: json_encode_link,
        DataQuery: json_encode_data_query,
        DataQueryLink: json_encode_data_query_link,
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
