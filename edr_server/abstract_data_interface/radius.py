from typing import Union

from .area import Area


class Radius(Area):
    def __init__(self, collection_id, query_parameters: dict, items_url: str) -> None:
        super().__init__(collection_id, query_parameters, items_url)
        self.supported_query_params = ["coords", "within", "within_units", "z", "datetime", "crs"]

    def _check_query_args(self) -> Union[str, None]:
        """
        Check required query arguments for a Radius query are present in the
        query string, and produce a descriptive error message if not.

        """
        error = None
        missing_args = []
        for required_arg in ["coords", "within", "within_units"]:
            arg = self.query_parameters.get(required_arg)
            if arg is None:
                missing_args.append(required_arg)
        if len(missing_args):
            missing_args_str = f"[{', '.join(missing_args)}]"
            proper_grammar = "argument" if len(missing_args) == 1 else "arguments"
            error = f"Required Radius query {proper_grammar} {missing_args_str} not present in query string."
        return error

    def _handle_units(self):
        crs = self.query_parameters.get("crs")
        radius = float(self.query_parameters.get("within"))
        within_units = self.query_parameters.get("within_units").lower()
        if within_units == "km":
            radius *= 1000
        if crs != "WGS84" and within_units not in ["m", "km"]:
            raise ValueError("Cannot accurately determine radius.")
        return radius

    def generate_polygon(self):
        """Generate the circle polygon to locate items within."""
        radius = self._handle_units()
        point = self.query_parameters.get("coords")
        self.polygon = point.buffer(radius)
