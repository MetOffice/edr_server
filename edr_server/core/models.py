import dataclasses
import warnings
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional, Tuple, Dict, Callable

import pyproj
import shapely.geometry

from edr_server.core.time import DateTimeInterval

DEFAULT_CRS = pyproj.CRS("WGS84")


@dataclass
class EdrUrlResolver:
    """
    This class abstracts the resolution of EDR URLs for use in serialisation.
    It's intended to be instantiated by a server implementation (e.g. edr_server.impl.tornado) which will provide it
    with the `api_base` required to generate absolute URLs.

    It doesn't support relative URLs, since it's fiddly to have to know the URL of the desired page relative to the
    current page. Although it could be achieved it doesn't add much value beyond what absolute URLs already give.

    The available URLs are based on https://developer.ogc.org/api/edr/edr_api.html and this class is only intended to
    resolve URLs that are part of the EDR specification.

    It could be extended to add additional implementation specific functionality.
    """
    api_base: str

    def __post_init__(self):
        # https://docs.python.org/3/library/dataclasses.html#post-init-processing
        self.api_base = self.api_base.strip().rstrip("/")

        # These dictionaries map data query enums to the functions that can be used to generate the proper URLs
        self.COLLECTION_DATA_QUERY_MAP: Dict[EdrDataQuery, Callable[[str], str]] = {
            EdrDataQuery.CUBE: self.cube,
            EdrDataQuery.CORRIDOR: self.corridor,
            EdrDataQuery.LOCATIONS: self.locations,
            EdrDataQuery.ITEMS: self.items,
            EdrDataQuery.AREA: self.area,
            EdrDataQuery.POSITION: self.position,
            EdrDataQuery.RADIUS: self.radius,
            EdrDataQuery.TRAJECTORY: self.trajectory,
        }

        self.INSTANCE_DATA_QUERY_MAP: Dict[EdrDataQuery, Callable[[str, str], str]] = {
            EdrDataQuery.CUBE: self.instance_cube,
            EdrDataQuery.CORRIDOR: self.instance_corridor,
            EdrDataQuery.LOCATIONS: self.instance_locations,
            # There's not EdrDataQuery.ITEMS equivalent for instances
            EdrDataQuery.AREA: self.instance_area,
            EdrDataQuery.POSITION: self.instance_position,
            EdrDataQuery.RADIUS: self.instance_radius,
            EdrDataQuery.TRAJECTORY: self.instance_trajectory,
        }

    def root(self) -> str:
        """/"""
        return f"{self.api_base}/"

    def conformance(self) -> str:
        """/conformance"""
        return f"{self.api_base}/conformance"

    def groups(self) -> str:
        """/groups"""
        return f"{self.api_base}/groups"

    def group(self, group_id: str) -> str:
        """/groups/{groupId}"""
        return f"{self.api_base}/groups/{group_id}"

    def collections(self) -> str:
        """/collections"""
        return f"{self.api_base}/collections"

    def collection(self, collection_id: str) -> str:
        """/collections/{collectionId}"""
        return f"{self.api_base}/collections/{collection_id}"

    def items(self, collection_id: str) -> str:
        """/collections/{collectionId}/items"""
        return f"{self.api_base}/collections/{collection_id}/items"

    def item(self, collection_id: str, item_id: str) -> str:
        """/collections/{collectionId}/items/{itemId}"""
        return f"{self.api_base}/collections/{collection_id}/items/{item_id}"

    def locations(self, collection_id: str) -> str:
        """/collections/{collectionId}/locations"""
        return f"{self.api_base}/collections/{collection_id}/locations"

    def location(self, collection_id: str, location_id: str) -> str:
        """/collections/{collectionId}/locations/{locId}"""
        return f"{self.api_base}/collections/{collection_id}/locations/{location_id}"

    def position(self, collection_id: str) -> str:
        """/collections/{collectionId}/position"""
        return f"{self.api_base}/collections/{collection_id}/position"

    def radius(self, collection_id: str) -> str:
        """/collections/{collectionId}/radius"""
        return f"{self.api_base}/collections/{collection_id}/radius"

    def area(self, collection_id: str) -> str:
        """/collections/{collectionId}/area"""
        return f"{self.api_base}/collections/{collection_id}/area"

    def cube(self, collection_id: str) -> str:
        """/collections/{collectionId}/cube"""
        return f"{self.api_base}/collections/{collection_id}/cube"

    def trajectory(self, collection_id: str) -> str:
        """/collections/{collectionId}/trajectory"""
        return f"{self.api_base}/collections/{collection_id}/trajectory"

    def corridor(self, collection_id: str) -> str:
        """/collections/{collectionId}/corridor"""
        return f"{self.api_base}/collections/{collection_id}/corridor"

    def instances(self, collection_id: str) -> str:
        """/collections/{collectionId}/instances"""
        return f"{self.api_base}/collections/{collection_id}/instances"

    def instance_position(self, collection_id: str, instance_id: str) -> str:
        """/collections/{collectionId}/instances/{instanceId}/position"""
        return f"{self.api_base}/collections/{collection_id}/instances/{instance_id}/position"

    def instance_radius(self, collection_id: str, instance_id: str) -> str:
        """/collections/{collectionId}/instances/{instanceId}/radius"""
        return f"{self.api_base}/collections/{collection_id}/instances/{instance_id}/radius"

    def instance_area(self, collection_id: str, instance_id: str) -> str:
        """/collections/{collectionId}/instances/{instanceId}/area"""
        return f"{self.api_base}/collections/{collection_id}/instances/{instance_id}/area"

    def instance_cube(self, collection_id: str, instance_id: str) -> str:
        """/collections/{collectionId}/instances/{instanceId}/cube"""
        return f"{self.api_base}/collections/{collection_id}/instances/{instance_id}/cube"

    def instance_trajectory(self, collection_id: str, instance_id: str) -> str:
        """/collections/{collectionId}/instances/{instanceId}/trajectory"""
        return f"{self.api_base}/collections/{collection_id}/instances/{instance_id}/trajectory"

    def instance_corridor(self, collection_id: str, instance_id: str) -> str:
        """/collections/{collectionId}/instances/{instanceId}/corridor"""
        return f"{self.api_base}/collections/{collection_id}/instances/{instance_id}/corridor"

    def instance_locations(self, collection_id: str, instance_id: str) -> str:
        """/collections/{collectionId}/instances/{instanceId}/locations"""
        return f"{self.api_base}/collections/{collection_id}/instances/{instance_id}/locations"


class EdrDataQuery(Enum):
    CUBE = "cube"
    CORRIDOR = "corridor"
    LOCATIONS = "locations"
    ITEMS = "items"
    AREA = "area"
    POSITION = "position"
    RADIUS = "radius"
    TRAJECTORY = "trajectory"

    def get_data_query_link(
            self,
            href: str,
            output_formats: List[str],
            height_units: List[str] = None,
            width_units: List[str] = None,
            within_units: List[str] = None,
            crs_details: List[pyproj.CRS] = None
    ) -> "DataQueryLink":
        if crs_details is None:
            crs_details = [DEFAULT_CRS]

        return DataQueryLink(
            href=href,
            rel="data",
            variables=self.get_data_query(output_formats, height_units, width_units, within_units, crs_details),
            type=self.name.lower(),
            hreflang="en",
            title=self.name.title(),
        )

    def get_data_query(
            self,
            output_formats: List[str],
            height_units: List[str] = None,
            width_units: List[str] = None,
            within_units: List[str] = None,
            crs_details: List[pyproj.CRS] = None
    ) -> "DataQuery":

        kwargs = {
            "title": f"{self.name.title()} Query",
            "query_type": self,
            "output_formats": output_formats,
            "default_output_format": output_formats[0],
            "crs_details": crs_details if crs_details else [DEFAULT_CRS]
        }

        if self is EdrDataQuery.AREA:
            kwargs["description"] = "Query to return data for a defined area"
            if height_units:
                kwargs["height_units"] = height_units

        elif self is EdrDataQuery.CORRIDOR:
            kwargs["description"] = ("Query to return data for a corridor of specified height and width along a "
                                     "trajectory defined using WKT")
            if height_units:
                kwargs["height_units"] = height_units
            if width_units:
                kwargs["width_units"] = width_units

        elif self is EdrDataQuery.CUBE:
            kwargs["description"] = "Query to return data for a cuboid defined by a bounding box and height"
            if height_units:
                kwargs["height_units"] = height_units

        elif self is EdrDataQuery.ITEMS:
            kwargs["description"] = "Query to return data for specific item"

        elif self is EdrDataQuery.LOCATIONS:
            kwargs["description"] = "Query to return data for a specific location"

        elif self is EdrDataQuery.POSITION:
            kwargs["description"] = "Query to return data for a defined well known text point"

        elif self is EdrDataQuery.RADIUS:
            kwargs["description"] = (
                "Query to return data for a circle defined by a well known text point and radius around it")
            if within_units:
                kwargs["within_units"] = within_units

        elif self is EdrDataQuery.TRAJECTORY:
            kwargs["description"] = "Query to return data for a defined well known text trajectory"

        return DataQuery(**kwargs)


@dataclass
class TemporalReferenceSystem:
    """
    I haven't found a library like pyproj that supports temporal reference systems, but would rather use one if it
    existed.

    EDR's core specification only supports Gregorian, however, so this will do for now. If implementors need something
     other than Gregorian, they can override the defaults.

    Based on a portion of
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/extent.yaml
    """
    name: str = "Gregorian"
    wkt: str = 'TIMECRS["DateTime",TDATUM["Gregorian Calendar"],CS[TemporalDateTime,1],AXIS["Time (T)",future]'


@dataclass
class TemporalExtent:
    """
    The specific times and time ranges covered by a dataset
    A temporal extent can be made up of one or more DateTimeIntervals, one or more specific datetimes, or a
    combination of both

    Based on a portion of
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/extent.yaml
    """
    values: List[datetime] = dataclasses.field(default_factory=list)
    intervals: List[DateTimeInterval] = dataclasses.field(default_factory=list)
    trs: TemporalReferenceSystem = TemporalReferenceSystem()

    @property
    def interval(self) -> Tuple[Optional[datetime], Optional[datetime]]:
        warnings.warn("Renamed to 'bounds' to avoid confusion with a list of DateTimeIntervals", DeprecationWarning)
        return self.bounds

    @property
    def bounds(self) -> Tuple[Optional[datetime], Optional[datetime]]:
        """
        Returns the earliest and latest datetimes covered by the extent.

        None indicates an open-ended interval, such as where a duration repeats indefinitely. The lower bound, upper
        bound, or both lower & and upper bounds can be open, depending on the extent being represented.
        """
        open_lower_bound = False
        open_upper_bound = False

        vals = self.values.copy()
        for dti in self.intervals:
            if dti.lower_bound:
                vals.append(dti.lower_bound)
            else:
                open_lower_bound = True

            if dti.upper_bound:
                vals.append(dti.upper_bound)
            else:
                open_upper_bound = True

        if vals:
            return min(vals) if not open_lower_bound else None, max(vals) if not open_upper_bound else None
        else:
            return None, None


@dataclass
class SpatialExtent:
    """
    Based on a portion of
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/extent.yaml
    """
    bbox: shapely.geometry.Polygon
    crs: pyproj.CRS = DEFAULT_CRS

    @property
    def bounds(self):
        return self.bbox.bounds


@dataclass
class Extent:
    """
    A struct-like container for the geographic area and time range(s) covered by a dataset
    Based on
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/extent.yaml
    """
    spatial: SpatialExtent
    temporal: TemporalExtent
    vertical: None


CollectionId = str
ItemId = str


@dataclass
class Link:
    """
    A simple link that can be used in the "links" section of an EDR response
    Based on
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/link.yaml
    """
    href: str
    rel: str
    type: Optional[str] = None
    hreflang: Optional[str] = None
    title: Optional[str] = None
    length: Optional[int] = None


@dataclass
class DataQuery:
    """
    Based on
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/areaDataQuery.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/corridorDataQuery.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/cubeDataQuery.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/itemsDataQuery.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/locationsDataQuery.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/positionDataQuery.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/radiusDataQuery.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/trajectoryDataQuery.yaml
    """
    title: Optional[str] = None
    description: Optional[str] = None
    query_type: Optional[EdrDataQuery] = None
    within_units: Optional[List[str]] = None
    width_units: Optional[List[str]] = None
    height_units: Optional[List[str]] = None
    output_formats: Optional[List[str]] = None
    default_output_format: Optional[str] = None
    crs_details: Optional[List[pyproj.CRS]] = None


@dataclass
class DataQueryLink:
    """
    Extended version of a simple link for use in the data_queries section of a collection metadata response
    Based on
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/link.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/areaLink.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/corridorLink.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/cubeLink.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/itemsLink.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/locationsLink.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/positionLink.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/radiusLink.yaml
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/trajectoryLink.yaml

    """
    # Didn't use inheritance here due to the way dataclasses interacts with the mixture of default and non-default
    # values in the fields. TLDR: it leads to a "Non-default argument(s) follows default argument(s) defined in 'Link'"
    # error. Further detail here:
    # https://stackoverflow.com/questions/51575931/class-inheritance-in-python-3-7-dataclasses
    # Duplication was the easiest workaround
    href: str
    rel: str
    variables: DataQuery
    type: Optional[str] = None
    hreflang: Optional[str] = None
    title: Optional[str] = None
    length: Optional[int] = None

    @property
    def templated(self):
        """All EDR's data query links are templated"""
        return True


@dataclass
class CollectionMetadata:
    """
    Based on
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/master/standard/openapi/schemas/collection.yaml
    """
    id: str
    title: str
    description: str
    keywords: List[str]
    extent: Extent
    parameters: List
    supported_data_queries: List[EdrDataQuery]
    output_formats: List[str]
    height_units: List[str] = dataclasses.field(default_factory=list)
    width_units: List[str] = dataclasses.field(default_factory=list)
    within_units: List[str] = dataclasses.field(default_factory=list)
    extra_links: List[Link] = dataclasses.field(default_factory=list)

    @property
    def crs(self) -> pyproj.CRS:
        return self.extent.spatial.crs

    def get_links(self, urls: EdrUrlResolver) -> List[Link]:
        links = [
            Link(
                href=urls.collection(self.id),
                rel="collection",
                type="application/json",
                hreflang="en",
                title="Collection",
            )
        ]
        links.extend([
            Link(
                href=urls.COLLECTION_DATA_QUERY_MAP[query](self.id),
                rel="data",
                type=query.name.lower(),
                hreflang="en",
                title=query.name.title(),
            )
            for query in self.supported_data_queries
        ])
        links.extend(self.extra_links)
        return links

    def get_data_query_links(self, urls: EdrUrlResolver) -> List[DataQueryLink]:
        return [
            query.get_data_query_link(
                href=urls.COLLECTION_DATA_QUERY_MAP[query](self.id),
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
    extra_links: List[Link] = dataclasses.field(default_factory=list)

    def get_links(self, urls: EdrUrlResolver) -> List[Link]:
        return [
                   Link(urls.collections(), "self", "application/json"),
               ] + self.extra_links


@dataclass
class ItemMetadata:
    pass
