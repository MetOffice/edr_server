from dataclasses import dataclass
from typing import List

from .core import Interface


@dataclass
class Location:
    id: str
    geometry_type: str
    coords: list
    properties: dict


class Locations(Interface):
    def __init__(self, collection_id, query_parameters: dict) -> None:
        self.collection_id = collection_id
        self.query_parameters = query_parameters
        self.supported_query_params = ["bbox", "datetime"]

    def _bbox_filter(self, location: Location) -> bool:
        raise NotImplementedError

    def _datetime_filter(self, location: Location) -> bool:
        raise NotImplementedError

    def all_locations(self) -> List[Location]:
        raise NotImplementedError

    def locations_filter(self, locations: List[Location]) -> List[Location]:
        raise NotImplementedError

    def data(self) -> List[Location]:
        return self.locations_filter(self.all_locations())