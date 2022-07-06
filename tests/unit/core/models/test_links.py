import unittest

from edr_server.core.exceptions import InvalidEdrJsonError
from edr_server.core.models import EdrDataQuery
from edr_server.core.models.crs import CrsObject
from edr_server.core.models.links import AreaDataQuery, CorridorDataQuery, CubeDataQuery


class AreaDataQueryTest(unittest.TestCase):

    def setUp(self) -> None:
        test_title = "Area Data Query"
        test_description = "This is a description that doesn't describe anything"
        test_output_formats = ["application/netcdf", "application/geo+json", "application/prs.coverage+json"]
        test_crs_details = [
            CrsObject(4326), CrsObject(4277), CrsObject(4188)
        ]

        self.test_area_query = AreaDataQuery(
            test_output_formats, test_output_formats[0], test_crs_details, test_title, test_description)

        # According to
        # https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/a0ab69d/standard/openapi/schemas/collections/areaDataQuery.yaml
        # none of these fields are required, so they could all potentially be missing
        self.test_serialised_area_data_query = {
            "title": test_title,
            "description": test_description,
            "query_type": "area",
            "output_formats": test_output_formats,
            "default_output_format": test_output_formats[0],
            "crs_details": {
                crs.name: {"crs": crs.name, "wkt": crs.to_wkt()} for crs in test_crs_details
            }
        }

    def test_init_defaults(self):
        """GIVEN no arguments are supplied WHEN an AreaDataQuery is instantiated THEN default values are set"""
        actual_area_dq = AreaDataQuery()

        self.assertEqual(actual_area_dq.title, "Area Data Query")
        self.assertEqual(actual_area_dq.description, "Query to return data for a defined area")
        self.assertEqual(actual_area_dq.get_query_type(), EdrDataQuery.AREA)
        self.assertEqual(actual_area_dq.output_formats, [])
        self.assertEqual(actual_area_dq.default_output_format, None)
        self.assertEqual(actual_area_dq.crs_details, [CrsObject(4326)])

    def test_init_default_output_format_inferred(self):
        """
        GIVEN output_formats is provided AND default_output_format is not
        WHEN an AreaDataQuery is instantiated
        THEN default_output_format is inferred from the provided output_formats
        """
        test_output_formats = ["application/netcdf", "application/geo+json", "application/prs.coverage+json"]
        expected_default_output_format = test_output_formats[0]

        test_area_dq = AreaDataQuery(output_formats=test_output_formats)

        self.assertEqual(test_area_dq.default_output_format, expected_default_output_format)

    def test__eq__(self):
        """GIVEN 2 AreaDataQuery objects that have the same values WHEN they are compared THEN they are equal"""
        self.assertEqual(AreaDataQuery(), AreaDataQuery())

        adq1 = AreaDataQuery.from_json(self.test_serialised_area_data_query)
        adq2 = AreaDataQuery.from_json(self.test_serialised_area_data_query)
        self.assertEqual(adq1, adq2)

    def test__neq__(self):
        """GIVEN 2 AreaDataQuery objects that have different values WHEN they are compared THEN they are not equal"""
        self.assertNotEqual(self.test_area_query, AreaDataQuery())
        self.assertNotEqual(AreaDataQuery(), CorridorDataQuery())

    def test_to_json(self):
        """GIVEN an AreaDataQuery WHEN to_json() is called THEN the expected JSON is produced"""
        expected_json = self.test_serialised_area_data_query

        actual_json = self.test_area_query.to_json()

        self.assertEqual(actual_json, expected_json)

    def test_to_json_defaults(self):
        """
        GIVEN an AreaDataQuery created using default values WHEN to_json() is called THEN the expected JSON is produced
        """
        test_area_dq = AreaDataQuery()
        gps_crs = CrsObject(4326)
        expected_json = {
            "title": "Area Data Query",
            "description": "Query to return data for a defined area",
            "query_type": "area",
            "crs_details": {
                gps_crs.name: {
                    "crs": gps_crs.name,
                    "wkt": gps_crs.to_wkt(),
                }
            },
        }

        actual_json = test_area_dq.to_json()

        self.assertEqual(expected_json, actual_json)

    def test_to_json_output_formats_empty_list(self):
        """
        GIVEN output_formats is an empty list WHEN to_json() is called THEN output_formats is not included in the JSON
        """
        test_area_dq = AreaDataQuery(output_formats=[])
        gps_crs = CrsObject(4326)
        expected_json = {
            "title": "Area Data Query",
            "description": "Query to return data for a defined area",
            "query_type": "area",
            "crs_details": {
                gps_crs.name: {
                    "crs": gps_crs.name,
                    "wkt": gps_crs.to_wkt(),
                }
            },
        }

        actual_json = test_area_dq.to_json()

        self.assertEqual(actual_json, expected_json)

    def test_from_json(self):
        """
        GIVEN a dict deserialised from valid JSON for an AreaDataQuery
        WHEN from_json() is called
        THEN an AreaDataQuery is returned with equivalent values
        """
        expected_adq = self.test_area_query

        actual_adq = AreaDataQuery.from_json(self.test_serialised_area_data_query)

        self.assertEqual(actual_adq, expected_adq)

    def test_from_json_empty_dict(self):
        """
        GIVEN an empty dictionary
        WHEN the empty dict is passed to from_json()
        THEN an AreaDataQuery with default values is returned
        """
        expected_area_dq = AreaDataQuery()

        actual_area_dq = AreaDataQuery.from_json({})

        self.assertEqual(actual_area_dq, expected_area_dq)

    def test_from_json_query_type_wrong(self):
        """
        GIVEN a dict where the query_type key is not "area"
        WHEN the dict is passed to from_json()
        THEN an InvalidEdrJsonError is raised
        """

        self.assertRaises(InvalidEdrJsonError, AreaDataQuery.from_json, {"query_type": "wrong!"})

    def test_from_json_query_type_missing(self):
        """
        GIVEN a JSON dict that doesn't have a "query_type" key
        WHEN the dict is passed to from_json()
        THEN an AreaDataQuery with equivalent values is returned
        """
        expected_area_dq = self.test_area_query
        test_json = self.test_serialised_area_data_query.copy()
        del test_json["query_type"]

        actual_area_dq = AreaDataQuery.from_json(test_json)

        self.assertEqual(actual_area_dq, expected_area_dq)

    def test_from_json_unexpected_key(self):
        """
        GIVEN a JSON dict that has all the expected keys with valid values
        AND an unexpected key
        WHEN the dict is passed to from_json()
        THEN an InvalidEdrJsonError is raised
        """
        test_json = self.test_serialised_area_data_query.copy()
        test_json["what the hell is this?"] = "12355"

        self.assertRaises(InvalidEdrJsonError, AreaDataQuery.from_json, test_json)


class CorridorDataQueryTest(unittest.TestCase):

    def setUp(self) -> None:
        test_title = "Corridor Data Query"
        test_description = "This is a description that doesn't describe anything"
        test_output_formats = ["application/netcdf", "application/geo+json", "application/prs.coverage+json"]
        test_crs_details = [
            CrsObject(4326), CrsObject(4277), CrsObject(4188)
        ]
        test_height_units = ["m", "hPa"]
        test_width_units = ["mi", "km"]

        self.test_corridor_query = CorridorDataQuery(
            test_output_formats, test_output_formats[0], test_crs_details, test_title, test_description,
            test_width_units, test_height_units,
        )

        # According to
        # https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/8427963/standard/openapi/schemas/collections/corridorDataQuery.yaml
        # none of these fields are required, so they could all potentially be missing
        self.test_serialised_corridor_data_query = {
            "title": test_title,
            "description": test_description,
            "query_type": "corridor",
            "output_formats": test_output_formats,
            "default_output_format": test_output_formats[0],
            "crs_details": {crs.name: {"crs": crs.name, "wkt": crs.to_wkt()} for crs in test_crs_details},
            "width_units": test_width_units,
            "height_units": test_height_units,
        }

    def test_init_defaults(self):
        """GIVEN no arguments are supplied WHEN an CorridorDataQuery is instantiated THEN default values are set"""
        actual_corridor_dq = CorridorDataQuery()

        self.assertEqual(actual_corridor_dq.title, "Corridor Data Query")
        self.assertEqual(actual_corridor_dq.description, "Query to return data for a defined corridor")
        self.assertEqual(actual_corridor_dq.get_query_type(), EdrDataQuery.CORRIDOR)
        self.assertEqual(actual_corridor_dq.output_formats, [])
        self.assertEqual(actual_corridor_dq.default_output_format, None)
        self.assertEqual(actual_corridor_dq.crs_details, [CrsObject(4326)])
        self.assertEqual(actual_corridor_dq.width_units, [])
        self.assertEqual(actual_corridor_dq.height_units, [])

    def test_init_default_output_format_inferred(self):
        """
        GIVEN output_formats is provided AND default_output_format is not
        WHEN an CorridorDataQuery is instantiated
        THEN default_output_format is inferred from the provided output_formats
        """
        test_output_formats = ["application/netcdf", "application/geo+json", "application/prs.coverage+json"]
        expected_default_output_format = test_output_formats[0]

        test_corridor_dq = CorridorDataQuery(output_formats=test_output_formats)

        self.assertEqual(test_corridor_dq.default_output_format, expected_default_output_format)

    def test__eq__(self):
        """GIVEN 2 CorridorDataQuery objects that have the same values WHEN they are compared THEN they are equal"""
        self.assertEqual(CorridorDataQuery(), CorridorDataQuery())

        cdq1 = CorridorDataQuery.from_json(self.test_serialised_corridor_data_query)
        cdq2 = CorridorDataQuery.from_json(self.test_serialised_corridor_data_query)
        self.assertEqual(cdq1, cdq2)

    def test__neq__(self):
        """
        GIVEN 2 CorridorDataQuery objects that have different values WHEN they are compared THEN they are not equal
        """
        self.assertNotEqual(self.test_corridor_query, CorridorDataQuery())
        self.assertNotEqual(CorridorDataQuery(), AreaDataQuery())

    def test__neq__extra_fields(self):
        """
        This test checks that we've updated the equality comparison logic to include any attributes we've extended the
        class with

        GIVEN 2 CorridorDataQuery instances
        AND any attributes added to the class (i.e. those not defined by the superclass) differ
        AND inherited fields are the same
        WHEN they are compared
        THEN they are not equal
        """
        json1 = self.test_serialised_corridor_data_query.copy()
        json1["width_units"] = ["football pitches"]
        cdq1 = CorridorDataQuery.from_json(json1)
        self.assertNotEqual(cdq1, self.test_corridor_query)

        json2 = self.test_serialised_corridor_data_query.copy()
        json2["height_units"] = ["Eiffel Towers"]
        cdq2 = CorridorDataQuery.from_json(json2)
        self.assertNotEqual(cdq2, self.test_corridor_query)

    def test_to_json(self):
        """GIVEN an CorridorDataQuery WHEN to_json() is called THEN the expected JSON is produced"""
        expected_json = self.test_serialised_corridor_data_query

        actual_json = self.test_corridor_query.to_json()

        self.assertEqual(actual_json, expected_json)

    def test_to_json_defaults(self):
        """
        GIVEN an CorridorDataQuery created using default values
        WHEN to_json() is called
        THEN the expected JSON is produced
        """
        test_corridor_dq = CorridorDataQuery()
        gps_crs = CrsObject(4326)
        expected_json = {
            "title": "Corridor Data Query",
            "description": "Query to return data for a defined corridor",
            "query_type": "corridor",
            "crs_details": {
                gps_crs.name: {
                    "crs": gps_crs.name,
                    "wkt": gps_crs.to_wkt(),
                }
            },
        }

        actual_json = test_corridor_dq.to_json()

        self.assertEqual(expected_json, actual_json)

    def test_to_json_output_formats_empty_list(self):
        """
        GIVEN output_formats is an empty list WHEN to_json() is called THEN output_formats is not included in the JSON
        """
        test_corridor_dq = CorridorDataQuery(output_formats=[])
        gps_crs = CrsObject(4326)
        expected_json = {
            "title": "Corridor Data Query",
            "description": "Query to return data for a defined corridor",
            "query_type": "corridor",
            "crs_details": {
                gps_crs.name: {
                    "crs": gps_crs.name,
                    "wkt": gps_crs.to_wkt(),
                }
            },
        }

        actual_json = test_corridor_dq.to_json()

        self.assertEqual(expected_json, actual_json)

    def test_to_json_width_units_empty_list(self):
        """
        GIVEN width_units is an empty list WHEN to_json() is called THEN width_units is not included in the JSON
        """
        test_corridor_dq = CorridorDataQuery(width_units=[])
        gps_crs = CrsObject(4326)
        expected_json = {
            "title": "Corridor Data Query",
            "description": "Query to return data for a defined corridor",
            "query_type": "corridor",
            "crs_details": {
                gps_crs.name: {
                    "crs": gps_crs.name,
                    "wkt": gps_crs.to_wkt(),
                }
            },
        }

        actual_json = test_corridor_dq.to_json()

        self.assertEqual(expected_json, actual_json)

    def test_to_json_height_units_empty_list(self):
        """
        GIVEN height_units is an empty list WHEN to_json() is called THEN height_units is not included in the JSON
        """
        test_corridor_dq = CorridorDataQuery(height_units=[])
        gps_crs = CrsObject(4326)
        expected_json = {
            "title": "Corridor Data Query",
            "description": "Query to return data for a defined corridor",
            "query_type": "corridor",
            "crs_details": {
                gps_crs.name: {
                    "crs": gps_crs.name,
                    "wkt": gps_crs.to_wkt(),
                }
            },
        }

        actual_json = test_corridor_dq.to_json()

        self.assertEqual(expected_json, actual_json)

    def test_from_json(self):
        """
        GIVEN a dict deserialised from valid JSON for an AreaDataQuery
        WHEN from_json() is called
        THEN an CorridorDataQuery is returned with equivalent values
        """
        expected_cdq = self.test_corridor_query

        actual_cdq = CorridorDataQuery.from_json(self.test_serialised_corridor_data_query)

        self.assertEqual(actual_cdq, expected_cdq)

    def test_from_json_empty_dict(self):
        """
        GIVEN an empty dictionary
        WHEN the empty dict is passed to from_json()
        THEN an CorridorDataQuery with default values is returned
        """
        expected_corridor_dq = CorridorDataQuery()

        actual_corridor_dq = CorridorDataQuery.from_json({})

        self.assertEqual(actual_corridor_dq, expected_corridor_dq)

    def test_from_json_query_type_wrong(self):
        """
        GIVEN a dict where the query_type key is not "area"
        WHEN the dict is passed to from_json()
        THEN an InvalidEdrJsonError is raised
        """

        self.assertRaises(InvalidEdrJsonError, CorridorDataQuery.from_json, {"query_type": "wrong!"})

    def test_from_json_query_type_missing(self):
        """
        GIVEN a JSON dict that doesn't have a "query_type" key
        WHEN the dict is passed to from_json()
        THEN an CorridorDataQuery with equivalent values is returned
        """
        expected_corridor_dq = self.test_corridor_query
        test_json = self.test_serialised_corridor_data_query.copy()
        del test_json["query_type"]

        actual_corridor_dq = CorridorDataQuery.from_json(test_json)

        self.assertEqual(actual_corridor_dq, expected_corridor_dq)

    def test_from_json_unexpected_key(self):
        """
        GIVEN a JSON dict that has all the expected keys with valid values
        AND an unexpected key
        WHEN the dict is passed to from_json()
        THEN an InvalidEdrJsonError is raised
        """
        test_json = self.test_serialised_corridor_data_query.copy()
        test_json["what the hell is this?"] = "12355"

        self.assertRaises(InvalidEdrJsonError, CorridorDataQuery.from_json, test_json)


class CubeDataQueryTest(unittest.TestCase):

    def setUp(self) -> None:
        test_title = "Cube Data Query"
        test_description = "This is a description that doesn't describe anything"
        test_output_formats = ["application/netcdf", "application/geo+json", "application/prs.coverage+json"]
        test_crs_details = [
            CrsObject(4326), CrsObject(4277), CrsObject(4188)
        ]
        test_height_units = ["m", "hPa"]

        self.test_cube_query = CubeDataQuery(
            test_output_formats, test_output_formats[0], test_crs_details, test_title, test_description,
            test_height_units,
        )

        # According to
        # https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/8427963/standard/openapi/schemas/collections/cubeDataQuery.yaml
        # none of these fields are required, so they could all potentially be missing
        self.test_serialised_cube_data_query = {
            "title": test_title,
            "description": test_description,
            "query_type": "cube",
            "output_formats": test_output_formats,
            "default_output_format": test_output_formats[0],
            "crs_details": {crs.name: {"crs": crs.name, "wkt": crs.to_wkt()} for crs in test_crs_details},
            "height_units": test_height_units,
        }

    def test_init_defaults(self):
        """GIVEN no arguments are supplied WHEN an CubeDataQuery is instantiated THEN default values are set"""
        actual_cube_dq = CubeDataQuery()

        self.assertEqual(actual_cube_dq.title, "Cube Data Query")
        self.assertEqual(actual_cube_dq.description, "Query to return data for a cube defined by well known text")
        self.assertEqual(actual_cube_dq.get_query_type(), EdrDataQuery.CUBE)
        self.assertEqual(actual_cube_dq.output_formats, [])
        self.assertEqual(actual_cube_dq.default_output_format, None)
        self.assertEqual(actual_cube_dq.crs_details, [CrsObject(4326)])
        self.assertEqual(actual_cube_dq.height_units, [])

    def test_init_default_output_format_inferred(self):
        """
        GIVEN output_formats is provided AND default_output_format is not
        WHEN an CubeDataQuery is instantiated
        THEN default_output_format is inferred from the provided output_formats
        """
        test_output_formats = ["application/netcdf", "application/geo+json", "application/prs.coverage+json"]
        expected_default_output_format = test_output_formats[0]

        test_cube_dq = CubeDataQuery(output_formats=test_output_formats)

        self.assertEqual(test_cube_dq.default_output_format, expected_default_output_format)

    def test__eq__(self):
        """GIVEN 2 CubeDataQuery objects that have the same values WHEN they are compared THEN they are equal"""
        self.assertEqual(CubeDataQuery(), CubeDataQuery())

        cdq1 = CubeDataQuery.from_json(self.test_serialised_cube_data_query)
        cdq2 = CubeDataQuery.from_json(self.test_serialised_cube_data_query)
        self.assertEqual(cdq1, cdq2)

    def test__neq__(self):
        """
        GIVEN 2 CubeDataQuery objects that have different values WHEN they are compared THEN they are not equal
        """
        self.assertNotEqual(self.test_cube_query, CubeDataQuery())
        self.assertNotEqual(CubeDataQuery(), AreaDataQuery())

    def test__neq__extra_fields(self):
        """
        This test checks that we've updated the equality comparison logic to include any attributes we've extended the
        class with

        GIVEN 2 CubeDataQuery instances
        AND any attributes added to the class (i.e. those not defined by the superclass) differ
        AND inherited fields are the same
        WHEN they are compared
        THEN they are not equal
        """
        json2 = self.test_serialised_cube_data_query.copy()
        json2["height_units"] = ["Eiffel Towers"]
        cdq2 = CubeDataQuery.from_json(json2)
        self.assertNotEqual(cdq2, self.test_cube_query)

    def test_to_json(self):
        """GIVEN an CubeDataQuery WHEN to_json() is called THEN the expected JSON is produced"""
        expected_json = self.test_serialised_cube_data_query

        actual_json = self.test_cube_query.to_json()

        self.assertEqual(actual_json, expected_json)

    def test_to_json_defaults(self):
        """
        GIVEN an CubeDataQuery created using default values
        WHEN to_json() is called
        THEN the expected JSON is produced
        """
        test_cube_dq = CubeDataQuery()
        gps_crs = CrsObject(4326)
        expected_json = {
            "title": "Cube Data Query",
            "description": "Query to return data for a cube defined by well known text",
            "query_type": "cube",
            "crs_details": {
                gps_crs.name: {
                    "crs": gps_crs.name,
                    "wkt": gps_crs.to_wkt(),
                }
            },
        }

        actual_json = test_cube_dq.to_json()

        self.assertEqual(expected_json, actual_json)

    def test_to_json_output_formats_empty_list(self):
        """
        GIVEN output_formats is an empty list WHEN to_json() is called THEN output_formats is not included in the JSON
        """
        test_cube_dq = CubeDataQuery(output_formats=[])
        gps_crs = CrsObject(4326)
        expected_json = {
            "title": "Cube Data Query",
            "description": "Query to return data for a cube defined by well known text",
            "query_type": "cube",
            "crs_details": {
                gps_crs.name: {
                    "crs": gps_crs.name,
                    "wkt": gps_crs.to_wkt(),
                }
            },
        }

        actual_json = test_cube_dq.to_json()

        self.assertEqual(expected_json, actual_json)

    def test_to_json_height_units_empty_list(self):
        """
        GIVEN height_units is an empty list WHEN to_json() is called THEN height_units is not included in the JSON
        """
        test_cube_dq = CubeDataQuery(height_units=[])
        gps_crs = CrsObject(4326)
        expected_json = {
            "title": "Cube Data Query",
            "description": "Query to return data for a cube defined by well known text",
            "query_type": "cube",
            "crs_details": {
                gps_crs.name: {
                    "crs": gps_crs.name,
                    "wkt": gps_crs.to_wkt(),
                }
            },
        }

        actual_json = test_cube_dq.to_json()

        self.assertEqual(expected_json, actual_json)

    def test_from_json(self):
        """
        GIVEN a dict deserialised from valid JSON for an AreaDataQuery
        WHEN from_json() is called
        THEN an CubeDataQuery is returned with equivalent values
        """
        expected_cdq = self.test_cube_query

        actual_cdq = CubeDataQuery.from_json(self.test_serialised_cube_data_query)

        self.assertEqual(actual_cdq, expected_cdq)

    def test_from_json_empty_dict(self):
        """
        GIVEN an empty dictionary
        WHEN the empty dict is passed to from_json()
        THEN an CubeDataQuery with default values is returned
        """
        expected_cube_dq = CubeDataQuery()

        actual_cube_dq = CubeDataQuery.from_json({})

        self.assertEqual(actual_cube_dq, expected_cube_dq)

    def test_from_json_query_type_wrong(self):
        """
        GIVEN a dict where the query_type key is not "area"
        WHEN the dict is passed to from_json()
        THEN an InvalidEdrJsonError is raised
        """

        self.assertRaises(InvalidEdrJsonError, CubeDataQuery.from_json, {"query_type": "wrong!"})

    def test_from_json_query_type_missing(self):
        """
        GIVEN a JSON dict that doesn't have a "query_type" key
        WHEN the dict is passed to from_json()
        THEN an CubeDataQuery with equivalent values is returned
        """
        expected_cube_dq = self.test_cube_query
        test_json = self.test_serialised_cube_data_query.copy()
        del test_json["query_type"]

        actual_cube_dq = CubeDataQuery.from_json(test_json)

        self.assertEqual(actual_cube_dq, expected_cube_dq)

    def test_from_json_unexpected_key(self):
        """
        GIVEN a JSON dict that has all the expected keys with valid values
        AND an unexpected key
        WHEN the dict is passed to from_json()
        THEN an InvalidEdrJsonError is raised
        """
        test_json = self.test_serialised_cube_data_query.copy()
        test_json["what the hell is this?"] = "12355"

        self.assertRaises(InvalidEdrJsonError, CubeDataQuery.from_json, test_json)
