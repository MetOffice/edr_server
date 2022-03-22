from typing import List, Tuple, Union

from .core import Interface
from .filter import Filter
from .locations import Feature


class Area(Interface):
    def __init__(self, collection_id, query_parameters: dict) -> None:
        self.collection_id = collection_id
        self.query_parameters = query_parameters
        self.supported_query_params = ["coords", "z", "datetime", "crs"]

        self._polygon = None

    @property
    def polygon(self):
        if self._polygon is None:
            self.generate_polygon()
        return self._polygon

    @polygon.setter
    def polygon(self, value):
        self._polygon = value

    def generate_polygon(self):
        """Generate the area polygon to locate items within."""
        self.polygon = self.query_parameters["coords"]

    def _check_query_args(self) -> Union[str, None]:
        """
        Check required query arguments for an Area query are present in the
        query string, and produce a descriptive error message if not.

        """
        error = None
        coords = self.query_parameters.get("coords")
        if coords is None:
            error = "Required Area query argument 'coords' not present in query string."
        return error

    def _datetime_filter(self, feature: Feature) -> Union[Feature, None]:
        """
        Filter the datetime values returned in the feature based on limits provided in the
        query arguments, if any.

        """
        result = feature
        if "datetime" in self.query_parameters.keys():
            extents = self.query_parameters["datetime"]
            values = feature.axis_t_values
            if len(values):
                filterer = Filter(values, extents)
                filtered_values = filterer.filter()
                if filtered_values is not None:
                    feature.axis_t_values = {"values": filtered_values}
                    result = feature
                else:
                    result = None
        return result

    def _z_filter(self, feature: Feature) -> Union[Feature, None]:
        """
        Filter the vertical `z` values returned in the feature based on limits provided in the
        query arguments, if any.

        """
        result = feature
        if "z" in self.query_parameters.keys():
            z_extents = self.query_parameters["z"]
            z_values = feature.axis_z_values
            if len(z_values):
                filterer = Filter(z_values, z_extents)
                filtered_z_values = filterer.filter()
                if filtered_z_values is not None:
                    feature.axis_z_values = {"values": filtered_z_values}
                    result = feature
                else:
                    result = None
        return result

    def polygon_filter(self, items: List[Feature]) -> List[Feature]:
        """
        Filter the features returned based on the polygon specified in the query.
        The specific implementation of the filtering is to be provided by the
        data interface, which can set the filtering appropriate to the
        requirements of the data.

        """
        raise NotImplementedError

    def all_items(self) -> List[Feature]:
        raise NotImplementedError

    def filter(self, items: List[Feature]) -> Union[List[Feature], None]:
        within_polygon = self.polygon_filter(items)
        if len(within_polygon):
            result = []
            for item in within_polygon:
                item = self._z_filter(item)
                if item is not None:
                    item = self._datetime_filter(item)
                    if item is not None:
                        result.append(item)
        else:
            result = None
        return result

    def data(self) -> Tuple[Union[List[Feature], None], Union[str, None]]:
        error = self._check_query_args()
        result = self.filter(self.all_items()) if error is None else None
        return result, error