from dataclasses import dataclass
import datetime
from typing import List

from .core import Interface


@dataclass
class Parameter:
    """A cut-back description of an EDR parameter, specifically for populating `item.covjson`."""
    type: str
    dataType: str
    axes: list
    shape: list
    values: list


@dataclass
class Feature:
    """
    A cut-back description of an EDR location / feature,
    specifically for populating the features list in `items.json`.

    """
    id: str
    geometry_type: str
    coords: list
    properties: dict
    link_href: str


@dataclass
class FeatureCollection:
    links: list
    number_returned: int
    number_matched: int
    timestamp: str
    items: "list[Feature]"


class Items(Interface):
    def __init__(self, collection_id, query_parameters: dict, collection_href: str) -> None:
        self.collection_id = collection_id
        self.query_parameters = query_parameters
        self.collection_href = collection_href
        self.supported_query_params = ["bbox", "datetime"]

    def _bbox_filter(self, location: Feature) -> bool:
        raise NotImplementedError

    def _datetime_filter(self, location: Feature) -> bool:
        raise NotImplementedError

    def _get_features(self) -> List[Feature]:
        """
        Build the list of all features (locations, areas, cubes, ...) to be provided as
        the list of EDR Items to be served.

        """
        raise NotImplementedError

    def _get_timestamp(self):
        """Return the timestamp, in ISO format, of the items request."""
        timestamp = datetime.datetime.now()
        return datetime.datetime.strftime(timestamp, "%Y-%m-%dT%H:%M:%SZ")

    def data(self) -> FeatureCollection:
        raise NotImplementedError