from typing import Tuple, Union
from .area import Area


class Position(Area):
    def __init__(self, collection_id, query_parameters: dict, items_url: str) -> None:
        super().__init__(collection_id, query_parameters, items_url)
        self.supported_query_params = ["coords", "z", "datetime", "crs"]

    def _check_query_args(self) -> Tuple[Union[str, None], Union[int, None]]:
        """
        Check required query arguments for an Area query are present in the
        query string, and produce a descriptive error message if not.

        """
        error = None
        error_code = None
        coords = self.query_parameters.get("coords")
        if coords.geom_type.lower() not in ["point", "multipoint"]:
            error = f"Supplied geometry must be one of Point, MultiPoint; got {coords.geom_type!r}."
            error_code = 400
        return error, error_code
