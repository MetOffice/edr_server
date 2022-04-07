import json
from datetime import datetime
from typing import Any, Dict, Callable, Type

from edr_server.core.models import TemporalExtent


def json_encode_datetime(dt: datetime) -> str:
    # Whilst wrapping this simple function call in a function may seem like overkill, it allows us to include it in
    # EdrJsonEncoder.ENCODER_MAP, so it gets hooked into the JSON Encoder correctly. Also, it documents that datetimes
    # should be encoded as ISO 8601 datetimes
    return dt.isoformat()


def json_encode_temporal_extent(temporal_extent: TemporalExtent) -> Dict[str, Any]:
    return {
        "name": temporal_extent.trs.name,
        "trs": temporal_extent.trs.wkt,
        "interval": [temporal_extent.bounds],
        "values": list(map(json_encode_datetime, temporal_extent.values)) + list(map(str, temporal_extent.intervals))
    }


class EdrJsonEncoder(json.JSONEncoder):
    ENCODER_MAP: Dict[Type, Callable[[Any], Dict[str, Any]]] = {
        datetime: json_encode_datetime,
        TemporalExtent: json_encode_temporal_extent,
    }

    def default(self, obj: Any) -> Any:
        try:
            # We try the super method first, because this is the most common code path, since most things
            # can be encoded by the json library
            return super().default(obj)
        except TypeError as type_err:
            try:
                return self.ENCODER_MAP[type(obj)](obj)
            except KeyError:
                raise type_err  # Re-raise original error, it's more appropriate than a Key Error
