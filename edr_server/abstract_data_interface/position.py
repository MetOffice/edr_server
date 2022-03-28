from .area import Area


class Position(Area):
    def __init__(self, collection_id, query_parameters: dict, items_url: str) -> None:
        super().__init__(collection_id, query_parameters, items_url)
        self.supported_query_params = ["coords", "z", "datetime", "crs"]
