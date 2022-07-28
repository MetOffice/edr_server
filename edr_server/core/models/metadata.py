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
        pass  # TODO can I handle extra arguments I want to ignore from deserialisation here?

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

    @staticmethod
    def get_standard_links(
            url_resolver: EdrUrlResolver, collection_id: CollectionId, supported_data_queries: List[EdrDataQuery]
    ) -> List[Link]:

        collection_links = [
            Link(
                href=url_resolver.collection(collection_id),
                rel="collection",
                type="application/json",
                hreflang="en",
                title="Collection",
            )
        ]
        collection_links.extend([
            Link(
                href=url_resolver.COLLECTION_DATA_QUERY_MAP[query](collection_id),
                rel="data",
                type=query.name.lower(),
                hreflang="en",
                title=query.name.title()
            )
            for query in supported_data_queries
        ])
        return collection_links

    @staticmethod
    def get_data_query_links(
            url_resolver: EdrUrlResolver, collection_id: CollectionId, supported_data_queries: List[EdrDataQuery],
            output_formats: List[str] = None, crs_details: List[CrsObject] = None, width_units: List[str] = None,
            height_units: List[str] = None, within_units: List[str] = None
    ) -> List[DataQueryLink]:
        dql_list = []
        for query_type in supported_data_queries:
            if query_type is EdrDataQuery.AREA:
                dql_list.append(
                    DataQueryLink(
                        href=url_resolver.COLLECTION_DATA_QUERY_MAP[query_type](collection_id),
                        rel="data",
                        variables=AreaDataQuery(output_formats=output_formats, crs_details=crs_details),
                        type=query_type.name.lower(),
                        hreflang="en",
                        title=query_type.name.title(),
                    )
                )
            elif query_type is EdrDataQuery.CORRIDOR:
                dql_list.append(
                    DataQueryLink(
                        href=url_resolver.COLLECTION_DATA_QUERY_MAP[query_type](collection_id),
                        rel="data",
                        variables=CorridorDataQuery(
                            output_formats=output_formats, crs_details=crs_details, width_units=width_units,
                            height_units=height_units
                        ),
                        type=query_type.name.lower(),
                        hreflang="en",
                        title=query_type.name.title(),
                    )
                )
            elif query_type is EdrDataQuery.CUBE:
                dql_list.append(
                    DataQueryLink(
                        href=url_resolver.COLLECTION_DATA_QUERY_MAP[query_type](collection_id),
                        rel="data",
                        variables=CubeDataQuery(
                            output_formats=output_formats, crs_details=crs_details, height_units=height_units
                        ),
                        type=query_type.name.lower(),
                        hreflang="en",
                        title=query_type.name.title(),
                    )
                )
            elif query_type is EdrDataQuery.ITEMS:
                dql_list.append(
                    DataQueryLink(
                        href=url_resolver.COLLECTION_DATA_QUERY_MAP[query_type](collection_id),
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
                        href=url_resolver.COLLECTION_DATA_QUERY_MAP[query_type](collection_id),
                        rel="data",
                        variables=LocationsDataQuery(output_formats=output_formats, crs_details=crs_details),
                        type=query_type.name.lower(),
                        hreflang="en",
                        title=query_type.name.title(),
                    )
                )
            elif query_type is EdrDataQuery.POSITION:
                dql_list.append(
                    DataQueryLink(
                        href=url_resolver.COLLECTION_DATA_QUERY_MAP[query_type](collection_id),
                        rel="data",
                        variables=PositionDataQuery(output_formats=output_formats, crs_details=crs_details),
                        type=query_type.name.lower(),
                        hreflang="en",
                        title=query_type.name.title(),
                    )
                )
            elif query_type is EdrDataQuery.RADIUS:
                dql_list.append(
                    DataQueryLink(
                        href=url_resolver.COLLECTION_DATA_QUERY_MAP[query_type](collection_id),
                        rel="data",
                        variables=RadiusDataQuery(
                            output_formats=output_formats, crs_details=crs_details, within_units=within_units
                        ),
                        type=query_type.name.lower(),
                        hreflang="en",
                        title=query_type.name.title(),
                    )
                )
            elif query_type is EdrDataQuery.TRAJECTORY:
                dql_list.append(
                    DataQueryLink(
                        href=url_resolver.COLLECTION_DATA_QUERY_MAP[query_type](collection_id),
                        rel="data",
                        variables=TrajectoryDataQuery(output_formats=output_formats, crs_details=crs_details),
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
