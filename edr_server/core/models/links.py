from dataclasses import dataclass, field
from typing import Optional, List

import pyproj

from ._types_and_defaults import EdrDataQuery, DEFAULT_CRS, CollectionId
from .urls import EdrUrlResolver


@dataclass
class Link:
    """
    A simple link that can be used in the "links" section of an EDR response
    Based on
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/link.yaml
    """
    href: str
    rel: str
    type: Optional[str] = None
    hreflang: Optional[str] = None
    title: Optional[str] = None
    length: Optional[int] = None


@dataclass
class DataQuery:
    """
    Based on
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/areaDataQuery.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/corridorDataQuery.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/cubeDataQuery.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/itemsDataQuery.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/locationsDataQuery.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/positionDataQuery.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/radiusDataQuery.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/trajectoryDataQuery.yaml
    """
    # TODO: Consider creating EDR query specific classes that only have the fields that are allowed for that query
    #       rather than having a single class that has all the fields and permits combinations that aren't actually
    #       valid? Might make things clearer. E.g. Position doesn't use within_units, height_units, or width_units,
    #       but it's possible to create a Position Data Query instance with those set. A Position specific class would
    #       only accept arguments that are allowed for a Position query.
    title: Optional[str] = None
    description: Optional[str] = None
    query_type: Optional[EdrDataQuery] = None
    within_units: Optional[List[str]] = None
    width_units: Optional[List[str]] = None
    height_units: Optional[List[str]] = None
    output_formats: Optional[List[str]] = None
    default_output_format: Optional[str] = None
    crs_details: Optional[List[pyproj.CRS]] = field(default_factory=lambda: [DEFAULT_CRS])

    @staticmethod
    def get_data_query(
            query_type,
            output_formats: List[str],
            height_units: List[str] = None,
            width_units: List[str] = None,
            within_units: List[str] = None,
            crs_details: List[pyproj.CRS] = None
    ) -> "DataQuery":

        kwargs = {
            "title": f"{query_type.name.title()} Query",
            "query_type": query_type,
            "output_formats": output_formats,
            "default_output_format": output_formats[0],
            "crs_details": crs_details if crs_details else [DEFAULT_CRS]
        }

        if query_type is EdrDataQuery.AREA:
            kwargs["description"] = "Query to return data for a defined area"
            if height_units:
                kwargs["height_units"] = height_units

        elif query_type is EdrDataQuery.CORRIDOR:
            kwargs["description"] = ("Query to return data for a corridor of specified height and width along a "
                                     "trajectory defined using WKT")
            if height_units:
                kwargs["height_units"] = height_units
            if width_units:
                kwargs["width_units"] = width_units

        elif query_type is EdrDataQuery.CUBE:
            kwargs["description"] = "Query to return data for a cuboid defined by a bounding box and height"
            if height_units:
                kwargs["height_units"] = height_units

        elif query_type is EdrDataQuery.ITEMS:
            kwargs["description"] = "Query to return data for specific item"

        elif query_type is EdrDataQuery.LOCATIONS:
            kwargs["description"] = "Query to return data for a specific location"

        elif query_type is EdrDataQuery.POSITION:
            kwargs["description"] = "Query to return data for a defined well known text point"

        elif query_type is EdrDataQuery.RADIUS:
            kwargs["description"] = (
                "Query to return data for a circle defined by a well known text point and radius around it")
            if within_units:
                kwargs["within_units"] = within_units

        elif query_type is EdrDataQuery.TRAJECTORY:
            kwargs["description"] = "Query to return data for a defined well known text trajectory"

        return DataQuery(**kwargs)


@dataclass
class DataQueryLink:
    """
    Extended version of a simple link for use in the data_queries section of a collection metadata response
    Based on
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/link.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/areaLink.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/corridorLink.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/cubeLink.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/itemsLink.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/locationsLink.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/positionLink.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/radiusLink.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/trajectoryLink.yaml

    """
    # Didn't use inheritance here due to the way dataclasses interacts with the mixture of default and non-default
    # values in the fields. TLDR: it leads to a "Non-default argument(s) follows default argument(s) defined in 'Link'"
    # error. Further detail here:
    # https://stackoverflow.com/questions/51575931/class-inheritance-in-python-3-7-dataclasses
    # Duplication was the easiest workaround
    href: str
    rel: str
    variables: DataQuery
    type: Optional[str] = None
    hreflang: Optional[str] = None
    title: Optional[str] = None
    length: Optional[int] = None

    @property
    def templated(self):
        """All EDR's data query links are templated"""
        return True

    @staticmethod
    def get_data_query_link(
            query_type,
            collection_id: CollectionId,
            urls: EdrUrlResolver,
            output_formats: List[str],
            height_units: List[str] = None,
            width_units: List[str] = None,
            within_units: List[str] = None,
            crs_details: List[pyproj.CRS] = None
    ) -> "DataQueryLink":
        if crs_details is None:
            crs_details = [DEFAULT_CRS]

        return DataQueryLink(
            href=urls.COLLECTION_DATA_QUERY_MAP[query_type](collection_id),
            rel="data",
            variables=DataQuery.get_data_query(
                query_type, output_formats, height_units, width_units, within_units, crs_details),
            type=query_type.name.lower(),
            hreflang="en",
            title=query_type.name.title(),
        )
