from dataclasses import dataclass
import datetime
from typing import List, Union

import numpy.ma as ma

from .core import Interface


@dataclass
class Parameter:
    """A cut-back description of an EDR parameter, specifically for populating `item.covjson`."""
    type: str
    dtype: str
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


class Item(Interface):
    def __init__(self, collection_id, item_id) -> None:
        self.collection_id = collection_id
        self.item_id = item_id
        self.param_name, *axes_inds = self.item_id.split("_")

        # Cast inds to int if possible but ignore errors to pick them up later.
        self.axes_inds = []
        for ind in axes_inds:
            try:
                self.axes_inds.append(int(ind))
            except ValueError:
                self.axes_inds.append(ind)

    def _has_item(self) -> bool:
        """Determine whether the server can provide the requested item."""
        raise NotImplementedError

    def _can_provide_data(self, parameter: Parameter) -> bool:
        """Confirm the requested parameter provides TileSet data and that the requested indices are valid."""
        raise NotImplementedError

    def _prepare_data(self, data) -> List:
        """
        Prepare the data for being templated into a coverageJSON file:
          * reshape the data to a flat list
          * replace any missing / masked data with None, which will be converted
            to JSON `null` in the template.

        """
        if ma.isMaskedArray(data):
            flat_data = [d if d != data.fill_value else None for d in data.filled().reshape(-1)]
        else:
            flat_data = list(data.reshape(-1))
        return flat_data

    def data(self) -> Union[Parameter, None]:
        raise NotImplementedError