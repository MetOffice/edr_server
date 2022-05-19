from dataclasses import dataclass, field
from typing import List

import pyproj

from ._types_and_defaults import CollectionId, EdrDataQuery
from .extents import Extents
from .links import DataQueryLink, Link
from .parameters import Parameter
from .urls import EdrUrlResolver


@dataclass
class CollectionMetadata:
    """
    Based on
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/e8a78f9/standard/openapi/schemas/collection.yaml
    """
    id: CollectionId
    title: str
    description: str
    keywords: List[str]
    extent: Extents
    supported_data_queries: List[EdrDataQuery]
    output_formats: List[str]
    parameters: List[Parameter] = field(default_factory=list)
    height_units: List[str] = field(default_factory=list)
    width_units: List[str] = field(default_factory=list)
    within_units: List[str] = field(default_factory=list)
    extra_links: List[Link] = field(default_factory=list)

    @property
    def crs(self) -> pyproj.CRS:
        return self.extent.spatial.crs

    def get_links(self, url_resolver: EdrUrlResolver) -> List[Link]:
        collection_links = [
            Link(
                href=url_resolver.collection(self.id),
                rel="collection",
                type="application/json",
                hreflang="en",
                title="Collection",
            )
        ]
        collection_links.extend([
            Link(
                href=url_resolver.COLLECTION_DATA_QUERY_MAP[query](self.id),
                rel="data",
                type=query.name.lower(),
                hreflang="en",
                title=query.name.title()
            )
            for query in self.supported_data_queries
        ])
        collection_links.extend(self.extra_links)
        return collection_links

    def get_data_query_links(self, url_resolver: EdrUrlResolver) -> List[DataQueryLink]:
        return [
            DataQueryLink.get_data_query_link(
                query_type=query,
                collection_id=self.id,
                urls=url_resolver,
                output_formats=self.output_formats,
                height_units=self.height_units,
                width_units=self.width_units,
                within_units=self.within_units,
                crs_details=[self.crs]
            )
            for query in self.supported_data_queries
        ]


@dataclass
class CollectionMetadataList:
    collections: List[CollectionMetadata]
    extra_links: List[Link] = field(default_factory=list)

    def get_links(self, url_resolver: EdrUrlResolver) -> List[Link]:
        return [
                   Link(url_resolver.collections(), "self", "application/json"),
               ] + self.extra_links


@dataclass
class ItemMetadata:
    pass
