from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Any

import pyproj
from shapely.geometry import box
from shapely.geometry.base import BaseGeometry

CollectionId = str
ItemId = str


class EdrDataQuery(Enum):
    CUBE = "cube"
    CORRIDOR = "corridor"
    LOCATIONS = "locations"
    ITEMS = "items"
    AREA = "area"
    POSITION = "position"
    RADIUS = "radius"
    TRAJECTORY = "trajectory"


@dataclass
class Extent:
    spatial: BaseGeometry = box(1, 2, 3, 4)
    temporal: Any = None
    vertical: Any = None


@dataclass
class CollectionMetadata:
    id: str
    title: str
    description: str
    keywords: List[str]
    crs: pyproj.CRS
    bbox: BaseGeometry
    parameters: List
    supported_data_queries: List[EdrDataQuery]
    output_formats: List[str]
    extent: Extent = Extent()


@dataclass
class ItemMetadata:
    pass


class AbstractCollectionsMetadataDataInterface(ABC):

    @abstractmethod
    def all(self) -> List[CollectionMetadata]:
        pass

    @abstractmethod
    def get(self, collection_id: CollectionId) -> CollectionMetadata:
        pass


class AbstractItemsDataInterface(ABC):
    @abstractmethod
    def all_metadata(self, collection_id: CollectionId) -> List[ItemMetadata]:
        pass

    @abstractmethod
    def get_metadata(self, collection_id: CollectionId, item_id: ItemId) -> ItemMetadata:
        pass


class EdrDataInterface:

    def __init__(
            self,
            collections: AbstractCollectionsMetadataDataInterface,
            items: Optional[AbstractItemsDataInterface] = None,
    ):
        self.collections = collections
        self.items = items
