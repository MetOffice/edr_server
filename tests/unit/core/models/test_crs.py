import unittest

import pytest

from edr_server.core.models.crs import CrsObject, DEFAULT_CRS, DEFAULT_VRS, DEFAULT_TRS


class CrsObjectTest(unittest.TestCase):
    """
    We don't need to do extensive tests of this class because 99% of the implementation is inherited from pyproj.CRS.
    We'll just test the methods we overrode/added.
    """

    WGS84_WKT = ('GEOGCRS["WGS 84",ENSEMBLE["World Geodetic System 1984 ensemble",'
                 'MEMBER["World Geodetic System 1984 (Transit)"],MEMBER["World Geodetic System 1984 (G730)"],'
                 'MEMBER["World Geodetic System 1984 (G873)"],MEMBER["World Geodetic System 1984 (G1150)"],'
                 'MEMBER["World Geodetic System 1984 (G1674)"],MEMBER["World Geodetic System 1984 (G1762)"],'
                 'MEMBER["World Geodetic System 1984 (G2139)"],ELLIPSOID["WGS 84",6378137,298.257223563,'
                 'LENGTHUNIT["metre",1]],ENSEMBLEACCURACY[2.0]],PRIMEM["Greenwich",0,'
                 'ANGLEUNIT["degree",0.0174532925199433]],CS[ellipsoidal,2],AXIS["geodetic latitude (Lat)",north,'
                 'ORDER[1],ANGLEUNIT["degree",0.0174532925199433]],AXIS["geodetic longitude (Lon)",east,ORDER[2],'
                 'ANGLEUNIT["degree",0.0174532925199433]],USAGE[SCOPE["Horizontal component of 3D system."],'
                 'AREA["World."],BBOX[-90,-180,90,180]],ID["EPSG",4326]]')

    def test__repr__(self):
        crs1 = CrsObject(4326)
        expected_repr_crs1 = "CrsObject(4326)"
        self.assertEqual(expected_repr_crs1, repr(crs1))

        crs2_wkt = ('VERTCS["WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],'
                    'PARAMETER["Vertical_Shift",0.0],PARAMETER["Direction",1.0],UNIT["Meter",1.0]],AXIS["Up",UP]')
        crs2 = CrsObject(crs2_wkt)
        expected_repr_crs2 = f"CrsObject({crs2_wkt!r})"
        self.assertEqual(expected_repr_crs2, repr(crs2))

    def test_to_json(self):
        expected = {"crs": "WGS 84", "wkt": self.WGS84_WKT}
        actual = CrsObject("WGS84").to_json()
        self.assertEqual(expected, actual)

    def test_from_json(self):
        expected = CrsObject("WGS84")
        actual = CrsObject.from_json({"crs": "WGS 84", "wkt": self.WGS84_WKT})
        self.assertEqual(expected, actual)


@pytest.mark.parametrize("default, expected", (
        (DEFAULT_CRS, CrsObject(4326)),
        (DEFAULT_VRS, CrsObject(
            'VERTCS["WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],'
            'PARAMETER["Vertical_Shift",0.0],PARAMETER["Direction",1.0],UNIT["Meter",1.0]],AXIS["Up",UP]'
        )),
        (DEFAULT_TRS, CrsObject(
            'TIMECRS["DateTime",TDATUM["Gregorian Calendar"],CS[TemporalDateTime,1],AXIS["Time (T)",future]]')),
))
def test_default_crs(default: CrsObject, expected: CrsObject):
    assert default == expected
