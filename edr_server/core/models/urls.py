from dataclasses import dataclass
from typing import Dict, Callable

from ._types_and_defaults import EdrDataQuery


class URL(str):
    """
    A string like class that validates a string is URL-like before returning an actual string
    Taken from this SO answer: https://stackoverflow.com/a/54611993/110255
    """

    def __new__(cls, *value):
        if value:
            v0 = value[0]
            if not type(v0) is str:
                raise TypeError('Unexpected type for URL: "%s"' % type(v0))
            # noinspection HttpUrlsUsage
            if not (v0.startswith('http://') or v0.startswith('https://')):
                raise ValueError('Passed string value "%s" is not an'
                                 ' "http*://" URL' % (v0,))
        # else allow None to be passed. This allows an "empty" URL instance, e.g. `URL()`

        return str.__new__(cls, *value)


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
        self.COLLECTION_DATA_QUERY_MAP: Dict[EdrDataQuery, Callable[[str], URL]] = {
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

    def root(self) -> URL:
        """/"""
        return URL(f"{self.api_base}/")

    def conformance(self) -> URL:
        """/conformance"""
        return URL(f"{self.api_base}/conformance")

    def groups(self) -> URL:
        """/groups"""
        return URL(f"{self.api_base}/groups")

    def group(self, group_id: str) -> URL:
        """/groups/{groupId}"""
        return URL(f"{self.api_base}/groups/{group_id}")

    def collections(self) -> URL:
        """/collections"""
        return URL(f"{self.api_base}/collections")

    def collection(self, collection_id: str) -> URL:
        """/collections/{collectionId}"""
        return URL(f"{self.api_base}/collections/{collection_id}")

    def items(self, collection_id: str) -> URL:
        """/collections/{collectionId}/items"""
        return URL(f"{self.api_base}/collections/{collection_id}/items")

    def item(self, collection_id: str, item_id: str) -> URL:
        """/collections/{collectionId}/items/{itemId}"""
        return URL(f"{self.api_base}/collections/{collection_id}/items/{item_id}")

    def locations(self, collection_id: str) -> URL:
        """/collections/{collectionId}/locations"""
        return URL(f"{self.api_base}/collections/{collection_id}/locations")

    def location(self, collection_id: str, location_id: str) -> URL:
        """/collections/{collectionId}/locations/{locId}"""
        return URL(f"{self.api_base}/collections/{collection_id}/locations/{location_id}")

    def position(self, collection_id: str) -> URL:
        """/collections/{collectionId}/position"""
        return URL(f"{self.api_base}/collections/{collection_id}/position")

    def radius(self, collection_id: str) -> URL:
        """/collections/{collectionId}/radius"""
        return URL(f"{self.api_base}/collections/{collection_id}/radius")

    def area(self, collection_id: str) -> URL:
        """/collections/{collectionId}/area"""
        return URL(f"{self.api_base}/collections/{collection_id}/area")

    def cube(self, collection_id: str) -> URL:
        """/collections/{collectionId}/cube"""
        return URL(f"{self.api_base}/collections/{collection_id}/cube")

    def trajectory(self, collection_id: str) -> str:
        """/collections/{collectionId}/trajectory"""
        return URL(f"{self.api_base}/collections/{collection_id}/trajectory")

    def corridor(self, collection_id: str) -> URL:
        """/collections/{collectionId}/corridor"""
        return URL(f"{self.api_base}/collections/{collection_id}/corridor")

    def instances(self, collection_id: str) -> URL:
        """/collections/{collectionId}/instances"""
        return URL(f"{self.api_base}/collections/{collection_id}/instances")

    def instance_position(self, collection_id: str, instance_id: str) -> URL:
        """/collections/{collectionId}/instances/{instanceId}/position"""
        return URL(f"{self.api_base}/collections/{collection_id}/instances/{instance_id}/position")

    def instance_radius(self, collection_id: str, instance_id: str) -> URL:
        """/collections/{collectionId}/instances/{instanceId}/radius"""
        return URL(f"{self.api_base}/collections/{collection_id}/instances/{instance_id}/radius")

    def instance_area(self, collection_id: str, instance_id: str) -> URL:
        """/collections/{collectionId}/instances/{instanceId}/area"""
        return URL(f"{self.api_base}/collections/{collection_id}/instances/{instance_id}/area")

    def instance_cube(self, collection_id: str, instance_id: str) -> URL:
        """/collections/{collectionId}/instances/{instanceId}/cube"""
        return URL(f"{self.api_base}/collections/{collection_id}/instances/{instance_id}/cube")

    def instance_trajectory(self, collection_id: str, instance_id: str) -> URL:
        """/collections/{collectionId}/instances/{instanceId}/trajectory"""
        return URL(f"{self.api_base}/collections/{collection_id}/instances/{instance_id}/trajectory")

    def instance_corridor(self, collection_id: str, instance_id: str) -> URL:
        """/collections/{collectionId}/instances/{instanceId}/corridor"""
        return URL(f"{self.api_base}/collections/{collection_id}/instances/{instance_id}/corridor")

    def instance_locations(self, collection_id: str, instance_id: str) -> URL:
        """/collections/{collectionId}/instances/{instanceId}/locations"""
        return URL(f"{self.api_base}/collections/{collection_id}/instances/{instance_id}/locations")
