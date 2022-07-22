from dataclasses import dataclass, field
from typing import List

from ._types_and_defaults import CollectionId, EdrDataQuery
from .crs import CrsObject
from .extents import Extents
from .links import DataQueryLink, Link, AreaDataQuery, CorridorDataQuery, CubeDataQuery, ItemsDataQuery, \
    LocationsDataQuery, PositionDataQuery, RadiusDataQuery, TrajectoryDataQuery
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
    extra_links: List[Link] = field(default_factory=list)
    # data_queries  # TODO make this explicit rather than generated to make deserialisation easier?
    height_units: List[str] = field(default_factory=list)
    width_units: List[str] = field(default_factory=list)
    within_units: List[str] = field(default_factory=list)

    def __post_init__(self):
        pass  # TODO can I handle extra arguments I want to ignore from deserilisation here?

    def __str__(self):
        return f"{self.id} metadata"

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"{self.id!r}, {self.title!r}, {self.description!r}, {self.keywords!r}, {self.extent!r}"
                f", {self.supported_data_queries!r}, {self.parameters!r}, {self.height_units!r}, {self.width_units!r}"
                f", {self.width_units!r}, {self.extra_links!r}"
                f")")

    @property
    def crs(self) -> CrsObject:
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
        dql_list = []
        for query_type in self.supported_data_queries:
            if query_type is EdrDataQuery.AREA:
                dql_list.append(
                    DataQueryLink(
                        href=url_resolver.COLLECTION_DATA_QUERY_MAP[query_type](self.id),
                        rel="data",
                        variables=AreaDataQuery(output_formats=self.output_formats, crs_details=[self.crs]),
                        type=query_type.name.lower(),
                        hreflang="en",
                        title=query_type.name.title(),
                    )
                )
            elif query_type is EdrDataQuery.CORRIDOR:
                dql_list.append(
                    DataQueryLink(
                        href=url_resolver.COLLECTION_DATA_QUERY_MAP[query_type](self.id),
                        rel="data",
                        variables=CorridorDataQuery(
                            output_formats=self.output_formats, crs_details=[self.crs], width_units=self.width_units,
                            height_units=self.height_units
                        ),
                        type=query_type.name.lower(),
                        hreflang="en",
                        title=query_type.name.title(),
                    )
                )
            elif query_type is EdrDataQuery.CUBE:
                dql_list.append(
                    DataQueryLink(
                        href=url_resolver.COLLECTION_DATA_QUERY_MAP[query_type](self.id),
                        rel="data",
                        variables=CubeDataQuery(
                            output_formats=self.output_formats, crs_details=[self.crs], height_units=self.height_units
                        ),
                        type=query_type.name.lower(),
                        hreflang="en",
                        title=query_type.name.title(),
                    )
                )
            elif query_type is EdrDataQuery.ITEMS:
                dql_list.append(
                    DataQueryLink(
                        href=url_resolver.COLLECTION_DATA_QUERY_MAP[query_type](self.id),
                        rel="data",
                        variables=ItemsDataQuery(),
                        type=query_type.name.lower(),
                        hreflang="en",
                        title=query_type.name.title(),
                    )
                )

            elif query_type is EdrDataQuery.LOCATIONS:
                dql_list.append(
                    DataQueryLink(
                        href=url_resolver.COLLECTION_DATA_QUERY_MAP[query_type](self.id),
                        rel="data",
                        variables=LocationsDataQuery(output_formats=self.output_formats, crs_details=[self.crs]),
                        type=query_type.name.lower(),
                        hreflang="en",
                        title=query_type.name.title(),
                    )
                )
            elif query_type is EdrDataQuery.POSITION:
                dql_list.append(
                    DataQueryLink(
                        href=url_resolver.COLLECTION_DATA_QUERY_MAP[query_type](self.id),
                        rel="data",
                        variables=PositionDataQuery(output_formats=self.output_formats, crs_details=[self.crs]),
                        type=query_type.name.lower(),
                        hreflang="en",
                        title=query_type.name.title(),
                    )
                )
            elif query_type is EdrDataQuery.RADIUS:
                dql_list.append(
                    DataQueryLink(
                        href=url_resolver.COLLECTION_DATA_QUERY_MAP[query_type](self.id),
                        rel="data",
                        variables=RadiusDataQuery(
                            output_formats=self.output_formats, crs_details=[self.crs], within_units=self.within_units
                        ),
                        type=query_type.name.lower(),
                        hreflang="en",
                        title=query_type.name.title(),
                    )
                )
            elif query_type is EdrDataQuery.TRAJECTORY:
                dql_list.append(
                    DataQueryLink(
                        href=url_resolver.COLLECTION_DATA_QUERY_MAP[query_type](self.id),
                        rel="data",
                        variables=TrajectoryDataQuery(output_formats=self.output_formats, crs_details=[self.crs]),
                        type=query_type.name.lower(),
                        hreflang="en",
                        title=query_type.name.title(),
                    )
                )

        return dql_list


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
