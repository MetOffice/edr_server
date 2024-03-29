from abc import abstractmethod
from contextlib import suppress
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, TypeVar, Set, Type

from . import EdrModel, JsonDict
from ._types_and_defaults import EdrDataQuery
from .crs import CrsObject, DEFAULT_CRS
from .i18n import Iso639Alpha2LanguageCode
from .urls import URL
from ..exceptions import InvalidEdrJsonError

MimeType = str
"""
Type Alias to make intent clearer when declaring attributes & parameters intended to store mime types.

There isn't a comprehensive list of all valid MIME Types, so the best we can do is check against valid formats
That might still be too restrictive for users of the library, so for now we're not applying any validation here.
Potentially there's a discussion to be had about to what extent we want to push users to adhere to the spirit and intent
of the EDR spec, versus leaving it up to them. The answer would perhaps come down to whether EDR standard's OpenAPI
schemas are permissive by design, or because they couldn't express the concept of "a string following the conventions
of a MIME type" in that format.
 
Strictly speaking, MIME Types (aka media types) are overseen by the IANA (see 
https://www.iana.org/assignments/media-types/media-types.xhtml for the registry and 
https://www.rfc-editor.org/rfc/rfc6838.html for details of registration and registration tress & subtype names).
However, in practice not every MIME type is registered with the IANA.
For example, whilst geojson has an official entry, covJSON does not, despite the covJSON specification defining a
canonical MIME type of application/prs.coverage+json (incidentally, the `prs.` prefix indicates the "personal 
registration tree" as defined by RFC 6838).
Another example, netCDF doesn't have an entry in the IANA registry, but seems to be declared by convention as 
application/netcdf or application/x-netcdf. (Although, if abiding by RFC 6838, application/x.netcdf might be more 
appropriate, as `x.` is the prefix for unregistered media types. I believe `x-` is a deprecated format predating that 
RFC)
"""


@dataclass
class Link(EdrModel["Link"]):
    """
    A simple link that can be used in the "links" section of an EDR response.
    EDR draws on RFC8288 for its approach to linking: https://www.rfc-editor.org/rfc/rfc8288.txt

    Based on
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/link.yaml
    """
    href: URL  # The target of the link, the page it links to
    rel: str
    """
    Relation between the current resource and link target. See https://microformats.org/wiki/rel-faq#How_is_rel_used
    E.g. See https://html.spec.whatwg.org/multipage/links.html#linkTypes for standard HTML values.
    E.g. See https://microformats.org/wiki/existing-rel-values for registered HTML extensions and other uses 
    """
    type: Optional[MimeType] = None
    """MIME type of the linked resource. There's some more docs about MimeTypes in general where the type is defined."""
    hreflang: Optional[Iso639Alpha2LanguageCode] = None
    title: Optional[str] = None
    length: Optional[int] = None

    @classmethod
    def _prepare_json_for_init(cls, json_dict: JsonDict) -> JsonDict:
        json_dict["href"] = URL(json_dict["href"])
        return json_dict

    @classmethod
    def _get_allowed_json_keys(cls) -> Set[str]:
        return {"title", "href", "rel", "type", "hreflang", "length"}

    def to_json(self) -> Dict[str, Any]:
        encoded_link = {
            "href": self.href,
            "rel": self.rel,
        }

        # Optional stuff
        if self.title:
            encoded_link["title"] = self.title
        if self.type:
            encoded_link["type"] = self.type
        if self.hreflang:
            encoded_link["hreflang"] = self.hreflang
        if self.length:
            encoded_link["length"] = self.length

        return encoded_link


U = TypeVar("U", bound="AbstractDataQuery")


class AbstractDataQuery(EdrModel[U]):

    @classmethod
    def _prepare_json_for_init(cls, json_dict: JsonDict) -> JsonDict:
        """
        Does any necessary conversion to the json dict to prep it for passing to the class' `__init__` method.
        E.g. converting nested objects.
        This method can be extended by subclasses to perform additional preparation, e.g.
        >>> # noinspection PyProtectedMember, PyShadowingNames, PyUnresolvedReferences
        >>> def _prepare_json_for_init(cls, json_dict: JsonDict) -> JsonDict:
        >>>     json_dict =  super()._prepare_json_for_init(json_dict)
        >>>     # Do extra prep...
        >>>     return json_dict

        Creates a shallow copy of the input dict, so be careful about modifying nested lists/dicts in place!
        """
        kwargs = json_dict.copy()

        if "query_type" in json_dict:
            expected_query_type = cls.get_query_type().name.lower()
            if json_dict["query_type"] != expected_query_type:
                raise InvalidEdrJsonError(
                    f"JSON has 'query_type'={json_dict['query_type']!r} but {expected_query_type!r} was expected")
            del kwargs["query_type"]

        return kwargs

    @classmethod
    @abstractmethod
    def get_query_type(cls) -> EdrDataQuery:
        # I want each subclass to provide the correct value for this, and also want it accessible to the class method
        # from_json(). I'd prefer it to be an abstract class property, but that's not a standard feature of python, and
        # I wanted to avoid adding a bunch of extra code to support it.
        raise NotImplementedError

    @classmethod
    def _get_allowed_json_keys(cls) -> Set[str]:
        return {"title", "description", "query_type"}

    def __init__(self, title: Optional[str] = None, description: Optional[str] = None):
        super().__init__(self)
        if title is None:
            self._title = f"{self.get_query_type().name.title()} Data Query"
        else:
            self._title = title

        if description is None:
            query_type = self.get_query_type()
            query_type_str = query_type.name.lower()
            if query_type is not EdrDataQuery.RADIUS:
                query_type_str = query_type_str.rstrip('s')
            self._description = f"Select data that is within a defined {query_type_str}."
        else:
            self._description = description

    def __str__(self):
        return f"{self.title} ({self.description})"

    def __repr__(self) -> str:
        """
        Gets a python representation of this object. It's intended that it's valid code that could be copy/pasted
        and executed to create an equivalent object.
        """
        str_args = ", ".join(repr(v) for v in self._key())
        return f"{self.__class__.__name__}({str_args})"

    def __eq__(self, other: Any) -> bool:
        """
        Returns `True` if argument is equal to this object, `False` otherwise.
        You shouldn't need to modify this method, just override and extend the `_key()` method
        """
        return self._key() == other._key() if isinstance(other, AbstractDataQuery) else False

    @abstractmethod
    def _key(self) -> tuple:
        """
        Used to construct a tuple of values to use in hashing, equality comparisons, and __repr__ (so it's important
        the order matches __init__)

        Marked as abstract to provide a prompt to implementors of subclasses to remember to check if they need to
        extend it. In some cases this will result in subclasses having to implement something like this:
        >>> # noinspection PyProtectedMember, PyShadowingNames, PyUnresolvedReferences
        >>> def _key(self) -> tuple:
        >>>     return super()._key()
        On the whole however, this reduces the risk of bugs arising from missing attributes from equality comparisons
        """
        return self._title, self._description, self.get_query_type()

    @property
    def title(self) -> Optional[str]:
        return self._title

    @property
    def description(self) -> Optional[str]:
        return self._description

    def to_json(self) -> Dict[str, Any]:
        # Docstring inherited from EdrModel
        j_dict = {
            "query_type": self.get_query_type().name.lower()
        }
        if self._title is not None:
            j_dict["title"] = self._title
        if self._description is not None:
            j_dict["description"] = self._description

        return j_dict


class ItemsDataQuery(AbstractDataQuery["ItemsDataQuery"]):

    def __init__(
            self,
            title: Optional[str] = None,
            description: Optional[str] = 'Select data based on predetermined groupings of data organised into items.'
    ):
        super().__init__(title, description)

    @classmethod
    def get_query_type(cls) -> EdrDataQuery:
        return EdrDataQuery.ITEMS

    def _key(self) -> tuple:
        return super()._key()


E = TypeVar("E", bound="AbstractSpatialDataQuery")


class AbstractSpatialDataQuery(AbstractDataQuery[E]):
    """
    The Data Query objects describe any metadata that's specific to particular EDR queries.
    They are tied to specific collections, and hence can vary from collection to collection.
    """

    def __init__(
            self, title: Optional[str] = None, description: Optional[str] = None,
            output_formats: Optional[List[str]] = None, default_output_format: Optional[str] = None,
            crs_details: Optional[List[CrsObject]] = None,
    ):
        super().__init__(title, description)

        self._output_formats = output_formats

        if default_output_format:
            self._default_output_format = default_output_format
        elif self._output_formats:
            self._default_output_format = self._output_formats[0]
        else:
            self._default_output_format = None

        self._crs_details = [DEFAULT_CRS] if crs_details is None else crs_details

    @classmethod
    def _get_allowed_json_keys(cls) -> Set[str]:
        return super()._get_allowed_json_keys().union({"output_formats", "default_output_format", "crs_details"})

    @classmethod
    def _prepare_json_for_init(cls, json_dict: JsonDict) -> JsonDict:
        """
        Does any necessary conversion to the json dict to prep it for passing to the class' `__init__` method.
        E.g. converting nested objects.
        This method can be extended by subclasses to perform additional preparation, e.g.
        >>> # noinspection PyProtectedMember, PyShadowingNames, PyUnresolvedReferences
        >>> def _prepare_json_for_init(cls, json_dict: JsonDict) -> JsonDict:
        >>>     json_dict =  super()._prepare_json_for_init(json_dict)
        >>>     # Do extra prep...
        >>>     return json_dict

        Creates a shallow copy of the input dict, so be careful about modifying nested lists/dicts in place!
        """
        kwargs = super()._prepare_json_for_init(json_dict)

        if "crs_details" in kwargs:
            kwargs["crs_details"] = [CrsObject.from_json(crs) for crs in kwargs["crs_details"].values()]

        return kwargs

    @abstractmethod
    def _key(self) -> tuple:
        """
        Used to construct a tuple of values to use in hashing, equality comparisons, and __repr__ (so it's important
        the order matches __init__)

        Marked as abstract to provide a prompt to implementors of subclasses to remember to check if they need to
        extend it. In some cases this will result in subclasses having to implement something like this:
        >>> # noinspection PyProtectedMember, PyShadowingNames, PyUnresolvedReferences
        >>> def _key(self) -> tuple:
        >>>     return super()._key()
        On the whole however, this reduces the risk of bugs arising from missing attributes from equality comparisons
        """
        return super()._key() + (self._output_formats, self._default_output_format, self._crs_details)

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

    def to_json(self) -> JsonDict:
        # docstring inherited from EdrModel
        j_dict = super().to_json()
        if self._output_formats:  # Slightly different from the others, we only include it if the list has values
            j_dict["output_formats"] = self._output_formats
        if self._default_output_format is not None:
            j_dict["default_output_format"] = self._default_output_format
        if self._crs_details is not None:
            j_dict["crs_details"] = {crs.name: crs.to_json() for crs in self._crs_details}

        return j_dict


class AreaDataQuery(AbstractSpatialDataQuery["AreaDataQuery"]):
    """Class that describes any metadata that's specific to Area queries"""

    @classmethod
    def get_query_type(cls) -> EdrDataQuery:
        return EdrDataQuery.AREA

    def _key(self) -> tuple:
        return super()._key()


class CorridorDataQuery(AbstractSpatialDataQuery["CorridorDataQuery"]):
    """Collection-specific metadata for corridor queries"""

    def __init__(
            self,
            title: Optional[str] = None, description: Optional[str] = None, output_formats: Optional[List[str]] = None,
            default_output_format: Optional[str] = None, crs_details: Optional[List[CrsObject]] = None,
            width_units: Optional[List[str]] = None, height_units: Optional[List[str]] = None
    ):
        super().__init__(title, description, output_formats, default_output_format, crs_details)
        self._width_units = width_units
        self._height_units = height_units

    @classmethod
    def _get_allowed_json_keys(cls) -> Set[str]:
        return super()._get_allowed_json_keys().union({"width_units", "height_units"})

    @classmethod
    def get_query_type(cls) -> EdrDataQuery:
        # docstring inherited
        return EdrDataQuery.CORRIDOR

    @classmethod
    def from_json(cls, json_dict: JsonDict) -> E:
        # docstring inherited
        return super().from_json(json_dict)

    def _key(self) -> tuple:
        # docstring inherited
        return super()._key() + (self._width_units, self._height_units)

    @property
    def width_units(self) -> List[str]:
        """Units that can be used to specify corridor width in queries"""
        return self._width_units if self._width_units is not None else []

    @property
    def height_units(self) -> List[str]:
        """Units that can be used to specify corridor height in queries"""
        return self._height_units if self._height_units is not None else []

    def to_json(self) -> JsonDict:
        # docstring inherited
        j_dict = super().to_json()

        if self._width_units:  # Only include when list has values
            j_dict["width_units"] = self._width_units

        if self._height_units:  # Only include when list has values
            j_dict["height_units"] = self._height_units

        return j_dict


class CubeDataQuery(AbstractSpatialDataQuery["CubeDataQuery"]):
    """Collection-specific metadata for cube queries"""

    def __init__(
            self,
            title: Optional[str] = None, description: Optional[str] = None, output_formats: Optional[List[str]] = None,
            default_output_format: Optional[str] = None, crs_details: Optional[List[CrsObject]] = None,
            height_units: Optional[List[str]] = None
    ) -> None:
        super().__init__(title, description, output_formats, default_output_format, crs_details)
        self._height_units = height_units

    @classmethod
    def _get_allowed_json_keys(cls) -> Set[str]:
        return super()._get_allowed_json_keys().union({"height_units"})

    @classmethod
    def get_query_type(cls) -> EdrDataQuery:
        # docstring inherited
        return EdrDataQuery.CUBE

    def _key(self) -> tuple:
        # docstring inherited
        # The alternative was `tuple([self._height_units])` and I wanted to avoid the unnecessary creation of a list
        return super()._key() + (self._height_units,)  # Brackets and comma indicate this is a literal tuple.

    @property
    def height_units(self) -> List[str]:
        """Units that can be used to specify corridor height in queries"""
        return self._height_units if self._height_units is not None else []

    def to_json(self) -> JsonDict:
        j_dict = super().to_json()
        if self._height_units:
            j_dict["height_units"] = self._height_units
        return j_dict


class LocationsDataQuery(AbstractSpatialDataQuery["LocationsDataQuery"]):
    """Collection-specific metadata for locations queries"""

    @classmethod
    def get_query_type(cls) -> EdrDataQuery:
        return EdrDataQuery.LOCATIONS

    def _key(self) -> tuple:
        return super()._key()


class PositionDataQuery(AbstractSpatialDataQuery["PositionDataQuery"]):
    """Collection-specific metadata for locations queries"""

    @classmethod
    def get_query_type(cls) -> EdrDataQuery:
        return EdrDataQuery.POSITION

    def _key(self) -> tuple:
        return super()._key()


class RadiusDataQuery(AbstractSpatialDataQuery["RadiusDataQuery"]):
    def __init__(
            self, title: Optional[str] = None, description: Optional[str] = None,
            output_formats: Optional[List[str]] = None, default_output_format: Optional[str] = None,
            crs_details: Optional[List[CrsObject]] = None, within_units: Optional[List[str]] = None
    ):
        super().__init__(title, description, output_formats, default_output_format, crs_details)
        self._within_units = within_units

    @classmethod
    def _get_allowed_json_keys(cls) -> Set[str]:
        return super()._get_allowed_json_keys().union({"within_units"})

    def to_json(self) -> JsonDict:
        j_dict = super().to_json()
        if self._within_units:
            j_dict["within_units"] = self._within_units
        return j_dict

    @classmethod
    def get_query_type(cls) -> EdrDataQuery:
        return EdrDataQuery.RADIUS

    def _key(self) -> tuple:
        return super()._key() + (self._within_units,)

    @property
    def within_units(self) -> Optional[List[str]]:
        return self._within_units if self._within_units is not None else []


class TrajectoryDataQuery(AbstractSpatialDataQuery["TrajectoryDataQuery"]):

    def _key(self) -> tuple:
        return super()._key()

    @classmethod
    def get_query_type(cls) -> EdrDataQuery:
        return EdrDataQuery.TRAJECTORY


@dataclass
class DataQueryLink(Link):
    """
    Extended version of a simple link for use in the data_queries section of a collection metadata response.

    EDR draws on RFC8288 for its approach to linking: https://www.rfc-editor.org/rfc/rfc8288.txt

    Object based on these EDR schemas (as they were in commit 546c338):
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
    variables: Optional[AbstractDataQuery] = None

    @classmethod
    def _get_allowed_json_keys(cls) -> Set[str]:
        return super()._get_allowed_json_keys().union({"templated", "variables"})

    @classmethod
    def _prepare_json_for_init(cls, json_dict: JsonDict) -> JsonDict:
        json_dict = super()._prepare_json_for_init(json_dict)
        if "variables" in json_dict:

            try:
                actual_query_type = json_dict["variables"]["query_type"]
            except KeyError:
                # Interesting point, the structure of the `data_queries` object in the collections JSON uses query type
                # as a key, so we could infer query type from that if it's not otherwise present. However, we don't have
                # access to that here. A simple approach would be for the `CollectionMetadata.from_json` method to check
                # if the query_type is missing and add one based on the inferred type before calling
                # `DataQueryLink.from_json`, but that'd break the encapsulation of knowledge of the DataQueryLink JSON
                # format within this class. We could wrap that logic in a method on `DataQueryLink`, however, that'd
                # update the JSON with the inferred type and then call the `DataQueryLink.from_json` method as normal.
                # The awkwardness with that would be how would `CollectionMetadata` know to call it? We'd need a more
                # specialised exception subclass to identify that error case from other invalid JSON errors
                raise InvalidEdrJsonError("'query_type' missing from data query JSON")
            data_query_cls = DATA_QUERY_MAP[actual_query_type]
            json_dict["variables"] = data_query_cls.from_json(json_dict["variables"])

        with suppress(KeyError):
            del json_dict["templated"]

        return json_dict

    @property
    def templated(self) -> bool:
        """All EDR's data query links are templated"""
        return self.variables is not None

    def to_json(self) -> Dict[str, Any]:
        j_dict = super().to_json()

        if self.variables:
            j_dict["variables"] = self.variables.to_json()
            j_dict["templated"] = True

        return j_dict


DATA_QUERY_MAP: Dict[str, Type[AbstractDataQuery]] = {
    "area": AreaDataQuery,
    "corridor": CorridorDataQuery,
    "cube": CubeDataQuery,
    "items": ItemsDataQuery,
    "locations": LocationsDataQuery,
    "position": PositionDataQuery,
    "radius": RadiusDataQuery,
    "trajectory": TrajectoryDataQuery,
}
"""
A map of EdrDataQuery enum values to the Data Query classes that represent those query types. 
Keys belong to this set: {edr_data_query.value for edr_data_query in EdrDataQuery}
"""
