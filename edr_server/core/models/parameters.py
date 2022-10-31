from dataclasses import dataclass
from typing import List, Optional, Type, Union, Dict, Any, Set

from . import EdrModel, JsonDict
from .extents import Extents
from .i18n import LanguageMap
from .urls import URL

ParameterDataType = Union[Type[int], Type[float], Type[str]]


@dataclass
class Symbol(EdrModel["Symbol"]):
    """
    Based on an except from
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/e8a78f9/standard/openapi/schemas/units.yaml
    """

    value: str  # Like K for kelvin or KM for kilometer, hPa for hectopascals, etc
    # noinspection HttpUrlsUsage
    type: URL = URL("http://www.opengis.net/def/uom/UCUM/")  # TODO: Is a value we can use as a sensible default?

    @classmethod
    def _prepare_json_for_init(cls, json_dict: JsonDict) -> JsonDict:
        return json_dict

    @classmethod
    def _get_allowed_json_keys(cls) -> Set[str]:
        return {"value", "type"}

    def to_json(self) -> Dict[str, Any]:
        return {"value": self.value, "type": self.type}


@dataclass
class Unit(EdrModel["Unit"]):
    """
    Based on
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/e8a78f9/standard/openapi/schemas/units.yaml
    """

    # Either a string, or a dict of language codes mapped to strings
    labels: Optional[Union[LanguageMap, str]] = None  # The display name, like Kelvin or Meters
    symbol: Optional[Union[Symbol, str]] = None
    id: Optional[str] = None

    @classmethod
    def _prepare_json_for_init(cls, json_dict: JsonDict) -> JsonDict:
        if "symbol" in json_dict and isinstance(json_dict["symbol"], dict):
            json_dict["symbol"] = Symbol.from_json(json_dict["symbol"])

        if "label" in json_dict and isinstance(json_dict["label"], dict):
            # Note, the field is called `label` in the serialised output, even though it can hold multiple values
            json_dict["label"] = LanguageMap.from_json(json_dict["label"])

        if "label" in json_dict and isinstance(json_dict["label"], (str, LanguageMap)):
            json_dict["labels"] = json_dict.pop('label')

        return json_dict

    @classmethod
    def _get_allowed_json_keys(cls) -> Set[str]:
        return {"symbol", "label", "id"}

    def __post_init__(self):
        # hook called by Python dataclass after the auto-generated __init__
        if not (self.labels or self.symbol):
            raise ValueError("Arguments for at least one of the 'labels' or 'symbol' parameters must be supplied")

    def to_json(self) -> Dict[str, Any]:
        encoded_unit = {}

        if self.symbol:
            encoded_unit["symbol"] = self.symbol if isinstance(self.symbol, str) else self.symbol.to_json()
        if self.labels:
            # Note, the field is called `label` in the serialised output, even though it can hold a LanguageMap
            encoded_unit["label"] = self.labels if isinstance(self.labels, str) else self.labels.to_json()
        if self.id:
            encoded_unit["id"] = self.id

        return encoded_unit


@dataclass
class Category(EdrModel["Category"]):
    """
    Based on an except from
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/fa594ca/standard/openapi/schemas/observedPropertyCollection.yaml
    """
    id: URL
    label: Union[LanguageMap, str]
    description: Optional[Union[LanguageMap, str]] = None

    @classmethod
    def _prepare_json_for_init(cls, json_dict: JsonDict) -> JsonDict:
        if isinstance(json_dict["label"], dict):
            json_dict["label"] = LanguageMap.from_json(json_dict["label"])

        if "description" in json_dict and isinstance(json_dict["description"], dict):
            json_dict["description"] = LanguageMap.from_json(json_dict["description"])

        return json_dict

    @classmethod
    def _get_allowed_json_keys(cls) -> Set[str]:
        return {"id", "label", "description"}

    def to_json(self) -> Dict[str, Any]:
        j_dict = {
            "id": self.id,
            "label": self.label if isinstance(self.label, str) else self.label.to_json()
        }

        if self.description:
            j_dict["description"] = (
                self.description if isinstance(self.description, str) else self.description.to_json()
            )

        return j_dict


@dataclass
class ObservedProperty(EdrModel["ObservedProperty"]):
    """
    Based on
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/fa594ca/standard/openapi/schemas/observedPropertyCollection.yaml
    """
    label: Union[LanguageMap, str]  # E.g.  Sea Ice Concentration
    # URI linking to an external registry which contains the definitive definition of the observed property
    id: Optional[URL] = None  # E.g. http://vocab.nerc.ac.uk/standard_name/sea_ice_area_fraction/
    description: Optional[str] = None
    categories: Optional[List[Category]] = None

    @classmethod
    def _prepare_json_for_init(cls, json_dict: JsonDict) -> JsonDict:
        if "label" in json_dict and isinstance(json_dict["label"], dict):
            json_dict["label"] = LanguageMap.from_json(json_dict["label"])

        if "categories" in json_dict:
            json_dict["categories"] = [Category.from_json(cat) for cat in json_dict["categories"]]

        return json_dict

    @classmethod
    def _get_allowed_json_keys(cls) -> Set[str]:
        return {"label", "id", "description", "categories"}

    def to_json(self) -> Dict[str, Any]:
        j_dict = {
            "label": self.label if isinstance(self.label, str) else self.label.to_json(),
        }
        if self.id:
            j_dict["id"] = self.id
        if self.description:
            j_dict["description"] = self.description
        if self.categories:
            j_dict["categories"] = [cat.to_json() for cat in self.categories]

        return j_dict


@dataclass
class Parameter(EdrModel["Parameter"]):
    """
    Based on
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/e8a78f9/standard/openapi/schemas/parameterNames.yaml
    """
    id: str
    unit: Unit
    observed_property: ObservedProperty
    data_type: Optional[ParameterDataType] = None
    description: Optional[Union[LanguageMap, str]] = None
    label: Optional[str] = None
    extent: Optional[Extents] = None

    # TODO: measurement_type
    # TODO category_encoding

    @classmethod
    def _prepare_json_for_init(cls, json_dict: JsonDict) -> JsonDict:
        del json_dict["type"]

        json_dict["observed_property"] = ObservedProperty.from_json(json_dict["observedProperty"])
        del json_dict["observedProperty"]

        if "data-type" in json_dict:
            # This field holds a type, such as int, float, or str.
            # The code below is converting the string name of the type to the actual type object
            # Note replacement of `-` with `_` in key name
            json_dict["data_type"] = getattr(__builtins__, json_dict["data-type"])
            del json_dict["data-type"]

        if "unit" in json_dict:
            json_dict["unit"] = Unit.from_json(json_dict["unit"])

        if "extent" in json_dict:
            json_dict["extent"] = Extents.from_json(json_dict["extent"])

        # TODO deserialise measurementType once it's added to model
        # TODO deserialise categoryEncoding, once it's added to model

        return json_dict

    @classmethod
    def _get_allowed_json_keys(cls) -> Set[str]:
        return {"type", "observedProperty", "description", "label", "data-type", "unit", "extent", "id",
                "categoryEncoding", "measurementType"}

    def to_json(self) -> Dict[str, Any]:
        encoded_param = {
            "type": "Parameter",
            "observedProperty": self.observed_property.to_json(),
        }

        if self.description:
            encoded_param["description"] = self.description
        if self.label:
            encoded_param["label"] = self.label
        if self.data_type:
            encoded_param["data-type"] = self.data_type.__name__
        if self.unit:
            encoded_param["unit"] = self.unit.to_json()
        # TODO serialise categoryEncoding, once it's added to model
        if self.extent:
            encoded_param["extent"] = self.extent.to_json()
        if self.id:
            encoded_param["id"] = self.id
        # TODO serialise measurementType once it's added to model

        return encoded_param
