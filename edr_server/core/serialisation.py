import json
from datetime import datetime
from typing import Any

from .models import EdrModel


def json_encode_datetime(dt: datetime) -> str:
    # Whilst wrapping this simple function call in a function may seem like overkill, it allows us to include it in
    # EdrJsonEncoder.ENCODER_MAP, so it gets hooked into the JSON Encoder correctly. Also, it documents that datetime
    # objects should be encoded using the ISO 8601 datetime format.

    # Is your serialised datetime missing a `Z` or other timezone designator?
    # You need to set the timezone on your datetimes, otherwise it is a timezone naive datetime and will not have
    # timezone information. E.g. datetime(2022,5,19, tzinfo=timezone.utc) or datetime.now().replace(tzinfo=timezone.utc)

    # This code is fine and correctly handles both timezone aware and timezone naive datetimes.
    return dt.isoformat()  # Did I mention that if you're having timezone serialisation issues, this code is fine?


class EdrJsonEncoder(json.JSONEncoder):

    def default(self, obj: Any) -> Any:
        """Return a JSON encodable version of objects that can't otherwise be serialised, or raise a TypeError"""
        if isinstance(obj, datetime):
            return json_encode_datetime(obj)
        elif isinstance(obj, EdrModel):
            return obj.to_json()
        else:
            return super().default(obj)
