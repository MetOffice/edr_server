from dataclasses import dataclass, field
from typing import List

from .core import Interface


@dataclass
class Tileset:
    """For providing data from tiled nD Arrays."""
    tile_shape: list
    url_template: str


@dataclass
class Parameter:
    """An individual, data-describing phenomenon reported against a Location."""
    name: str
    id: str
    description: str
    type: str
    dtype: str
    axes: list
    shape: list
    value_type: str
    values: list
    unit: str
    unit_label: str
    unit_type: str
    phenomenon_id: str
    phenomenon: str
    measurement_type_method: str = ""
    measurement_type_period: str = ""
    category_encoding: dict = field(default_factory=dict)


@dataclass
class Referencing:
    """Definitions of reference systems for one or more coordinates of a Location."""
    coords: list
    system_type: str
    system_id: str = ""
    system_calendar: str = ""


@dataclass
class Feature:
    """An individual EDR Location (feature) instance."""
    id: str
    geometry_type: str
    coords: list
    bbox: list
    axes: list
    axis_x_values: dict
    axis_y_values: dict
    axis_z_values: dict
    axis_t_values: dict
    properties: dict
    parameters: "list[Parameter]"
    referencing: "list[Referencing]"
    temporal_interval: list = field(default_factory=list)
    vertical_interval: list = field(default_factory=list)


class Locations(Interface):
    def __init__(self, collection_id, query_parameters: dict) -> None:
        self.collection_id = collection_id
        self.query_parameters = query_parameters
        self.supported_query_params = ["bbox", "datetime"]

    def _bbox_filter(self, location: Feature) -> bool:
        raise NotImplementedError

    def _datetime_filter(self, location: Feature) -> bool:
        raise NotImplementedError

    def get_collection_bbox(self):
        """Get the bounding box for the collection that holds these locations."""
        raise NotImplementedError

    def parameters(self) -> List[Parameter]:
        """Construct the list of all parameters that can be served."""
        raise NotImplementedError

    def references(self, refs_list: List) -> List[Referencing]:
        """Construct the list of all referencing objects for the location."""
        raise NotImplementedError

    def all_locations(self) -> List[Feature]:
        raise NotImplementedError

    def locations_filter(self, locations: List[Feature]) -> List[Feature]:
        raise NotImplementedError

    def data(self) -> List[Feature]:
        return self.locations_filter(self.all_locations())


class Location(Interface):
    def __init__(self, collection_id, location_id, query_parameters: dict, items_url: str) -> None:
        self.collection_id = collection_id
        self.location_id = location_id
        self.query_parameters = query_parameters
        self.items_url = items_url

    def _parameter_filter(self, all_location_parameters) -> List:
        """
        Filter the list of all parameters provided at this location
        by the list of parameters passed in the query string, if any.

        """
        if self.query_parameters.get("parameter-name") is not None:
            query_location_parameters = set(self.query_parameters["parameter-name"])
            result = list(set(all_location_parameters) & query_location_parameters)
        else:
            result = all_location_parameters
        return result

    def _tilesets(self, param_name) -> List[Tileset]:
        """Define tilesets metadata for a specific parameter."""
        raise NotImplementedError

    def parameters(self) -> List[Parameter]:
        """
        Build a `Parameter` instance for each of the filtered parameters
        provided by `self._filter_parameters`.

        """
        raise NotImplementedError

    def data(self) -> Feature:
        raise NotImplementedError