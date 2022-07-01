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


DEFAULT_CRS = CrsObject("WGS84")
DEFAULT_VRS = CrsObject(
    'VERTCS["WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],'
    'PARAMETER["Vertical_Shift",0.0],PARAMETER["Direction",1.0],UNIT["Meter",1.0]],AXIS["Up",UP]'
)
DEFAULT_TRS = CrsObject(
    'TIMECRS["DateTime",TDATUM["Gregorian Calendar"],CS[TemporalDateTime,1],AXIS["Time (T)",future]]')
