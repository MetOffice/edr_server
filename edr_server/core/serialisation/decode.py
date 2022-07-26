"""
These functions are used by passing them as object_hook parameters to `json.loads()`

E.g. `json.loads(encoded_collection, object_hook=json_decode_collection)`
"""
from datetime import datetime
from typing import Any, Dict

import pyproj

from ..models.extents import TemporalExtent, Extents, SpatialExtent, VerticalExtent
from ..models.i18n import LanguageMap
from ..models.links import DataQueryLink, Link
from ..models.metadata import CollectionMetadata, CollectionMetadataList
from ..models.parameters import Symbol, Unit, Category, ObservedProperty, Parameter


def json_decode_category(encoded_category: Dict[str, Any]) -> Category:
    kwargs = encoded_category
    if isinstance(kwargs["label"], dict):
        kwargs["label"] = LanguageMap.from_json(kwargs["label"])

    if "description" in encoded_category and isinstance(encoded_category["description"], dict):
        kwargs["description"] = LanguageMap.from_json(encoded_category["description"])

    return Category(**kwargs)


def json_decode_collection(encoded_collection: Dict[str, Any]) -> CollectionMetadata:
    kwargs = encoded_collection

    kwargs["links"] = [Link.from_json(encoded_link) for encoded_link in kwargs["links"]]
    kwargs["extent"] = json_decode_extents(kwargs["extent"])
    kwargs["data_queries"] = [DataQueryLink.from_json(encoded_dq) for encoded_dq in kwargs["data_queries"].values()]
    del kwargs["crs_details"]
    kwargs["parameters"] = [json_decode_parameter(encoded_param) for encoded_param in kwargs["parameter_names"]]
    del kwargs["parameter_names"]

    return CollectionMetadata(**kwargs)


def json_decode_collection_metadata_list(encoded_collection_list: Dict[str, Any]) -> CollectionMetadataList:
    kwargs = {
        "links": [Link.from_json(encoded_link) for encoded_link in encoded_collection_list["links"]],
        "collections": [
            json_decode_collection(encoded_collection) for encoded_collection in encoded_collection_list["collections"]
        ],
    }

    return CollectionMetadataList(**kwargs)


def json_decode_datetime(dt_str: str) -> datetime:
    # Whilst wrapping this simple function call in a function may seem like overkill, it allows us to include it in
    # EdrJsondecoder.decodeR_MAP, so it gets hooked into the JSON decoder correctly. Also, it documents that datetime
    # objects should be decoded using the ISO 8601 datetime format.
    return datetime.fromisoformat(dt_str)


def json_decode_extents(encoded_extents: Dict[str, Any]) -> Extents:
    kwargs = {}

    # According to the extents.yaml, all 3 properties are optional
    if "spatial" in encoded_extents:
        kwargs["spatial"] = SpatialExtent.from_json(encoded_extents["spatial"])
    if "temporal" in encoded_extents:
        kwargs["temporal"] = TemporalExtent.from_json(encoded_extents["temporal"])
    if "vertical" in encoded_extents:
        kwargs["vertical"] = json_decode_vertical_extent(encoded_extents["vertical"])

    return Extents(**kwargs)


def json_decode_observed_property(encoded_observed_property: Dict[str, Any]) -> ObservedProperty:
    if isinstance(encoded_observed_property, dict):
        encoded_observed_property["label"] = LanguageMap.from_json(encoded_observed_property["label"])

    if "categories" in encoded_observed_property:
        encoded_observed_property["categories"] = [json_decode_category(cat)
                                                   for cat in encoded_observed_property["categories"]]

    return ObservedProperty(**encoded_observed_property)


def json_decode_parameter(encoded_param: Dict[str, Any]) -> Parameter:
    del encoded_param["type"]

    encoded_param["observed_Property"] = json_decode_observed_property(encoded_param["observedProperty"])
    del encoded_param["observedProperty"]

    if "data-type" in encoded_param:
        # Note replacement of `-` with `_` in key name
        encoded_param["data_type"] = getattr(__builtins__, encoded_param["data-type"])
        del encoded_param["data-type"]

    if "unit" in encoded_param:
        encoded_param["unit"] = json_decode_unit(encoded_param["unit"])

    if "extent" in encoded_param:
        encoded_param["extent"] = json_decode_extents(encoded_param["extent"])

    # TODO deserialise measurementType once it's added to model
    # TODO deserialise categoryEncoding, once it's added to model

    return Parameter(**encoded_param)


def json_decode_symbol(encoded_symbol: Dict[str, Any]) -> Symbol:
    return Symbol(**encoded_symbol)


def json_decode_unit(encoded_unit: Dict[str, Any]) -> Unit:
    if "symbol" in encoded_unit:
        if isinstance(encoded_unit["symbol"], dict):
            encoded_unit["symbol"] = json_decode_symbol(encoded_unit["symbol"])
    if "labels" in encoded_unit:
        # Note, the field is called `label` in the serialised output, even though it can hold multiple values
        if isinstance(encoded_unit["label"], dict):
            encoded_unit["label"] = LanguageMap.from_json(encoded_unit["label"])

    return Unit(**encoded_unit)


def json_decode_vertical_extent(encoded_vertical_extent: Dict[str, Any]) -> VerticalExtent:
    encoded_vertical_extent["vrs"] = pyproj.CRS(encoded_vertical_extent["vrs"])
    return VerticalExtent(**encoded_vertical_extent)
