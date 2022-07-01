import unittest

from edr_server.core.exceptions import InvalidEdrJsonError
from edr_server.core.models import EdrDataQuery
from edr_server.core.models.crs import CrsObject
from edr_server.core.models.links import AreaDataQuery


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
            "crs_details": [{
                "crs": crs.name,
                "wkt": crs.to_wkt(),
            } for crs in test_crs_details]
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
        gsp_crs = CrsObject(4326)
        expected_json = {
            "title": "Area Data Query",
            "description": "Query to return data for a defined area",
            "query_type": "area",
            "crs_details": [{
                "crs": gsp_crs.name,
                "wkt": gsp_crs.to_wkt(),
            }]
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
            "crs_details": [{
                "crs": gps_crs.name,
                "wkt": gps_crs.to_wkt(),
            }]
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
