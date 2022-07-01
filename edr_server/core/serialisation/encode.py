import json
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Tuple, Type

from ..models.extents import TemporalExtent, Extents, SpatialExtent, VerticalExtent
from ..models.i18n import LanguageMap
from ..models.links import Link, OldDataQuery, DataQueryLink, AreaDataQuery
from ..models.metadata import CollectionMetadata, CollectionMetadataList
from ..models.parameters import Symbol, Unit, Category, ObservedProperty, Parameter
from ..models.urls import EdrUrlResolver


def json_encode_area_data_query(area_dq: AreaDataQuery, _encoder: "EdrJsonEncoder") -> Dict[str, Any]:
    return area_dq.to_json()


def json_encode_category(category: Category, encoder: "EdrJsonEncoder") -> Dict[str, Any]:
    encoded_category = {
        "id": category.id,
        "label": category.label if isinstance(category.label, str) else encoder.default(category.label)
    }

    if category.description:
        encoded_category["description"] = (
            category.description if isinstance(category.description, str) else encoder.default(category.description))

    return encoded_category


def json_encode_collection(collection: CollectionMetadata, encoder: "EdrJsonEncoder") -> Dict[str, Any]:
    return {
        "links": [encoder.default(link) for link in collection.get_links(encoder.urls)],
        "id": collection.id,
        "title": collection.title,
        "description": collection.description,
        "keywords": collection.keywords,
        "extent": encoder.default(collection.extent),
        "data_queries": {dl.type: {"link": encoder.default(dl)}
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


def json_encode_data_query_link(dq_link: DataQueryLink, encoder: "EdrJsonEncoder") -> Dict[str, Any]:
    encoded_link = {
        "href": dq_link.href,
        "rel": dq_link.rel,
    }

    # Optional stuff
    if dq_link.variables:
        encoded_link["variables"] = encoder.default(dq_link.variables)
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


def json_encode_data_query(dq: OldDataQuery, _encoder: Optional["EdrJsonEncoder"] = None) -> Dict[str, Any]:
    encoded_dq = {
        "title": dq.title,
        "descriptions": dq.description,
        "query_type": dq.query_type.name.lower(),
        "output_formats": dq.output_formats,
        "default_output_format": dq.default_output_format,
        "crs_details": [{"crs_details": crs.name, "wkt": crs.to_wkt()} for crs in dq.crs_details]
    }

    if dq.height_units:
        encoded_dq["height_units"] = dq.height_units
    if dq.width_units:
        encoded_dq["width_units"] = dq.width_units
    if dq.within_units:
        encoded_dq["within_units"] = dq.within_units

    return encoded_dq


def json_encode_extents(extents: Extents, encoder: "EdrJsonEncoder") -> Dict[str, Any]:
    encoded_extents = {}

    # According to the extents.yaml, all 3 properties are optional
    if extents.spatial:
        encoded_extents["spatial"] = encoder.default(extents.spatial)
    if extents.temporal:
        encoded_extents["temporal"] = encoder.default(extents.temporal)
    if extents.vertical:
        encoded_extents["vertical"] = encoder.default(extents.vertical)

    return encoded_extents


def json_encode_language_map(language_map: LanguageMap, _encoder: Optional["EdrJsonEncoder"] = None):
    return {k: v for k, v in language_map.items()}  # Make a copy so that we don't accidentally change the original data


def json_encode_link(link: Link, _encoder: Optional["EdrJsonEncoder"] = None) -> Dict[str, Any]:
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


def json_encode_observed_property(
        observed_property: ObservedProperty, encoder: Optional["EdrJsonEncoder"] = None) -> Dict[str, Any]:
    encoded_property = {
        "label": (observed_property.label
                  if isinstance(observed_property.label, str) else encoder.default(observed_property.label)),

    }
    if observed_property.id:
        encoded_property["id"] = observed_property.id
    if observed_property.description:
        encoded_property["description"] = observed_property.description
    if observed_property.categories:
        encoded_property["categories"] = [encoder.default(cat) for cat in observed_property.categories]

    return encoded_property


def json_encode_parameter(param: Parameter, encoder: Optional["EdrJsonEncoder"] = None) -> Dict[str, Any]:
    encoded_param = {
        "type": "Parameter",
        "observedProperty": encoder.default(param.observed_property),
    }

    if param.description:
        encoded_param["description"] = param.description
    if param.label:
        encoded_param["label"] = param.label
    if param.data_type:
        encoded_param["data-type"] = param.data_type.__name__
    if param.unit:
        encoded_param["unit"] = encoder.default(param.unit)
    # TODO serialise categoryEncoding, once it's added to model
    if param.extent:
        encoded_param["extent"] = encoder.default(param.extent)
    if param.id:
        encoded_param["id"] = param.id
    # TODO serialise measurementType once it's added to model

    return encoded_param


def json_encode_spatial_extent(
        spatial_extent: SpatialExtent, _encoder: Optional["EdrJsonEncoder"] = None) -> Dict[str, Any]:
    return {
        # TODO support multiple bounding boxes (https://github.com/ADAQ-AQI/edr_server/issues/31)
        "bbox": [list(spatial_extent.bounds)],
        "crs_details": spatial_extent.crs.to_wkt(),
        "name": spatial_extent.crs.name,
    }


def json_encode_symbol(symbol: Symbol, _encoder: Optional["EdrJsonEncoder"] = None) -> Dict[str, Any]:
    return {
        "value": symbol.value,
        "type": symbol.type,
    }


def json_encode_temporal_extent(
        temporal_extent: TemporalExtent, encoder: Optional["EdrJsonEncoder"] = None) -> Dict[str, Any]:
    return {
        "name": temporal_extent.trs.name,
        "trs": temporal_extent.trs.to_wkt(),
        "interval": [temporal_extent.bounds],
        "values": [encoder.default(dt) for dt in temporal_extent.values] + list(map(str, temporal_extent.intervals))
    }


def json_encode_unit(unit: Unit, encoder: Optional["EdrJsonEncoder"] = None) -> Dict[str, Any]:
    encoded_unit = {}

    if unit.symbol:
        encoded_unit["symbol"] = unit.symbol if isinstance(unit.symbol, str) else encoder.default(unit.symbol)
    if unit.labels:
        # Note, the field is called `label` in the serialised output, even though it can hold multiple values
        encoded_unit["label"] = unit.labels if isinstance(unit.labels, str) else encoder.default(unit.labels)
    if unit.id:
        encoded_unit["id"] = unit.id

    return encoded_unit


def json_encode_vertical_extent(
        vertical_extent: VerticalExtent, _encoder: Optional["EdrJsonEncoder"] = None) -> Dict[str, Any]:
    return {
        "interval": list(map(str, vertical_extent.interval)),
        "values": list(map(str, vertical_extent.values)),
        "vrs": vertical_extent.vrs.to_wkt(),
        "name": vertical_extent.vrs.name,
    }


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
        Category: json_encode_category,
        CollectionMetadata: json_encode_collection,
        CollectionMetadataList: json_encode_collection_metadata_list,
        datetime: json_encode_datetime,
        OldDataQuery: json_encode_data_query,
        DataQueryLink: json_encode_data_query_link,
        Extents: json_encode_extents,
        LanguageMap: json_encode_language_map,
        Link: json_encode_link,
        ObservedProperty: json_encode_observed_property,
        Parameter: json_encode_parameter,
        SpatialExtent: json_encode_spatial_extent,
        Symbol: json_encode_symbol,
        TemporalExtent: json_encode_temporal_extent,
        Unit: json_encode_unit,
        VerticalExtent: json_encode_vertical_extent,
    }

    def default(self, obj: Any) -> Any:
        """Return a JSON encodable version of objects that can't otherwise be serialised, or raise a TypeError"""
        try:
            return self.ENCODER_MAP[type(obj)](obj, self)
        except KeyError:
            # Let the base class default method raise the TypeError
            return super().default(obj)
