from dataclasses import dataclass, field
from typing import List

from .core import Interface


@dataclass
class Collection:
    name: str
    id: str
    description: str
    keywords: list
    bbox: list
    crs: str
    crs_name: str
    temporal_interval: list = field(default_factory=list)
    temporal_values: list = field(default_factory=list)
    trs: str = ""
    temporal_name: str = ""
    vertical_interval: list = field(default_factory=list)
    vertical_values: list = field(default_factory=list)
    vrs: str = ""
    vertical_name: str = ""

    def has_temporal_extent(self):
        has_extent = bool(len(self.temporal_interval))
        if has_extent and not len(self.trs):
            raise ValueError("At minimum the temporal interval and TRS must be specified.")
        return has_extent

    def has_vertical_extent(self):
        has_extent = bool(len(self.vertical_interval))
        if has_extent and not len(self.vrs):
            raise ValueError("At minimum the vertical interval and VRS must be specified.")
        return has_extent


@dataclass
class Parameter:
    name: str
    id: str
    description: str
    unit_label: str
    unit_value: str
    unit_defn: str
    property_id: str
    property_label: str


class RefreshCollections(Interface):
    def __init__(self, supported_data_queries) -> None:
        self.supported_data_queries = supported_data_queries

    def _get_temporal_extent(self, name):
        """
        Determine if the data for the collection described by `name` has a temporal extent.

        Must set `interval`, `trs` and `name` for the temporal extent JSON response.
        The `trs` variable must be provided as well-known text (WKT).

        """
        raise NotImplementedError

    def _get_vertical_extent(self, name):
        """
        Determine if the data for the collection described by `name` has a vertical extent.

        Must set `interval`, `vrs` and `name` for the vertical extent JSON response.
        The `vrs` variable must be provided as well-known text (WKT).

        """
        raise NotImplementedError

    def get_parameters(self, collection_id) -> List[Parameter]:
        """
        Return metadata for all the parameters (~physical quantities)
        associated with the collection specified by its ID `collection_id`.

        """
        raise NotImplementedError

    def make_collection(self, name) -> Collection:
        raise NotImplementedError

    def make_collections(self) -> List[Collection]:
        raise NotImplementedError

    def data(self):
        return self.make_collections()