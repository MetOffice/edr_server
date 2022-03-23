from copy import copy
from typing import List, Tuple, Union

from .core import Interface
from .filter import Filter
from .locations import Feature


class Area(Interface):
    def __init__(self, collection_id, query_parameters: dict, items_url: str) -> None:
        self.collection_id = collection_id
        self.query_parameters = query_parameters
        self.supported_query_params = ["coords", "z", "datetime", "crs"]
        self.items_url = items_url

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
            values = result.axis_t_values
            if len(values):
                filterer = Filter(values, extents)
                filtered_values = filterer.filter()
                if filtered_values is not None:
                    result.axis_t_values = {"values": filtered_values}
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
            z_values = result.axis_z_values
            if len(z_values):
                filterer = Filter(z_values, z_extents)
                filtered_z_values = filterer.filter()
                if filtered_z_values is not None:
                    result.axis_z_values = {"values": filtered_z_values}
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
            if not len(result):
                result = None
        else:
            result = None
        return result

    def features_to_domain(self, features: List[Feature]) -> Feature:
        """
        Filtering all the features in the collection will return a list
        of features of at least length 1, but we need a single Feature to
        populate `domain.json`. To do this we concatenate the lists of parameters
        from all features and return a single new `Feature` with
        these concatenated elements.

        """
        if len(features) == 1:
            result = features[0]
        else:
            all_params = []
            for feature in features:
                all_params.extend(feature.parameters)
            all_unique_params = list(set(all_params))
            result = copy.copy(features[0])
            result.parameters = all_unique_params
        return result

    def data(self) -> Tuple[Union[Feature, None], Union[str, None]]:
        error = self._check_query_args()
        if error is None:
            filtered_features = self.filter(self.all_items())
            result = self.features_to_domain(filtered_features)
        else:
            result = None
        return result, error