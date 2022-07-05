from typing import Dict, Any

from pyproj import CRS

from edr_server.core.models import EdrModel


class CrsObject(EdrModel["CrsObject"], CRS):
    """
    A subclass of pyproj's CRS class to override its to_json/from_json methods with EDR compliant implementations.
    This allows us to more easily (de)serialise these objects when they're used in other models.

    This class maps to the crsObject in the EDR OpenAPI, as defined here:
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/8427963/standard/openapi/schemas/collections/crsObject.yaml
    """

    def to_json(self) -> Dict[str, Any]:
        return {"crs": self.name, "wkt": self.to_wkt()}

    @classmethod
    def from_json(cls, json_dict: Dict[str, Any]) -> "CrsObject":
        return CrsObject.from_wkt(json_dict["wkt"])

    def __repr__(self):
        # Inherited pyproj.CRS.__repr__ converts to wkt, which is looooong. This will check whether we can identify a
        # matching ESPG code to use instead of the verbose WKT. Requires 100% confidence as we don't want to lose any
        # information and falls back to WKT if it can't find a match. Also returns the correct class name
        arg = espg if (espg := self.to_epsg(100)) else str(self)
        # str() returns the WKT as provided to the constructor by the creator,
        # whereas .to_wkt() seems to try and match it to a known CRS from the EPSG database
        return f"CrsObject({arg!r})"


DEFAULT_CRS = CrsObject(4326)
DEFAULT_VRS = CrsObject(
    'VERTCS["WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],'
    'PARAMETER["Vertical_Shift",0.0],PARAMETER["Direction",1.0],UNIT["Meter",1.0]],AXIS["Up",UP]'
)
DEFAULT_TRS = CrsObject(
    'TIMECRS["DateTime",TDATUM["Gregorian Calendar"],CS[TemporalDateTime,1],AXIS["Time (T)",future]]')
