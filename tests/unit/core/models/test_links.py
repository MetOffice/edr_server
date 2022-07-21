import unittest

from edr_server.core.exceptions import InvalidEdrJsonError
from edr_server.core.models import EdrDataQuery
from edr_server.core.models.crs import CrsObject
from edr_server.core.models.links import AreaDataQuery, CorridorDataQuery, CubeDataQuery, LocationsDataQuery, \
    PositionDataQuery, ItemsDataQuery, RadiusDataQuery, TrajectoryDataQuery, DataQueryLink, DATA_QUERY_MAP
from edr_server.core.models.urls import URL


class AreaDataQueryTest(unittest.TestCase):

    def setUp(self) -> None:
        test_title = "Area Data Query"
        test_description = "This is a description that doesn't describe anything"
        test_output_formats = ["application/netcdf", "application/geo+json", "application/prs.coverage+json"]
        test_crs_details = [CrsObject(4326), CrsObject(4277), CrsObject(4188)]

        self.test_area_query = AreaDataQuery(
            test_title, test_description, test_output_formats, test_output_formats[0], test_crs_details)

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
        self.assertEqual(actual_area_dq.description, "Select data that is within a defined area.")
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
            "description": "Select data that is within a defined area.",
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
            "description": "Select data that is within a defined area.",
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
            test_title, test_description, test_output_formats, test_output_formats[0], test_crs_details,
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
        """GIVEN no arguments are supplied WHEN a corridorDataQuery is instantiated THEN default values are set"""
        actual_corridor_dq = CorridorDataQuery()

        self.assertEqual(actual_corridor_dq.title, "Corridor Data Query")
        self.assertEqual(actual_corridor_dq.description, "Select data that is within a defined corridor.")
        self.assertEqual(actual_corridor_dq.get_query_type(), EdrDataQuery.CORRIDOR)
        self.assertEqual(actual_corridor_dq.output_formats, [])
        self.assertEqual(actual_corridor_dq.default_output_format, None)
        self.assertEqual(actual_corridor_dq.crs_details, [CrsObject(4326)])
        self.assertEqual(actual_corridor_dq.width_units, [])
        self.assertEqual(actual_corridor_dq.height_units, [])

    def test_init_default_output_format_inferred(self):
        """
        GIVEN output_formats is provided AND default_output_format is not
        WHEN a corridorDataQuery is instantiated
        THEN default_output_format is inferred from the provided output_formats
        """
        test_output_formats = ["application/netcdf", "application/geo+json", "application/prs.coverage+json"]
        expected_default_output_format = test_output_formats[0]

        test_corridor_dq = CorridorDataQuery(output_formats=test_output_formats)

        self.assertEqual(expected_default_output_format, test_corridor_dq.default_output_format)

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
        """GIVEN a corridorDataQuery WHEN to_json() is called THEN the expected JSON is produced"""
        expected_json = self.test_serialised_corridor_data_query

        actual_json = self.test_corridor_query.to_json()

        self.assertEqual(actual_json, expected_json)

    def test_to_json_defaults(self):
        """
        GIVEN a corridorDataQuery created using default values
        WHEN to_json() is called
        THEN the expected JSON is produced
        """
        test_corridor_dq = CorridorDataQuery()
        gps_crs = CrsObject(4326)
        expected_json = {
            "title": "Corridor Data Query",
            "description": "Select data that is within a defined corridor.",
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
            "description": "Select data that is within a defined corridor.",
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
            "description": "Select data that is within a defined corridor.",
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
            "description": "Select data that is within a defined corridor.",
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
        GIVEN a dict deserialised from valid JSON for a CorridorDataQuery
        WHEN from_json() is called
        THEN anCorridorDataQuery is returned with equivalent values
        """
        expected_cdq = self.test_corridor_query

        actual_cdq = CorridorDataQuery.from_json(self.test_serialised_corridor_data_query)

        self.assertEqual(actual_cdq, expected_cdq)

    def test_from_json_empty_dict(self):
        """
        GIVEN an empty dictionary
        WHEN the empty dict is passed to from_json()
        THEN a corridorDataQuery with default values is returned
        """
        expected_corridor_dq = CorridorDataQuery()

        actual_corridor_dq = CorridorDataQuery.from_json({})

        self.assertEqual(actual_corridor_dq, expected_corridor_dq)

    def test_from_json_query_type_wrong(self):
        """
        GIVEN a dict where the query_type key is not "corridor"
        WHEN the dict is passed to from_json()
        THEN an InvalidEdrJsonError is raised
        """

        self.assertRaises(InvalidEdrJsonError, CorridorDataQuery.from_json, {"query_type": "wrong!"})

    def test_from_json_query_type_missing(self):
        """
        GIVEN a JSON dict that doesn't have a "query_type" key
        WHEN the dict is passed to from_json()
        THEN a corridorDataQuery with equivalent values is returned
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


class ItemsQueryTest(unittest.TestCase):

    def setUp(self) -> None:
        test_title = "Items Data Query"
        test_description = "This is a description that doesn't describe anything"

        self.test_items_query = ItemsDataQuery(test_title, test_description)

        # According to
        # https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/a0ab69d/standard/openapi/schemas/collections/itemsDataQuery.yaml
        # none of these fields are required, so they could all potentially be missing
        self.test_serialised_items_data_query = {
            "title": test_title,
            "description": test_description,
            "query_type": "items",
        }

    def test_init_defaults(self):
        """GIVEN no arguments are supplied WHEN an ItemsDataQuery is instantiated THEN default values are set"""
        actual_items_dq = ItemsDataQuery()

        self.assertEqual(actual_items_dq.title, "Items Data Query")
        self.assertEqual(
            actual_items_dq.description, "Select data based on predetermined groupings of data organised into items.")
        self.assertEqual(actual_items_dq.get_query_type(), EdrDataQuery.ITEMS)

    def test__eq__(self):
        """GIVEN 2 ItemsDataQuery objects that have the same values WHEN they are compared THEN they are equal"""
        self.assertEqual(ItemsDataQuery(), ItemsDataQuery())

        adq1 = ItemsDataQuery.from_json(self.test_serialised_items_data_query)
        adq2 = ItemsDataQuery.from_json(self.test_serialised_items_data_query)
        self.assertEqual(adq1, adq2)

    def test__neq__(self):
        """GIVEN 2 ItemsDataQuery objects that have different values WHEN they are compared THEN they are not equal"""
        self.assertNotEqual(self.test_items_query, ItemsDataQuery())
        self.assertNotEqual(ItemsDataQuery(), CorridorDataQuery())

    def test_to_json(self):
        """GIVEN an ItemsDataQuery WHEN to_json() is called THEN the expected JSON is produced"""
        expected_json = self.test_serialised_items_data_query

        actual_json = self.test_items_query.to_json()

        self.assertEqual(actual_json, expected_json)

    def test_to_json_defaults(self):
        """
        GIVEN an ItemsDataQuery created using default values WHEN to_json() is called THEN the expected JSON is produced
        """
        test_items_dq = ItemsDataQuery()
        expected_json = {
            "title": "Items Data Query",
            "description": "Select data based on predetermined groupings of data organised into items.",
            "query_type": "items",
        }

        actual_json = test_items_dq.to_json()

        self.assertEqual(expected_json, actual_json)

    def test_from_json(self):
        """
        GIVEN a dict deserialised from valid JSON for an ItemsDataQuery
        WHEN from_json() is called
        THEN an ItemsDataQuery is returned with equivalent values
        """
        expected_idq = self.test_items_query

        actual_idq = ItemsDataQuery.from_json(self.test_serialised_items_data_query)

        self.assertEqual(actual_idq, expected_idq)

    def test_from_json_empty_dict(self):
        """
        GIVEN an empty dictionary
        WHEN the empty dict is passed to from_json()
        THEN an ItemsDataQuery with default values is returned
        """
        expected_items_dq = ItemsDataQuery()

        actual_items_dq = ItemsDataQuery.from_json({})

        self.assertEqual(actual_items_dq, expected_items_dq)

    def test_from_json_query_type_wrong(self):
        """
        GIVEN a dict where the query_type key is not "items"
        WHEN the dict is passed to from_json()
        THEN an InvalidEdrJsonError is raised
        """

        self.assertRaises(InvalidEdrJsonError, ItemsDataQuery.from_json, {"query_type": "wrong!"})

    def test_from_json_query_type_missing(self):
        """
        GIVEN a JSON dict that doesn't have a "query_type" key
        WHEN the dict is passed to from_json()
        THEN an ItemsDataQuery with equivalent values is returned
        """
        expected_items_dq = self.test_items_query
        test_json = self.test_serialised_items_data_query.copy()
        del test_json["query_type"]

        actual_items_dq = ItemsDataQuery.from_json(test_json)

        self.assertEqual(actual_items_dq, expected_items_dq)

    def test_from_json_unexpected_key(self):
        """
        GIVEN a JSON dict that has all the expected keys with valid values
        AND an unexpected key
        WHEN the dict is passed to from_json()
        THEN an InvalidEdrJsonError is raised
        """
        test_title = "Items Data Query"
        test_description = "This is a description that doesn't describe anything"
        test_output_formats = ["application/netcdf", "application/geo+json", "application/prs.coverage+json"]
        test_crs_details = [CrsObject(4326), CrsObject(4277), CrsObject(4188)]
        test_json = {
            "title": test_title,
            "description": test_description,
            "query_type": "items",
            # The fields below this point aren't valid for Items Data Queries
            "output_formats": test_output_formats,
            "default_output_format": test_output_formats[0],
            "crs_details": {crs.name: {"crs": crs.name, "wkt": crs.to_wkt()} for crs in test_crs_details},
        }

        self.assertRaises(InvalidEdrJsonError, ItemsDataQuery.from_json, test_json)


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
            test_title, test_description, test_output_formats, test_output_formats[0], test_crs_details,
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
        """GIVEN no arguments are supplied WHEN a CubeDataQuery is instantiated THEN default values are set"""
        actual_cube_dq = CubeDataQuery()

        self.assertEqual(actual_cube_dq.title, "Cube Data Query")
        self.assertEqual(actual_cube_dq.description, "Select data that is within a defined cube.")
        self.assertEqual(actual_cube_dq.get_query_type(), EdrDataQuery.CUBE)
        self.assertEqual(actual_cube_dq.output_formats, [])
        self.assertEqual(actual_cube_dq.default_output_format, None)
        self.assertEqual(actual_cube_dq.crs_details, [CrsObject(4326)])
        self.assertEqual(actual_cube_dq.height_units, [])

    def test_init_default_output_format_inferred(self):
        """
        GIVEN output_formats is provided AND default_output_format is not
        WHEN a CubeDataQuery is instantiated
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
        """GIVEN a CubeDataQuery WHEN to_json() is called THEN the expected JSON is produced"""
        expected_json = self.test_serialised_cube_data_query

        actual_json = self.test_cube_query.to_json()

        self.assertEqual(actual_json, expected_json)

    def test_to_json_defaults(self):
        """
        GIVEN a CubeDataQuery created using default values
        WHEN to_json() is called
        THEN the expected JSON is produced
        """
        test_cube_dq = CubeDataQuery()
        gps_crs = CrsObject(4326)
        expected_json = {
            "title": "Cube Data Query",
            "description": "Select data that is within a defined cube.",
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
            "description": "Select data that is within a defined cube.",
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
            "description": "Select data that is within a defined cube.",
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
        GIVEN a dict deserialised from valid JSON for a CubeDataQuery
        WHEN from_json() is called
        THEN a CubeDataQuery is returned with equivalent values
        """
        expected_cdq = self.test_cube_query

        actual_cdq = CubeDataQuery.from_json(self.test_serialised_cube_data_query)

        self.assertEqual(actual_cdq, expected_cdq)

    def test_from_json_empty_dict(self):
        """
        GIVEN an empty dictionary
        WHEN the empty dict is passed to from_json()
        THEN a CubeDataQuery with default values is returned
        """
        expected_cube_dq = CubeDataQuery()

        actual_cube_dq = CubeDataQuery.from_json({})

        self.assertEqual(actual_cube_dq, expected_cube_dq)

    def test_from_json_query_type_wrong(self):
        """
        GIVEN a dict where the query_type key is not "cube"
        WHEN the dict is passed to from_json()
        THEN an InvalidEdrJsonError is raised
        """

        self.assertRaises(InvalidEdrJsonError, CubeDataQuery.from_json, {"query_type": "wrong!"})

    def test_from_json_query_type_missing(self):
        """
        GIVEN a JSON dict that doesn't have a "query_type" key
        WHEN the dict is passed to from_json()
        THEN a CubeDataQuery with equivalent values is returned
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


class LocationsDataQueryTest(unittest.TestCase):

    def setUp(self) -> None:
        test_title = "Locations Data Query"
        test_description = "This is a description that doesn't describe anything"
        test_output_formats = ["application/netcdf", "application/geo+json", "application/prs.coverage+json"]
        test_crs_details = [CrsObject(4326), CrsObject(4277), CrsObject(4188)]

        self.test_locations_query = LocationsDataQuery(
            test_title, test_description, test_output_formats, test_output_formats[0], test_crs_details)

        # According to
        # https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/a0ab69d/standard/openapi/schemas/collections/locationsDataQuery.yaml
        # none of these fields are required, so they could all potentially be missing
        self.test_serialised_locations_data_query = {
            "title": test_title,
            "description": test_description,
            "query_type": "locations",
            "output_formats": test_output_formats,
            "default_output_format": test_output_formats[0],
            "crs_details": {
                crs.name: {"crs": crs.name, "wkt": crs.to_wkt()} for crs in test_crs_details
            }
        }

    def test_init_defaults(self):
        """GIVEN no arguments are supplied WHEN a LocationsDataQuery is instantiated THEN default values are set"""
        actual_locations_dq = LocationsDataQuery()

        self.assertEqual(actual_locations_dq.title, "Locations Data Query")
        self.assertEqual(actual_locations_dq.description, "Select data that is within a defined location.")
        self.assertEqual(actual_locations_dq.get_query_type(), EdrDataQuery.LOCATIONS)
        self.assertEqual(actual_locations_dq.output_formats, [])
        self.assertEqual(actual_locations_dq.default_output_format, None)
        self.assertEqual(actual_locations_dq.crs_details, [CrsObject(4326)])

    def test_init_default_output_format_inferred(self):
        """
        GIVEN output_formats is provided AND default_output_format is not
        WHEN a LocationsDataQuery is instantiated
        THEN default_output_format is inferred from the provided output_formats
        """
        test_output_formats = ["application/netcdf", "application/geo+json", "application/prs.coverage+json"]
        expected_default_output_format = test_output_formats[0]

        test_locations_dq = LocationsDataQuery(output_formats=test_output_formats)

        self.assertEqual(test_locations_dq.default_output_format, expected_default_output_format)

    def test__eq__(self):
        """GIVEN 2 LocationsDataQuery objects that have the same values WHEN they are compared THEN they are equal"""
        self.assertEqual(LocationsDataQuery(), LocationsDataQuery())

        adq1 = LocationsDataQuery.from_json(self.test_serialised_locations_data_query)
        adq2 = LocationsDataQuery.from_json(self.test_serialised_locations_data_query)
        self.assertEqual(adq1, adq2)

    def test__neq__(self):
        """
        GIVEN 2 LocationsDataQuery objects that have different values WHEN they are compared THEN they are not equal
        """
        self.assertNotEqual(self.test_locations_query, LocationsDataQuery())
        self.assertNotEqual(LocationsDataQuery(), CorridorDataQuery())

    def test_to_json(self):
        """GIVEN a LocationsDataQuery WHEN to_json() is called THEN the expected JSON is produced"""
        expected_json = self.test_serialised_locations_data_query

        actual_json = self.test_locations_query.to_json()

        self.assertEqual(actual_json, expected_json)

    def test_to_json_defaults(self):
        """
        GIVEN a LocationsDataQuery created using default values
        WHEN to_json() is called
        THEN the expected JSON is produced
        """
        test_locations_dq = LocationsDataQuery()
        gps_crs = CrsObject(4326)
        expected_json = {
            "title": "Locations Data Query",
            "description": "Select data that is within a defined location.",
            "query_type": "locations",
            "crs_details": {
                gps_crs.name: {
                    "crs": gps_crs.name,
                    "wkt": gps_crs.to_wkt(),
                }
            },
        }

        actual_json = test_locations_dq.to_json()

        self.assertEqual(expected_json, actual_json)

    def test_to_json_output_formats_empty_list(self):
        """
        GIVEN output_formats is an empty list WHEN to_json() is called THEN output_formats is not included in the JSON
        """
        test_locations_dq = LocationsDataQuery(output_formats=[])
        gps_crs = CrsObject(4326)
        expected_json = {
            "title": "Locations Data Query",
            "description": "Select data that is within a defined location.",
            "query_type": "locations",
            "crs_details": {
                gps_crs.name: {
                    "crs": gps_crs.name,
                    "wkt": gps_crs.to_wkt(),
                }
            },
        }

        actual_json = test_locations_dq.to_json()

        self.assertEqual(actual_json, expected_json)

    def test_from_json(self):
        """
        GIVEN a dict deserialised from valid JSON for a LocationsDataQuery
        WHEN from_json() is called
        THEN a LocationsDataQuery is returned with equivalent values
        """
        expected_adq = self.test_locations_query

        actual_adq = LocationsDataQuery.from_json(self.test_serialised_locations_data_query)

        self.assertEqual(actual_adq, expected_adq)

    def test_from_json_empty_dict(self):
        """
        GIVEN an empty dictionary
        WHEN the empty dict is passed to from_json()
        THEN a LocationsDataQuery with default values is returned
        """
        expected_locations_dq = LocationsDataQuery()

        actual_locations_dq = LocationsDataQuery.from_json({})

        self.assertEqual(actual_locations_dq, expected_locations_dq)

    def test_from_json_query_type_wrong(self):
        """
        GIVEN a dict where the query_type key is not "locations"
        WHEN the dict is passed to from_json()
        THEN an InvalidEdrJsonError is raised
        """

        self.assertRaises(InvalidEdrJsonError, LocationsDataQuery.from_json, {"query_type": "wrong!"})

    def test_from_json_query_type_missing(self):
        """
        GIVEN a JSON dict that doesn't have a "query_type" key
        WHEN the dict is passed to from_json()
        THEN a LocationsDataQuery with equivalent values is returned
        """
        expected_locations_dq = self.test_locations_query
        test_json = self.test_serialised_locations_data_query.copy()
        del test_json["query_type"]

        actual_locations_dq = LocationsDataQuery.from_json(test_json)

        self.assertEqual(actual_locations_dq, expected_locations_dq)

    def test_from_json_unexpected_key(self):
        """
        GIVEN a JSON dict that has all the expected keys with valid values
        AND an unexpected key
        WHEN the dict is passed to from_json()
        THEN an InvalidEdrJsonError is raised
        """
        test_json = self.test_serialised_locations_data_query.copy()
        test_json["what the hell is this?"] = "12355"

        self.assertRaises(InvalidEdrJsonError, LocationsDataQuery.from_json, test_json)


class PositionDataQueryTest(unittest.TestCase):

    def setUp(self) -> None:
        test_title = "Position Data Query"
        test_description = "This is a description that doesn't describe anything"
        test_output_formats = ["application/netcdf", "application/geo+json", "application/prs.coverage+json"]
        test_crs_details = [CrsObject(4326), CrsObject(4277), CrsObject(4188)]

        self.test_position_query = PositionDataQuery(
            test_title, test_description, test_output_formats, test_output_formats[0], test_crs_details)

        # According to
        # https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/a0ab69d/standard/openapi/schemas/collections/positionDataQuery.yaml
        # none of these fields are required, so they could all potentially be missing
        self.test_serialised_position_data_query = {
            "title": test_title,
            "description": test_description,
            "query_type": "position",
            "output_formats": test_output_formats,
            "default_output_format": test_output_formats[0],
            "crs_details": {
                crs.name: {"crs": crs.name, "wkt": crs.to_wkt()} for crs in test_crs_details
            }
        }

    def test_init_defaults(self):
        """GIVEN no arguments are supplied WHEN a PositionDataQuery is instantiated THEN default values are set"""
        actual_position_dq = PositionDataQuery()

        self.assertEqual(actual_position_dq.title, "Position Data Query")
        self.assertEqual(actual_position_dq.description, "Select data that is within a defined position.")
        self.assertEqual(actual_position_dq.get_query_type(), EdrDataQuery.POSITION)
        self.assertEqual(actual_position_dq.output_formats, [])
        self.assertEqual(actual_position_dq.default_output_format, None)
        self.assertEqual(actual_position_dq.crs_details, [CrsObject(4326)])

    def test_init_default_output_format_inferred(self):
        """
        GIVEN output_formats is provided AND default_output_format is not
        WHEN a PositionDataQuery is instantiated
        THEN default_output_format is inferred from the provided output_formats
        """
        test_output_formats = ["application/netcdf", "application/geo+json", "application/prs.coverage+json"]
        expected_default_output_format = test_output_formats[0]

        test_position_dq = PositionDataQuery(output_formats=test_output_formats)

        self.assertEqual(test_position_dq.default_output_format, expected_default_output_format)

    def test__eq__(self):
        """GIVEN 2 PositionDataQuery objects that have the same values WHEN they are compared THEN they are equal"""
        self.assertEqual(PositionDataQuery(), PositionDataQuery())

        adq1 = PositionDataQuery.from_json(self.test_serialised_position_data_query)
        adq2 = PositionDataQuery.from_json(self.test_serialised_position_data_query)
        self.assertEqual(adq1, adq2)

    def test__neq__(self):
        """
        GIVEN 2 PositionDataQuery objects that have different values WHEN they are compared THEN they are not equal
        """
        self.assertNotEqual(self.test_position_query, PositionDataQuery())
        self.assertNotEqual(PositionDataQuery(), CorridorDataQuery())

    def test_to_json(self):
        """GIVEN a PositionDataQuery WHEN to_json() is called THEN the expected JSON is produced"""
        expected_json = self.test_serialised_position_data_query

        actual_json = self.test_position_query.to_json()

        self.assertEqual(actual_json, expected_json)

    def test_to_json_defaults(self):
        """
        GIVEN a PositionDataQuery created using default values
        WHEN to_json() is called
        THEN the expected JSON is produced
        """
        test_position_dq = PositionDataQuery()
        gps_crs = CrsObject(4326)
        expected_json = {
            "title": "Position Data Query",
            "description": "Select data that is within a defined position.",
            "query_type": "position",
            "crs_details": {
                gps_crs.name: {
                    "crs": gps_crs.name,
                    "wkt": gps_crs.to_wkt(),
                }
            },
        }

        actual_json = test_position_dq.to_json()

        self.assertEqual(expected_json, actual_json)

    def test_to_json_output_formats_empty_list(self):
        """
        GIVEN output_formats is an empty list WHEN to_json() is called THEN output_formats is not included in the JSON
        """
        test_position_dq = PositionDataQuery(output_formats=[])
        gps_crs = CrsObject(4326)
        expected_json = {
            "title": "Position Data Query",
            "description": "Select data that is within a defined position.",
            "query_type": "position",
            "crs_details": {
                gps_crs.name: {
                    "crs": gps_crs.name,
                    "wkt": gps_crs.to_wkt(),
                }
            },
        }

        actual_json = test_position_dq.to_json()

        self.assertEqual(actual_json, expected_json)

    def test_from_json(self):
        """
        GIVEN a dict deserialised from valid JSON for a PositionDataQuery
        WHEN from_json() is called
        THEN a PositionDataQuery is returned with equivalent values
        """
        expected_adq = self.test_position_query

        actual_adq = PositionDataQuery.from_json(self.test_serialised_position_data_query)

        self.assertEqual(actual_adq, expected_adq)

    def test_from_json_empty_dict(self):
        """
        GIVEN an empty dictionary
        WHEN the empty dict is passed to from_json()
        THEN a PositionDataQuery with default values is returned
        """
        expected_position_dq = PositionDataQuery()

        actual_position_dq = PositionDataQuery.from_json({})

        self.assertEqual(actual_position_dq, expected_position_dq)

    def test_from_json_query_type_wrong(self):
        """
        GIVEN a dict where the query_type key is not "position"
        WHEN the dict is passed to from_json()
        THEN an InvalidEdrJsonError is raised
        """

        self.assertRaises(InvalidEdrJsonError, PositionDataQuery.from_json, {"query_type": "wrong!"})

    def test_from_json_query_type_missing(self):
        """
        GIVEN a JSON dict that doesn't have a "query_type" key
        WHEN the dict is passed to from_json()
        THEN a PositionDataQuery with equivalent values is returned
        """
        expected_position_dq = self.test_position_query
        test_json = self.test_serialised_position_data_query.copy()
        del test_json["query_type"]

        actual_position_dq = PositionDataQuery.from_json(test_json)

        self.assertEqual(actual_position_dq, expected_position_dq)

    def test_from_json_unexpected_key(self):
        """
        GIVEN a JSON dict that has all the expected keys with valid values
        AND an unexpected key
        WHEN the dict is passed to from_json()
        THEN an InvalidEdrJsonError is raised
        """
        test_json = self.test_serialised_position_data_query.copy()
        test_json["what the hell is this?"] = "12355"

        self.assertRaises(InvalidEdrJsonError, PositionDataQuery.from_json, test_json)


class RadiusDataQueryTest(unittest.TestCase):

    def setUp(self) -> None:
        test_title = "Radius Data Query"
        test_description = "This is a description that doesn't describe anything"
        test_output_formats = ["application/netcdf", "application/geo+json", "application/prs.coverage+json"]
        test_crs_details = [
            CrsObject(4326), CrsObject(4277), CrsObject(4188)
        ]
        test_within_units = ["m", "KM"]

        self.test_radius_query = RadiusDataQuery(
            test_title, test_description, test_output_formats, test_output_formats[0], test_crs_details,
            test_within_units
        )

        # According to
        # https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/8427963/standard/openapi/schemas/collections/radiusDataQuery.yaml
        # none of these fields are required, so they could all potentially be missing
        self.test_serialised_radius_data_query = {
            "title": test_title,
            "description": test_description,
            "query_type": "radius",
            "output_formats": test_output_formats,
            "default_output_format": test_output_formats[0],
            "crs_details": {crs.name: {"crs": crs.name, "wkt": crs.to_wkt()} for crs in test_crs_details},
            "within_units": test_within_units,
        }

    def test_init_defaults(self):
        """GIVEN no arguments are supplied WHEN a RadiusDataQuery is instantiated THEN default values are set"""
        actual_radius_dq = RadiusDataQuery()

        self.assertEqual("Radius Data Query", actual_radius_dq.title)
        self.assertEqual("Select data that is within a defined radius.", actual_radius_dq.description, )
        self.assertEqual(EdrDataQuery.RADIUS, actual_radius_dq.get_query_type())
        self.assertEqual([], actual_radius_dq.output_formats)
        self.assertEqual(None, actual_radius_dq.default_output_format)
        self.assertEqual([CrsObject(4326)], actual_radius_dq.crs_details)
        self.assertEqual([], actual_radius_dq.within_units)

    def test_init_default_output_format_inferred(self):
        """
        GIVEN output_formats is provided AND default_output_format is not
        WHEN a RadiusDataQuery is instantiated
        THEN default_output_format is inferred from the provided output_formats
        """
        test_output_formats = ["application/netcdf", "application/geo+json", "application/prs.coverage+json"]
        expected_default_output_format = test_output_formats[0]

        test_radius_dq = RadiusDataQuery(output_formats=test_output_formats)

        self.assertEqual(test_radius_dq.default_output_format, expected_default_output_format)

    def test__eq__(self):
        """GIVEN 2 RadiusDataQuery objects that have the same values WHEN they are compared THEN they are equal"""
        self.assertEqual(RadiusDataQuery(), RadiusDataQuery())

        rdq1 = RadiusDataQuery.from_json(self.test_serialised_radius_data_query)
        rdq2 = RadiusDataQuery.from_json(self.test_serialised_radius_data_query)
        self.assertEqual(rdq1, rdq2)

    def test__neq__(self):
        """
        GIVEN 2 RadiusDataQuery objects that have different values WHEN they are compared THEN they are not equal
        """
        self.assertNotEqual(self.test_radius_query, RadiusDataQuery())
        self.assertNotEqual(RadiusDataQuery(), AreaDataQuery())

    def test__neq__extra_fields(self):
        """
        This test checks that we've updated the equality comparison logic to include any attributes we've extended the
        class with

        GIVEN 2 RadiusDataQuery instances
        AND any attributes added to the class (i.e. those not defined by the superclass) differ
        AND inherited fields are the same
        WHEN they are compared
        THEN they are not equal
        """
        json2 = self.test_serialised_radius_data_query.copy()
        json2["within_units"] = ["Eiffel Towers"]
        cdq2 = RadiusDataQuery.from_json(json2)
        self.assertNotEqual(cdq2, self.test_radius_query)

    def test_to_json(self):
        """GIVEN a RadiusDataQuery WHEN to_json() is called THEN the expected JSON is produced"""
        expected_json = self.test_serialised_radius_data_query

        actual_json = self.test_radius_query.to_json()

        self.assertEqual(actual_json, expected_json)

    def test_to_json_defaults(self):
        """
        GIVEN a RadiusDataQuery created using default values
        WHEN to_json() is called
        THEN the expected JSON is produced
        """
        test_radius_dq = RadiusDataQuery()
        gps_crs = CrsObject(4326)
        expected_json = {
            "title": "Radius Data Query",
            "description": "Select data that is within a defined radius.",
            "query_type": "radius",
            "crs_details": {
                gps_crs.name: {
                    "crs": gps_crs.name,
                    "wkt": gps_crs.to_wkt(),
                }
            },
        }

        actual_json = test_radius_dq.to_json()

        self.assertEqual(expected_json, actual_json)

    def test_to_json_output_formats_empty_list(self):
        """
        GIVEN output_formats is an empty list WHEN to_json() is called THEN output_formats is not included in the JSON
        """
        test_radius_dq = RadiusDataQuery(output_formats=[])
        gps_crs = CrsObject(4326)
        expected_json = {
            "title": "Radius Data Query",
            "description": "Select data that is within a defined radius.",
            "query_type": "radius",
            "crs_details": {
                gps_crs.name: {
                    "crs": gps_crs.name,
                    "wkt": gps_crs.to_wkt(),
                }
            },
        }

        actual_json = test_radius_dq.to_json()

        self.assertEqual(expected_json, actual_json)

    def test_to_json_within_units_empty_list(self):
        """
        GIVEN within_units is an empty list WHEN to_json() is called THEN within_units is not included in the JSON
        """
        test_radius_dq = RadiusDataQuery(within_units=[])
        gps_crs = CrsObject(4326)
        expected_json = {
            "title": "Radius Data Query",
            "description": "Select data that is within a defined radius.",
            "query_type": "radius",
            "crs_details": {
                gps_crs.name: {
                    "crs": gps_crs.name,
                    "wkt": gps_crs.to_wkt(),
                }
            },
        }

        actual_json = test_radius_dq.to_json()

        self.assertEqual(expected_json, actual_json)

    def test_from_json(self):
        """
        GIVEN a dict deserialised from valid JSON for a RadiusDataQuery
        WHEN from_json() is called
        THEN a RadiusDataQuery is returned with equivalent values
        """
        expected_cdq = self.test_radius_query

        actual_cdq = RadiusDataQuery.from_json(self.test_serialised_radius_data_query)

        self.assertEqual(actual_cdq, expected_cdq)

    def test_from_json_empty_dict(self):
        """
        GIVEN an empty dictionary
        WHEN the empty dict is passed to from_json()
        THEN a RadiusDataQuery with default values is returned
        """
        expected_radius_dq = RadiusDataQuery()

        actual_radius_dq = RadiusDataQuery.from_json({})

        self.assertEqual(actual_radius_dq, expected_radius_dq)

    def test_from_json_query_type_wrong(self):
        """
        GIVEN a dict where the query_type key is not "radius"
        WHEN the dict is passed to from_json()
        THEN an InvalidEdrJsonError is raised
        """

        self.assertRaises(InvalidEdrJsonError, RadiusDataQuery.from_json, {"query_type": "wrong!"})

    def test_from_json_query_type_missing(self):
        """
        GIVEN a JSON dict that doesn't have a "query_type" key
        WHEN the dict is passed to from_json()
        THEN a RadiusDataQuery with equivalent values is returned
        """
        expected_radius_dq = self.test_radius_query
        test_json = self.test_serialised_radius_data_query.copy()
        del test_json["query_type"]

        actual_radius_dq = RadiusDataQuery.from_json(test_json)

        self.assertEqual(actual_radius_dq, expected_radius_dq)

    def test_from_json_unexpected_key(self):
        """
        GIVEN a JSON dict that has all the expected keys with valid values
        AND an unexpected key
        WHEN the dict is passed to from_json()
        THEN an InvalidEdrJsonError is raised
        """
        test_json = self.test_serialised_radius_data_query.copy()
        test_json["what the hell is this?"] = "12355"

        self.assertRaises(InvalidEdrJsonError, RadiusDataQuery.from_json, test_json)


class TrajectoryDataQueryTest(unittest.TestCase):

    def setUp(self) -> None:
        test_title = "Trajectory Data Query"
        test_description = "This is a description that doesn't describe anything"
        test_output_formats = ["application/netcdf", "application/geo+json", "application/prs.coverage+json"]
        test_crs_details = [CrsObject(4326), CrsObject(4277), CrsObject(4188)]

        self.test_trajectory_query = TrajectoryDataQuery(
            test_title, test_description, test_output_formats, test_output_formats[0], test_crs_details)

        # According to
        # https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/a0ab69d/standard/openapi/schemas/collections/trajectoryDataQuery.yaml
        # none of these fields are required, so they could all potentially be missing
        self.test_serialised_trajectory_data_query = {
            "title": test_title,
            "description": test_description,
            "query_type": "trajectory",
            "output_formats": test_output_formats,
            "default_output_format": test_output_formats[0],
            "crs_details": {
                crs.name: {"crs": crs.name, "wkt": crs.to_wkt()} for crs in test_crs_details
            }
        }

    def test_init_defaults(self):
        """GIVEN no arguments are supplied WHEN a TrajectoryDataQuery is instantiated THEN default values are set"""
        actual_trajectory_dq = TrajectoryDataQuery()

        self.assertEqual(actual_trajectory_dq.title, "Trajectory Data Query")
        self.assertEqual(actual_trajectory_dq.description, "Select data that is within a defined trajectory.")
        self.assertEqual(actual_trajectory_dq.get_query_type(), EdrDataQuery.TRAJECTORY)
        self.assertEqual(actual_trajectory_dq.output_formats, [])
        self.assertEqual(actual_trajectory_dq.default_output_format, None)
        self.assertEqual(actual_trajectory_dq.crs_details, [CrsObject(4326)])

    def test_init_default_output_format_inferred(self):
        """
        GIVEN output_formats is provided AND default_output_format is not
        WHEN a TrajectoryDataQuery is instantiated
        THEN default_output_format is inferred from the provided output_formats
        """
        test_output_formats = ["application/netcdf", "application/geo+json", "application/prs.coverage+json"]
        expected_default_output_format = test_output_formats[0]

        test_trajectory_dq = TrajectoryDataQuery(output_formats=test_output_formats)

        self.assertEqual(test_trajectory_dq.default_output_format, expected_default_output_format)

    def test__eq__(self):
        """GIVEN 2 TrajectoryDataQuery objects that have the same values WHEN they are compared THEN they are equal"""
        self.assertEqual(TrajectoryDataQuery(), TrajectoryDataQuery())

        adq1 = TrajectoryDataQuery.from_json(self.test_serialised_trajectory_data_query)
        adq2 = TrajectoryDataQuery.from_json(self.test_serialised_trajectory_data_query)
        self.assertEqual(adq1, adq2)

    def test__neq__(self):
        """
        GIVEN 2 TrajectoryDataQuery objects that have different values WHEN they are compared THEN they are not equal
        """
        self.assertNotEqual(self.test_trajectory_query, TrajectoryDataQuery())
        self.assertNotEqual(TrajectoryDataQuery(), CorridorDataQuery())

    def test_to_json(self):
        """GIVEN a TrajectoryDataQuery WHEN to_json() is called THEN the expected JSON is produced"""
        expected_json = self.test_serialised_trajectory_data_query

        actual_json = self.test_trajectory_query.to_json()

        self.assertEqual(actual_json, expected_json)

    def test_to_json_defaults(self):
        """
        GIVEN a TrajectoryDataQuery created using default values
        WHEN to_json() is called
        THEN the expected JSON is produced
        """
        test_trajectory_dq = TrajectoryDataQuery()
        gps_crs = CrsObject(4326)
        expected_json = {
            "title": "Trajectory Data Query",
            "description": "Select data that is within a defined trajectory.",
            "query_type": "trajectory",
            "crs_details": {
                gps_crs.name: {
                    "crs": gps_crs.name,
                    "wkt": gps_crs.to_wkt(),
                }
            },
        }

        actual_json = test_trajectory_dq.to_json()

        self.assertEqual(expected_json, actual_json)

    def test_to_json_output_formats_empty_list(self):
        """
        GIVEN output_formats is an empty list WHEN to_json() is called THEN output_formats is not included in the JSON
        """
        test_trajectory_dq = TrajectoryDataQuery(output_formats=[])
        gps_crs = CrsObject(4326)
        expected_json = {
            "title": "Trajectory Data Query",
            "description": "Select data that is within a defined trajectory.",
            "query_type": "trajectory",
            "crs_details": {
                gps_crs.name: {
                    "crs": gps_crs.name,
                    "wkt": gps_crs.to_wkt(),
                }
            },
        }

        actual_json = test_trajectory_dq.to_json()

        self.assertEqual(actual_json, expected_json)

    def test_from_json(self):
        """
        GIVEN a dict deserialised from valid JSON for a TrajectoryDataQuery
        WHEN from_json() is called
        THEN a TrajectoryDataQuery is returned with equivalent values
        """
        expected_adq = self.test_trajectory_query

        actual_adq = TrajectoryDataQuery.from_json(self.test_serialised_trajectory_data_query)

        self.assertEqual(actual_adq, expected_adq)

    def test_from_json_empty_dict(self):
        """
        GIVEN an empty dictionary
        WHEN the empty dict is passed to from_json()
        THEN a TrajectoryDataQuery with default values is returned
        """
        expected_trajectory_dq = TrajectoryDataQuery()

        actual_trajectory_dq = TrajectoryDataQuery.from_json({})

        self.assertEqual(actual_trajectory_dq, expected_trajectory_dq)

    def test_from_json_query_type_wrong(self):
        """
        GIVEN a dict where the query_type key is not "trajectory"
        WHEN the dict is passed to from_json()
        THEN an InvalidEdrJsonError is raised
        """

        self.assertRaises(InvalidEdrJsonError, TrajectoryDataQuery.from_json, {"query_type": "wrong!"})

    def test_from_json_query_type_missing(self):
        """
        GIVEN a JSON dict that doesn't have a "query_type" key
        WHEN the dict is passed to from_json()
        THEN a TrajectoryDataQuery with equivalent values is returned
        """
        expected_trajectory_dq = self.test_trajectory_query
        test_json = self.test_serialised_trajectory_data_query.copy()
        del test_json["query_type"]

        actual_trajectory_dq = TrajectoryDataQuery.from_json(test_json)

        self.assertEqual(actual_trajectory_dq, expected_trajectory_dq)

    def test_from_json_unexpected_key(self):
        """
        GIVEN a JSON dict that has all the expected keys with valid values
        AND an unexpected key
        WHEN the dict is passed to from_json()
        THEN an InvalidEdrJsonError is raised
        """
        test_json = self.test_serialised_trajectory_data_query.copy()
        test_json["what the hell is this?"] = "12355"

        self.assertRaises(InvalidEdrJsonError, TrajectoryDataQuery.from_json, test_json)


class DataQueryLinkTest(unittest.TestCase):

    def setUp(self) -> None:
        test_position_data_query = PositionDataQuery("Test Query")
        self.test_dql = DataQueryLink(
            URL("https://localhost"), "alternate", test_position_data_query, "text", "en", "Test Link", 42)

        self.test_json = {
            "title": "Test Link",
            "href": "https://localhost",
            "rel": "alternate",
            "type": "text",
            "hreflang": "en",
            "length": 42,
            "templated": True,
            "variables": test_position_data_query.to_json(),
        }

    def test__eq__(self):
        """
        GIVEN 2 different DataQueryLink instances that hold the same data
        WHEN they are compared
        THEN True is returned
        """
        dql1 = DataQueryLink(
            URL("http://localhost"), "test", PositionDataQuery("test query"), "test", "en", "Test Link", 1)
        dql2 = DataQueryLink(
            URL("http://localhost"), "test", PositionDataQuery("test query"), "test", "en", "Test Link", 1)

        self.assertEqual(dql1, dql2)

    def test__eq__with_different_data_queries(self):
        """
        GIVEN 2 DataQueryLinks that differ only by the Data Query stored in DataQueryLink.variables
        WHEN they are compared
        THEN False is returned
        """
        dql1 = DataQueryLink(
            URL("https://localhost"), "test", PositionDataQuery("test query"), "test", "en", "Test Link", 1)
        dql2 = DataQueryLink(URL("https://localhost"), "test", PositionDataQuery("test query"))

        self.assertNotEqual(dql1, dql2)

    def test_from_json_all_fields(self):
        """
        GIVEN a JSON dict with all the possible acceptable fields
        WHEN from_json is called
        THEN the corresponding object is returned
        """
        expected = self.test_dql

        actual = DataQueryLink.from_json(self.test_json)

        self.assertEqual(expected, actual)

    def test_from_json_required_fields_only(self):
        """
        GIVEN a JSON dict that only contains mandatory fields
        WHEN from_json is called
        THEN the corresponding object is returned
        """
        test_json = {
            "href": URL("https://localhost"),
            "rel": "test",
        }
        expected = DataQueryLink(URL("https://localhost"), "test")

        actual = DataQueryLink.from_json(test_json)

        self.assertEqual(expected, actual)

    def test_from_json_unexpected_field(self):
        """
        GIVEN a JSON dict that contains the mandatory fields
        AND an unexpected field
        WHEN from_json is called
        THEN an InvalidEdrJsonError is raised
        """
        self.test_json["what's this?"] = None
        self.assertRaises(InvalidEdrJsonError, DataQueryLink.from_json, self.test_json)

    def test_from_json_area_data_query(self):
        """
        GIVEN a DataQueryLink JSON dict with an embedded AreaDataQuery
        WHEN from_json is called
        THEN the correct objects are returned
        """
        test_area_query = AreaDataQuery("Area Q", "test an area query", ["application/netcdf"])
        self.test_json["variables"] = test_area_query.to_json()
        self.test_dql.variables = test_area_query

        actual = DataQueryLink.from_json(self.test_json)

        self.assertEqual(self.test_dql, actual)

    def test_from_json_corridor_data_query(self):
        """
        GIVEN a DataQueryLink JSON dict with an embedded CorridorDataQuery
        WHEN from_json is called
        THEN the correct objects are returned
        """
        test_corridor_query = CorridorDataQuery(
            "Corridor Q", "test an area query", ["application/netcdf"], width_units=["m", "km"], height_units=["hPa"])
        self.test_json["variables"] = test_corridor_query.to_json()
        self.test_dql.variables = test_corridor_query

        actual = DataQueryLink.from_json(self.test_json)

        self.assertEqual(self.test_dql, actual)

    def test_from_json_items_data_query(self):
        """
        GIVEN a DataQueryLink JSON dict with an embedded ItemsDataQuery
        WHEN from_json is called
        THEN the correct objects are returned
        """
        test_items_query = ItemsDataQuery("Items Q", "test an area query")
        self.test_json["variables"] = test_items_query.to_json()
        self.test_dql.variables = test_items_query

        actual = DataQueryLink.from_json(self.test_json)

        self.assertEqual(self.test_dql, actual)

    def test_from_json_cube_data_query(self):
        """
        GIVEN a DataQueryLink JSON dict with an embedded CubeDataQuery
        WHEN from_json is called
        THEN the correct objects are returned
        """
        test_cube_query = CubeDataQuery(
            "Cube Q", "test an area query", ["application/netcdf"], height_units=["km", "mi"])
        self.test_json["variables"] = test_cube_query.to_json()
        self.test_dql.variables = test_cube_query

        actual = DataQueryLink.from_json(self.test_json)

        self.assertEqual(self.test_dql, actual)

    def test_from_json_locations_data_query(self):
        """
        GIVEN a DataQueryLink JSON dict with an embedded LocationsDataQuery
        WHEN from_json is called
        THEN the correct objects are returned
        """
        test_locations_query = LocationsDataQuery("Locations Q", "test an area query", ["application/netcdf"])
        self.test_json["variables"] = test_locations_query.to_json()
        self.test_dql.variables = test_locations_query

        actual = DataQueryLink.from_json(self.test_json)

        self.assertEqual(self.test_dql, actual)

    def test_from_json_position_data_query(self):
        """
        GIVEN a DataQueryLink JSON dict with an embedded PositionDataQuery
        WHEN from_json is called
        THEN the correct objects are returned
        """
        test_position_query = PositionDataQuery("Position Q", "test an area query", ["application/netcdf"])
        self.test_json["variables"] = test_position_query.to_json()
        self.test_dql.variables = test_position_query

        actual = DataQueryLink.from_json(self.test_json)

        self.assertEqual(self.test_dql, actual)

    def test_from_json_radius_data_query(self):
        """
        GIVEN a DataQueryLink JSON dict with an embedded RadiusDataQuery
        WHEN from_json is called
        THEN the correct objects are returned
        """
        test_radius_query = RadiusDataQuery(
            "Radius Q", "test an area query", ["application/netcdf"], within_units=["m", "km"])
        self.test_json["variables"] = test_radius_query.to_json()
        self.test_dql.variables = test_radius_query

        actual = DataQueryLink.from_json(self.test_json)

        self.assertEqual(self.test_dql, actual)

    def test_from_json_trajectory_data_query(self):
        """
        GIVEN a DataQueryLink JSON dict with an embedded TrajectoryDataQuery
        WHEN from_json is called
        THEN the correct objects are returned
        """
        test_trajectory_query = TrajectoryDataQuery("Trajectory Q", "test an area query", ["application/netcdf"])
        self.test_json["variables"] = test_trajectory_query.to_json()
        self.test_dql.variables = test_trajectory_query

        actual = DataQueryLink.from_json(self.test_json)

        self.assertEqual(self.test_dql, actual)

    def test_to_json_all_fields(self):
        """GIVEN a DataQueryLink with all fields set WHEN to_json is called THEN the correct JSON dict is produced"""
        self.assertEqual(self.test_json, self.test_dql.to_json())

    def test_to_json_variables_not_set(self):
        """
        GIVEN a DataQueryLink with all fields set except variables
        WHEN to_json is called
        THEN the correct JSON dict is produced

        Specifically, we only expect the "templated" field to be included if variables is provided, and omitted if
        variables is not provided
        """
        del self.test_json["variables"]
        del self.test_json["templated"]

        test_dql = DataQueryLink(
            self.test_dql.href, self.test_dql.rel, None, self.test_dql.type, self.test_dql.hreflang,
            self.test_dql.title, self.test_dql.length
        )

        actual = test_dql.to_json()

        self.assertEqual(self.test_json, actual)

    def test_to_json_required_fields_only(self):
        """
        GIVEN a DataQueryLink with only mandatory fields set
        WHEN to_json is called
        THEN the correct JSON dict is produced
        """
        test_dql = DataQueryLink(URL("https://localhost"), "alternate")
        expected_json = {
            "href": "https://localhost",
            "rel": "alternate",
        }

        actual = test_dql.to_json()

        self.assertEqual(expected_json, actual)

    def test_to_json_area_data_query(self):
        """
        GIVEN a DataQueryLink instance with an embedded AreaDataQuery
        WHEN to_json is called
        THEN the correct JSON dict is returned
        """
        test_area_query = AreaDataQuery("Area Q", "test an area query", ["application/netcdf"])
        self.test_dql.variables = test_area_query
        self.test_json["variables"] = test_area_query.to_json()

        actual = self.test_dql.to_json()

        self.assertEqual(self.test_json, actual)

    def test_to_json_corridor_data_query(self):
        """
        GIVEN a DataQueryLink instance with an embedded CorridorDataQuery
        WHEN to_json is called
        THEN the correct JSON dict is returned
        """
        test_corridor_query = CorridorDataQuery(
            "Corridor Q", "test an corridor query", ["application/netcdf"], width_units=["m"], height_units=["m"])
        self.test_dql.variables = test_corridor_query
        self.test_json["variables"] = test_corridor_query.to_json()

        actual = self.test_dql.to_json()

        self.assertEqual(self.test_json, actual)

    def test_to_json_items_data_query(self):
        """
        GIVEN a DataQueryLink instance with an embedded ItemsDataQuery
        WHEN to_json is called
        THEN the correct JSON dict is returned
        """
        test_items_query = ItemsDataQuery("Items Q", "test an items query")
        self.test_dql.variables = test_items_query
        self.test_json["variables"] = test_items_query.to_json()

        actual = self.test_dql.to_json()

        self.assertEqual(self.test_json, actual)

    def test_to_json_cube_data_query(self):
        """
        GIVEN a DataQueryLink instance with an embedded CubeDataQuery
        WHEN to_json is called
        THEN the correct JSON dict is returned
        """
        test_cube_query = CubeDataQuery(
            "Cube Q", "test an cube query", ["application/netcdf"], height_units=["km", "mi"])
        self.test_dql.variables = test_cube_query
        self.test_json["variables"] = test_cube_query.to_json()

        actual = self.test_dql.to_json()

        self.assertEqual(self.test_json, actual)

    def test_to_json_locations_data_query(self):
        """
        GIVEN a DataQueryLink instance with an embedded LocationsDataQuery
        WHEN to_json is called
        THEN the correct JSON dict is returned
        """
        test_locations_query = LocationsDataQuery("Locations Q", "test an locations query", ["application/netcdf"])
        self.test_dql.variables = test_locations_query
        self.test_json["variables"] = test_locations_query.to_json()

        actual = self.test_dql.to_json()

        self.assertEqual(self.test_json, actual)

    def test_to_json_position_data_query(self):
        """
        GIVEN a DataQueryLink instance with an embedded PositionDataQuery
        WHEN to_json is called
        THEN the correct JSON dict is returned
        """
        test_position_query = PositionDataQuery("Position Q", "test an position query", ["application/netcdf"])
        self.test_dql.variables = test_position_query
        self.test_json["variables"] = test_position_query.to_json()

        actual = self.test_dql.to_json()

        self.assertEqual(self.test_json, actual)

    def test_to_json_radius_data_query(self):
        """
        GIVEN a DataQueryLink instance with an embedded RadiusDataQuery
        WHEN to_json is called
        THEN the correct JSON dict is returned
        """
        test_radius_query = RadiusDataQuery(
            "Radius Q", "test an radius query", ["application/netcdf"], within_units=["m", "ft"])
        self.test_dql.variables = test_radius_query
        self.test_json["variables"] = test_radius_query.to_json()

        actual = self.test_dql.to_json()

        self.assertEqual(self.test_json, actual)

    def test_to_json_trajectory_data_query(self):
        """
        GIVEN a DataQueryLink instance with an embedded TrajectoryDataQuery
        WHEN to_json is called
        THEN the correct JSON dict is returned
        """
        test_trajectory_query = TrajectoryDataQuery("Trajectory Q", "test an trajectory query", ["application/netcdf"])
        self.test_dql.variables = test_trajectory_query
        self.test_json["variables"] = test_trajectory_query.to_json()

        actual = self.test_dql.to_json()

        self.assertEqual(self.test_json, actual)

    def test_templated_variables_set(self):
        """
        GIVEN a DataQueryLink with a value for `variables`
        WHEN the `templated` property is accessed
        THEN True is returned
        """
        self.assertIsNotNone(self.test_dql.variables)  # Just to check we have the expected test state
        self.assertTrue(self.test_dql.templated)

    def test_templated_variables_unset(self):
        """
        GIVEN a DataQueryLink that has `variables` unset
        WHEN the `templated` property is accessed
        THEN False is returned
        """
        self.test_dql.variables = None
        self.assertFalse(self.test_dql.templated)


class DataQueryMapTest(unittest.TestCase):

    def test_is_dict(self):
        self.assertIsInstance(DATA_QUERY_MAP, dict)

    def test_expected_keys(self):
        expected_keys = {dq.value for dq in EdrDataQuery}
        actual_keys = set(DATA_QUERY_MAP.keys())
        self.assertEqual(expected_keys, actual_keys)

    def test_area(self):
        self.assertEqual(AreaDataQuery, DATA_QUERY_MAP["area"])

    def test_corridor(self):
        self.assertEqual(CorridorDataQuery, DATA_QUERY_MAP["corridor"])

    def test_items(self):
        self.assertEqual(ItemsDataQuery, DATA_QUERY_MAP["items"])

    def test_cube(self):
        self.assertEqual(CubeDataQuery, DATA_QUERY_MAP["cube"])

    def test_locations(self):
        self.assertEqual(LocationsDataQuery, DATA_QUERY_MAP["locations"])

    def test_position(self):
        self.assertEqual(PositionDataQuery, DATA_QUERY_MAP["position"])

    def test_radius(self):
        self.assertEqual(RadiusDataQuery, DATA_QUERY_MAP["radius"])

    def test_trajectory(self):
        self.assertEqual(TrajectoryDataQuery, DATA_QUERY_MAP["trajectory"])
