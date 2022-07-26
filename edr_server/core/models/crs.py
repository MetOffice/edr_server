from typing import Dict, Any, Set

from pyproj import CRS

from . import EdrModel, JsonDict


class CrsObject(EdrModel["CrsObject"], CRS):
    """
    A subclass of pyproj's CRS class to override its to_json/from_json methods with EDR compliant implementations.
    This allows us to more easily (de)serialise these objects when they're used in other models.

    This class maps to the crsObject in the EDR OpenAPI, as defined here:
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/8427963/standard/openapi/schemas/collections/crsObject.yaml
    """

    def __init__(self, projparams: Any = None, **kwargs):
        # Override the usual MRO and use the CRS __init__ method instead of EdrModel
        # We do this rather than switch the order of the declared base classes because in most cases where there's a
        # choice of inherited methods with the same name, we want EdrModel to take precedence over CRS
        CRS.__init__(self, projparams, **kwargs)

    @classmethod
    def _get_expected_keys(cls) -> Set[str]:
        # Required to satisfy the Abstract Base Class, but actually we've overridden the from_json method,
        # so we don't actually use this and don't need it to do anything.
        pass

    @classmethod
    def _prepare_json_for_init(cls, json_dict: JsonDict) -> JsonDict:
        # Required to satisfy the Abstract Base Class, but actually we've overridden the from_json method,
        # so we don't actually use this and don't need it to do anything. This is relevant to the inherited abstract
        # methods and ensuring python applies the abstract base class correctly
        pass

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
