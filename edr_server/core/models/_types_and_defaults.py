"""
This module exists to break some circular import issues, hence it's a private module, and its public interface
is via edr_server.cor.models (e.g. `from edr_server.core.models import EdrDataQuery`)

But modules within the `models` package should import it using `from ._types_and_defaults import ...`

I'd rather it didn't exist, but after experimenting seems to be the "least bad" option
 """
from enum import Enum

CollectionId = str
ItemId = str


class EdrDataQuery(Enum):
    AREA = "area"
    CORRIDOR = "corridor"
    CUBE = "cube"
    ITEMS = "items"
    LOCATIONS = "locations"
    POSITION = "position"
    RADIUS = "radius"
    TRAJECTORY = "trajectory"
