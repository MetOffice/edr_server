from abc import abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, TypeVar, Set

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


JsonDict = Dict[str, Any]
U = TypeVar("U", bound="AbstractDataQuery")


class AbstractDataQuery(EdrModel[U]):
    _EXPECTED_JSON_KEYS: Set[str] = {
        "title",
        "description",
        "query_type",
    }

    @classmethod
    def _validate_json_keys(cls, json_dict: JsonDict) -> None:
        """
        Raises an InvalidJsonError if any unexpected keys are found.
        `_EXPECTED_JSON_KEYS` can be overridden in subclasses to add additional expected keys, so in practice you
        shouldn't need to modify this method.
        """
        if invalid_keys := json_dict.keys() - cls._EXPECTED_JSON_KEYS:  # Performs set difference.
            # The dictionary view returned by .keys() doesn't support the named set methods, but does support the set
            # operators defined in collections.abc.Set
            raise InvalidEdrJsonError(f"Unexpected keys in JSON dict: {invalid_keys!r}")

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
    def from_json(cls, json_dict: JsonDict) -> U:
        # docstring inherited from EdrModel
        # Subclasses may need different behaviour for converting from JSON, but implementors shouldn't need to modify
        # this method. `_prepare_json_for_init` can be overridden to control how the JSON dict is converted into a form
        # that can be passed to the __init__ method, and additional keys for validation can be added to
        # `_EXPECTED_JSON_KEYS`.
        cls._validate_json_keys(json_dict)
        prepared_dict = cls._prepare_json_for_init(json_dict)
        return cls(**prepared_dict)

    @classmethod
    @abstractmethod
    def get_query_type(cls) -> EdrDataQuery:
        # I want each subclass to provide the correct value for this, and also want it accessible to the class method
        # from_json(). I'd prefer it to be an abstract class property, but that's not a standard feature of python, and
        # I wanted to avoid adding a bunch of extra code to support it.
        raise NotImplemented

    def __init__(self, title: Optional[str] = None, description: Optional[str] = None):

        if title is None:
            self._title = f"{self.get_query_type().name.title()} Data Query"
        else:
            self._title = title

        if description is None:
            query_type = self.get_query_type().name.lower().rstrip('s')
            self._description = f"Select data that is within a defined {query_type}."
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

    _EXPECTED_JSON_KEYS: Set[str] = AbstractDataQuery._EXPECTED_JSON_KEYS.union({
        "output_formats",
        "default_output_format",
        "crs_details",
    })

    def __init__(  # TODO change order of arguments so that subclass args come after superclass
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

    _EXPECTED_JSON_KEYS = AbstractSpatialDataQuery._EXPECTED_JSON_KEYS.union({"width_units", "height_units"})

    def __init__(
            self,
            output_formats: Optional[List[str]] = None, default_output_format: Optional[str] = None,
            crs_details: Optional[List[CrsObject]] = None, title: Optional[str] = None,
            description: Optional[str] = None, width_units: Optional[List[str]] = None,
            height_units: Optional[List[str]] = None,
    ):
        super().__init__(title, description, output_formats, default_output_format, crs_details)
        self._width_units = width_units
        self._height_units = height_units

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

    _EXPECTED_JSON_KEYS = AbstractSpatialDataQuery._EXPECTED_JSON_KEYS.union({"height_units"})

    def __init__(
            self,
            output_formats: Optional[List[str]] = None, default_output_format: Optional[str] = None,
            crs_details: Optional[List[CrsObject]] = None, title: Optional[str] = None,
            description: Optional[str] = None, height_units: Optional[List[str]] = None,
    ) -> None:
        super().__init__(title, description, output_formats, default_output_format, crs_details)
        self._height_units = height_units

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
    variables: OldDataQuery  # TODO replace with new AbstractSpatialDataQuery. How to handle heterogeneous subclasses though?
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
