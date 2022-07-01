import unittest

from edr_server.core.models.crs import CrsObject


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

    def test_to_json(self):
        expected = {"crs": "WGS 84", "wkt": self.WGS84_WKT}
        actual = CrsObject("WGS84").to_json()
        self.assertEqual(expected, actual)

    def test_from_json(self):
        expected = CrsObject("WGS84")
        actual = CrsObject.from_json({"crs": "WGS 84", "wkt": self.WGS84_WKT})
        self.assertEqual(expected, actual)
