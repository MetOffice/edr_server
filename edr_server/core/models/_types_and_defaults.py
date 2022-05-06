"""
This module exists to break some circular import issues, hence it's a private module, and its public interface
is via edr_server.cor.models (e.g. `from edr_server.core.models import EdrDataQuery`)

But modules within the `models` package should import it using `from ._types_and_defaults import ...`

I'd rather it didn't exist, but after experimenting seems to be the "least bad" option
 """
from enum import Enum

import pyproj

CollectionId = str
ItemId = str


class EdrDataQuery(Enum):
    CUBE = "cube"
    CORRIDOR = "corridor"
    LOCATIONS = "locations"
    ITEMS = "items"
    AREA = "area"
    POSITION = "position"
    RADIUS = "radius"
    TRAJECTORY = "trajectory"


DEFAULT_CRS = pyproj.CRS("WGS84")
DEFAULT_VRS = pyproj.CRS(
    'VERTCS["WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],'
    'PARAMETER["Vertical_Shift",0.0],PARAMETER["Direction",1.0],UNIT["Meter",1.0]],AXIS["Up",UP]'
)
DEFAULT_TRS = 'TIMECRS["DateTime",TDATUM["Gregorian Calendar"],CS[TemporalDateTime,1],AXIS["Time (T)",future]'
