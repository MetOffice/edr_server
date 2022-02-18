from dataclasses import dataclass, field
from typing import List

from .core import Interface


@dataclass
class Parameter:
    id: str
    name: str
    description: str
    unit: str
    unit_label: str
    unit_type: str
    phenomenon_id: str
    phenomenon: str
    measurement_type_method: str = ""
    measurement_type_period: str = ""
    category_encoding: dict = field(default_factory=dict)


@dataclass
class Location:
    id: str
    geometry_type: str
    coords: list
    properties: dict
    parameters: list[Parameter]


class Locations(Interface):
    def __init__(self, collection_id, query_parameters: dict) -> None:
        self.collection_id = collection_id
        self.query_parameters = query_parameters
        self.supported_query_params = ["bbox", "datetime"]

    def _bbox_filter(self, location: Location) -> bool:
        raise NotImplementedError

    def _datetime_filter(self, location: Location) -> bool:
        raise NotImplementedError

    def parameters(self) -> List[Parameter]:
        """Construct the list of all parameters that can be served."""
        raise NotImplementedError

    def all_locations(self) -> List[Location]:
        raise NotImplementedError

    def locations_filter(self, locations: List[Location]) -> List[Location]:
        raise NotImplementedError

    def data(self) -> List[Location]:
        return self.locations_filter(self.all_locations())