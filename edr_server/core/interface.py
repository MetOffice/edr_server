from abc import ABC, abstractmethod
from typing import List, Optional

from .models import CollectionId, ItemId
from .models.metadata import CollectionMetadata, CollectionMetadataList, ItemMetadata
from .models.urls import EdrUrlResolver


class EdrRequest:
    """Encapsulates request specific information that may be required/useful to data interface implementations"""

    def __init__(self, url_resolver: EdrUrlResolver):
        self.url_resolver = url_resolver


class AbstractCollectionsMetadataDataInterface(ABC):

    @abstractmethod
    def all(self, request: EdrRequest) -> CollectionMetadataList:
        pass

    @abstractmethod
    def get(self,  request: EdrRequest, collection_id: CollectionId) -> CollectionMetadata:
        """Get a collection by ID
        :raises: CollectionNotFoundException if a collection with the given ID doesn't exist
        """


class AbstractItemsDataInterface(ABC):
    @abstractmethod
    def all_metadata(self, request: EdrRequest, collection_id: CollectionId) -> List[ItemMetadata]:
        pass

    @abstractmethod
    def get_metadata(self, request: EdrRequest, collection_id: CollectionId, item_id: ItemId) -> ItemMetadata:
        pass


class EdrDataInterface:

    def __init__(
            self,
            collections: AbstractCollectionsMetadataDataInterface,
            items: Optional[AbstractItemsDataInterface] = None,
    ):
        self.collections = collections
        self.items = items
