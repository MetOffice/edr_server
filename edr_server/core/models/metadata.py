from dataclasses import dataclass, field
from typing import List, Dict, Any, Set

from . import EdrModel, JsonDict
from ._types_and_defaults import CollectionId, EdrDataQuery
from .crs import CrsObject
from .extents import Extents
from .links import DataQueryLink, Link, AreaDataQuery, CorridorDataQuery, CubeDataQuery, ItemsDataQuery, \
    LocationsDataQuery, PositionDataQuery, RadiusDataQuery, TrajectoryDataQuery
from .parameters import Parameter
from .urls import EdrUrlResolver


@dataclass
class CollectionMetadata(EdrModel):
    """
    Based on
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/e8a78f9/standard/openapi/schemas/collection.yaml
    """

    id: CollectionId
    title: str
    description: str
    keywords: List[str]
    extent: Extents
    output_formats: List[str]
    parameters: List[Parameter] = field(default_factory=list)
    links: List[Link] = field(default_factory=list)
    data_queries: List[DataQueryLink] = field(default_factory=list)

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

    @classmethod
    def _get_allowed_json_keys(cls) -> Set[str]:
        return {
            "links", "id", "title", "description", "keywords", "extent", "data_queries", "crs_details",
            "output_formats", "parameter_names",
        }

    @classmethod
    def _prepare_json_for_init(cls, json_dict: JsonDict) -> JsonDict:
        if "links" in json_dict:
            json_dict["links"] = [Link.from_json(encoded_link) for encoded_link in json_dict["links"]]
        if "extent" in json_dict:
            json_dict["extent"] = Extents.from_json(json_dict["extent"])

        if "data_queries" in json_dict:
            json_dict["data_queries"] = [DataQueryLink.from_json(dl["link"]) for dl in json_dict["data_queries"]]

        if "crs_details" in json_dict:
            # This could be a source of bugs if working with JSON from other sources, but for everything we
            # serialise, we get this value from collection.extents.spatial
            del json_dict["crs_details"]

        if "parameter_names" in json_dict:
            params = json_dict.pop('parameter_names').values()
            json_dict["parameters"] = [Parameter.from_json(p) for p in params]

        return json_dict

    def __str__(self):
        return f"{self.id} metadata"

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"{self.id!r}, {self.title!r}, {self.description!r}, {self.keywords!r}, {self.extent!r}"
                f", {self.supported_data_queries!r}, {self.parameters!r}, {self.links!r}, {self.data_queries!r}"
                f")")

    @property
    def crs(self) -> CrsObject:
        return self.extent.spatial.crs

    @property
    def supported_data_queries(self) -> List[EdrDataQuery]:
        return [dql.variables.get_query_type() for dql in self.data_queries if dql.variables]

    def to_json(self) -> Dict[str, Any]:
        return {
            "links": [link.to_json() for link in self.links],
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "keywords": self.keywords,
            "extent": self.extent.to_json(),
            "data_queries": {dl.type: {"link": dl.to_json()} for dl in self.data_queries},
            "crs_details": [str(self.extent.spatial.crs)],
            "output_formats": self.output_formats,
            "parameter_names": {param.id: param.to_json() for param in self.parameters},
        }


@dataclass
class CollectionMetadataList:
    collections: List[CollectionMetadata]
    extra_links: List[Link] = field(default_factory=list)  # TODO change this

    def get_links(self, url_resolver: EdrUrlResolver) -> List[Link]:
        return [Link(url_resolver.collections(), "self", "application/json")] + self.extra_links


@dataclass
class ItemMetadata:
    pass
