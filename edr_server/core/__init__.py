from abc import ABC, abstractmethod
from typing import List, Optional

from edr_server.core.models import CollectionId, ItemId, CollectionMetadata, ItemMetadata


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
