from abc import abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, TypeVar

from pyproj import CRS

from . import EdrModel
from ._types_and_defaults import CollectionId, EdrDataQuery
from .crs import CrsObject, DEFAULT_CRS
from .urls import URL, EdrUrlResolver
from ..exceptions import InvalidEdrJsonError


@dataclass
class Link:
    """
    A simple link that can be used in the "links" section of an EDR response
    Based on
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/link.yaml
    """
    href: URL
    rel: str
    type: Optional[str] = None
    hreflang: Optional[str] = None
    title: Optional[str] = None
    length: Optional[int] = None


@dataclass
class OldDataQuery:
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
    crs_details: Optional[List[CRS]] = field(default_factory=lambda: [DEFAULT_CRS])

    @staticmethod
    def get_data_query(
            query_type,
            output_formats: List[str],
            height_units: List[str] = None,
            width_units: List[str] = None,
            within_units: List[str] = None,
            crs_details: List[CRS] = None
    ) -> "OldDataQuery":

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

        return OldDataQuery(**kwargs)


E = TypeVar("E", bound="AbstractDataQuery")


class AbstractDataQuery(EdrModel[E]):

    def __init__(
            self, output_formats: Optional[List[str]] = None, default_output_format: Optional[str] = None,
            crs_details: Optional[List[CrsObject]] = None, title: Optional[str] = None,
            description: Optional[str] = None,
    ):
        if crs_details is None:
            crs_details = [DEFAULT_CRS]

        self._title = title
        self._description = description
        self._output_formats = output_formats

        if default_output_format:
            self._default_output_format = default_output_format
        elif self._output_formats:
            self._default_output_format = self._output_formats[0]
        else:
            self._default_output_format = None

        self._crs_details = crs_details

    def _key(self) -> tuple:
        """Used to construct a tuple of values to use in hashing and equality comparisons"""
        return self._title, self._description, self._output_formats, self._default_output_format, self._crs_details

    def __eq__(self, other: Any) -> bool:
        return self._key() == other._key() if isinstance(other, AbstractDataQuery) else False

    @classmethod
    @abstractmethod
    def get_query_type(cls) -> EdrDataQuery:
        # I want each subclass to provide the correct value for this, and also want it accessible to the class method
        # from_json(). I'd prefer it to be an abstract class property, but abstract class method is the best I
        # could find a reasonable way of implementing without adding a bunch of extra code
        raise NotImplemented

    @property
    def title(self) -> Optional[str]:
        return self._title

    @property
    def description(self) -> Optional[str]:
        return self._description

    @property
    def output_formats(self) -> List[str]:
        return self._output_formats if self._output_formats else []

    @property
    def default_output_format(self) -> Optional[str]:
        return self._default_output_format

    @property
    def crs_details(self) -> Optional[List[CrsObject]]:
        return self._crs_details

    def to_json(self) -> Dict[str, Any]:
        j_dict = {
            "query_type": self.get_query_type().name.lower()
        }
        if self._title is not None:
            j_dict["title"] = self._title
        if self._description is not None:
            j_dict["description"] = self._description
        if self._output_formats:  # Slightly different from the others, we only include it if the list has values
            j_dict["output_formats"] = self._output_formats
        if self._default_output_format is not None:
            j_dict["default_output_format"] = self._default_output_format
        if self._crs_details is not None:
            j_dict["crs_details"] = [crs.to_json() for crs in self._crs_details]

        return j_dict

    @classmethod
    def from_json(cls, json_dict: Dict[str, Any]) -> E:
        kwargs = json_dict.copy()

        if "query_type" in json_dict:
            expected_query_type = cls.get_query_type().name.lower()
            if json_dict["query_type"] != expected_query_type:
                raise InvalidEdrJsonError(f"JSON has 'query_type'={json_dict['query_type']!r}"
                                          f" but {expected_query_type!r} was expected")
            del kwargs["query_type"]

        if "crs_details" in kwargs:
            kwargs["crs_details"] = [CrsObject.from_json(crs) for crs in kwargs["crs_details"]]

        return cls(**kwargs)


class AreaDataQuery(AbstractDataQuery["AreaDataQuery"]):

    def __init__(
            self,
            output_formats: Optional[List[str]] = None, default_output_format: Optional[str] = None,
            crs_details: Optional[List[CrsObject]] = None,
            title: Optional[str] = "Area Data Query",
            description: Optional[str] = "Query to return data for a defined area",
    ):
        super().__init__(output_formats, default_output_format, crs_details, title, description)

    @classmethod
    def get_query_type(cls) -> EdrDataQuery:
        return EdrDataQuery.AREA


CORRIDOR = "corridor"
CUBE = "cube"
ITEMS = "items"
LOCATIONS = "locations"
POSITION = "position"
RADIUS = "radius"
TRAJECTORY = "trajectory"


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
    href: URL
    rel: str
    variables: OldDataQuery
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
            crs_details: List[CRS] = None
    ) -> "DataQueryLink":
        if crs_details is None:
            crs_details = [DEFAULT_CRS]

        return DataQueryLink(
            href=urls.COLLECTION_DATA_QUERY_MAP[query_type](collection_id),
            rel="data",
            variables=OldDataQuery.get_data_query(
                query_type, output_formats, height_units, width_units, within_units, crs_details),
            type=query_type.name.lower(),
            hreflang="en",
            title=query_type.name.title(),
        )
