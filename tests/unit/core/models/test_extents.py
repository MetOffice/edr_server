import unittest
from datetime import datetime, timedelta
from shapely.geometry import Polygon
import numpy as np

from edr_server.core.models.extents import TemporalExtent, SpatialExtent, VerticalExtent
from edr_server.core.models.time import DateTimeInterval, Duration
from edr_server.core.models.crs import CrsObject


class TemporalExtentTest(unittest.TestCase):

    def test_bounds_no_values(self):
        """
        GIVEN a TemporalExtent with neither datetimes or DateTimeIntervals (meaning TemporalExtent.values and
              TemporalExtent.intervals will both be empty lists)
        WHEN TemporalExtent.bounds is called
        THEN (None, None) is returned
        """
        self.assertEqual((None, None), TemporalExtent().bounds)

    def test_bounds_datetime_single(self):
        """
        GIVEN a TemporalExtent that contains a single datetime
        WHEN TemporalExtent.bounds is accessed
        THEN the result is consistent with that datetime
        """
        dt = datetime.now()
        expected_bounds = dt, dt

        extent = TemporalExtent(values=[dt])

        self.assertEqual(expected_bounds, extent.bounds)

    def test_bounds_datetime_multiple(self):
        """
        GIVEN a TemporalExtent that contains multiple datetime
        WHEN TemporalExtent.bounds is accessed
        THEN the result contains the earliest and latest datetimes
        """
        min_dt = datetime(2020, 1, 1)
        values = [min_dt + timedelta(days=n) for n in range(0, 365)]
        max_dt = values[-1]
        expected_bounds = min_dt, max_dt

        extent = TemporalExtent(values=values)

        self.assertEqual(expected_bounds, extent.bounds)

    def test_bounds_datetime_multiple_unsorted(self):
        """
        GIVEN a TemporalExtent that contains multiple datetimes
        AND the datetimes are unsorted
        WHEN TemporalExtent.bounds is accessed
        THEN the result contains the earliest and latest datetimes

        Explicitly testing an unsorted list to make it clear we don't assume the list is ordered
        """
        min_dt = datetime(2020, 1, 1)
        max_dt = datetime(2020, 12, 31)
        expected_bounds = min_dt, max_dt
        # ok, this is technically just reversed, but it's good enough to test that we don't just assume ascending order
        values = [min_dt + timedelta(days=n) for n in range(0, 366)][::-1]

        extent = TemporalExtent(values=values)

        self.assertEqual(expected_bounds, extent.bounds)

    def test_bounds_dti_single(self):
        """
        GIVEN a TemporalExtent that contains a DateTimeInterval
        WHEN TemporalExtent.bounds is accessed
        THEN the result corresponds to the start and end of that DateTimeInterval
        """
        dti = DateTimeInterval(datetime(2020, 1, 1), datetime(2020, 12, 30))
        expected_bounds = dti.start, dti.end

        extent = TemporalExtent(intervals=[dti])

        self.assertEqual(expected_bounds, extent.bounds)

    def test_bounds_dti_single_open_lower_bound(self):
        """
        GIVEN a TemporalExtent that contains a DateTimeInterval
        AND that DateTimeInterval has an open start date (i.e. DateTimeInterval.start is None)
        WHEN TemporalExtent.bounds is accessed
        THEN the result corresponds to the start and end of that DateTimeInterval
        """
        dti = DateTimeInterval(
            end=datetime(2020, 12, 30), duration=Duration(days=1), recurrences=DateTimeInterval.INFINITE_RECURRENCES)
        expected_bounds = None, dti.end

        extent = TemporalExtent(intervals=[dti])

        self.assertEqual(expected_bounds, extent.bounds)

    def test_bounds_dti_single_open_upper_bound(self):
        """
        GIVEN a TemporalExtent that contains a DateTimeInterval
        AND that DateTimeInterval has an open end date (i.e. DateTimeInterval.end is None)
        WHEN TemporalExtent.bounds is accessed
        THEN the result corresponds to the start and end of that DateTimeInterval
        """
        dti = DateTimeInterval(start=datetime(2020, 12, 30), duration=Duration(days=1),
                               recurrences=DateTimeInterval.INFINITE_RECURRENCES)
        expected_bounds = dti.start, None

        extent = TemporalExtent(intervals=[dti])

        self.assertEqual(expected_bounds, extent.bounds)

    def test_bounds_dti_multiple(self):
        """
        GIVEN a TemporalExtent that contains multiple DateTimeIntervals
        WHEN TemporalExtent.bounds is accessed
        THEN the result corresponds to the start and end of that DateTimeInterval
        """
        start = datetime(2020, 12, 30)
        middle = start + timedelta(days=1)
        end = middle + timedelta(days=1)
        dti1 = DateTimeInterval(start=start, end=middle)
        dti2 = DateTimeInterval(start=middle, end=end)
        expected_bounds = start, end

        # Deliberately putting the later dti before the earlier one
        # to test that the behaviour doesn't depend on items being in sorted order
        extent = TemporalExtent(intervals=[dti2, dti1])

        self.assertEqual(expected_bounds, extent.bounds)

    def test_bounds_dti_multiple_open_lower_bound(self):
        """
        GIVEN a TemporalExtent that contains multiple DateTimeIntervals
        AND at least one DateTimeInterval has an open start date (i.e. DateTimeInterval.start is None)
        WHEN TemporalExtent.bounds is accessed
        THEN the result contains None and the value of the latest end date
        """
        start = datetime(2020, 12, 30)
        dti1 = DateTimeInterval(start=start, duration=Duration(days=1))
        dti2 = DateTimeInterval(end=dti1.end, duration=Duration(days=2),
                                recurrences=DateTimeInterval.INFINITE_RECURRENCES)
        dti3 = DateTimeInterval(datetime(2020, 1, 1), datetime(2020, 2, 1))

        expected_bounds = None, dti1.end

        # There's deliberate overlap with the DateTimeIntervals
        extent = TemporalExtent(intervals=[dti1, dti2, dti3])

        self.assertEqual(expected_bounds, extent.bounds)

    def test_bounds_dti_multiple_open_upper_bound(self):
        """
        GIVEN a TemporalExtent that contains multiple DateTimeIntervals
        AND at least one DateTimeInterval has an open end date (i.e. DateTimeInterval.end is None)
        WHEN TemporalExtent.bounds is accessed
        THEN the result contains the value of the earliest start date and None
        """
        dti1 = DateTimeInterval(start=datetime(
            2020, 12, 30), duration=Duration(days=1))
        dti2 = DateTimeInterval(start=dti1.end, duration=Duration(days=2),
                                recurrences=DateTimeInterval.INFINITE_RECURRENCES)
        dti3 = DateTimeInterval(datetime(2020, 1, 1), datetime(2020, 2, 1))

        expected_bounds = dti3.start, None

        # There's deliberate overlap with the DateTimeIntervals, as this should be supported
        extent = TemporalExtent(intervals=[dti1, dti2, dti3])

        self.assertEqual(expected_bounds, extent.bounds)

    def test_bounds_mixed_min_max_are_datetimes(self):
        """
        GIVEN a TemporalExtent that contains a mix of datetimes and DateTimeIntervals
        AND the bounds of the extent are both given by datetimes (rather than properties of DateTimeIntervals)
        WHEN TemporalExtent.bounds is accessed
        THEN the result contains the values of those datetimes
        """
        datetimes = [datetime(2019, 12, 1) + timedelta(weeks=n * 52)
                     for n in range(5)]
        dti1 = DateTimeInterval(start=datetime(
            2020, 12, 30), duration=Duration(days=1))
        dti2 = DateTimeInterval(start=dti1.end, duration=Duration(days=2))
        dti3 = DateTimeInterval(datetime(2020, 1, 1), datetime(2020, 2, 1))

        expected_bounds = datetimes[0], datetimes[-1]

        # There's deliberate overlap with the DateTimeIntervals, as this should be supported
        extent = TemporalExtent(values=datetimes, intervals=[dti1, dti2, dti3])

        self.assertEqual(expected_bounds, extent.bounds)

    def test_bounds_mixed_min_max_are_datetimeintervals(self):
        """
        GIVEN a TemporalExtent that contains a mix of datetimes and DateTimeIntervals
        AND the bounds of the extent are both given by the start & end properties of different DateTimeIntervals
        WHEN TemporalExtent.bounds is accessed
        THEN the result contains the start value of the earliest DateTimeInterval and end value of the latest
             DateTimeInterval
        """
        datetimes = [datetime(2019, 12, 1) + timedelta(weeks=n * 52)
                     for n in range(5)]
        dti1 = DateTimeInterval(end=datetimes[0], duration=Duration(days=1))
        dti2 = DateTimeInterval(start=datetimes[-1], duration=Duration(days=2))
        dti3 = DateTimeInterval(datetime(2020, 1, 1), datetime(2020, 2, 1))

        expected_bounds = dti1.start, dti2.end

        # There's deliberate overlap with the DateTimeIntervals, as this should be supported
        extent = TemporalExtent(values=datetimes, intervals=[dti1, dti2, dti3])

        self.assertEqual(expected_bounds, extent.bounds)

    def test_bounds_mixed_min_is_datetime_max_is_dti(self):
        """
        GIVEN a TemporalExtent that contains a mix of datetimes and DateTimeIntervals
        AND the lower bound is a datetime
        AND the upper bound is the end date of a DateTimeInterval
        WHEN TemporalExtent.bounds is accessed
        THEN the result contains the earliest datetime and end value of the latest
             DateTimeInterval
        """
        datetimes = [datetime(2019, 12, 1) + timedelta(weeks=n * 52)
                     for n in range(5)]
        dti1 = DateTimeInterval(start=datetime(
            2020, 12, 30), duration=Duration(days=1))
        dti2 = DateTimeInterval(end=datetimes[-1], duration=Duration(days=2))
        dti3 = DateTimeInterval(datetime(2020, 1, 1), datetime(2020, 2, 1))

        expected_bounds = datetimes[0], dti2.end

        # There's deliberate overlap with the DateTimeIntervals, as this should be supported
        extent = TemporalExtent(values=datetimes, intervals=[dti1, dti2, dti3])

        self.assertEqual(expected_bounds, extent.bounds)

    def test_bounds_mixed_min_is_datetime_max_is_unbounded_dti(self):
        """
        GIVEN a TemporalExtent that contains a mix of datetimes and DateTimeIntervals
        AND the lower bound is a datetime
        AND the upper bound is an unbounded DateTimeInterval
        WHEN TemporalExtent.bounds is accessed
        THEN the result contains the earliest datetime and None
        """
        datetimes = [datetime(2019, 12, 1) + timedelta(weeks=n * 52)
                     for n in range(5)]
        dti1 = DateTimeInterval(start=datetime(2020, 12, 30), duration=Duration(days=1),
                                recurrences=DateTimeInterval.INFINITE_RECURRENCES)
        dti2 = DateTimeInterval(end=datetimes[-1], duration=Duration(days=2))
        dti3 = DateTimeInterval(datetime(2020, 1, 1), datetime(2020, 2, 1))

        expected_bounds = datetimes[0], None

        # There's deliberate overlap with the DateTimeIntervals, as this should be supported
        extent = TemporalExtent(values=datetimes, intervals=[dti1, dti2, dti3])

        self.assertEqual(expected_bounds, extent.bounds)

    def test_bounds_mixed_min_is_dti_max_is_datetime(self):
        """
        GIVEN a TemporalExtent that contains a mix of datetimes and DateTimeIntervals
        AND the lower bound is the start date of a DateTimeInterval
        AND the upper bound is a datetime
        WHEN TemporalExtent.bounds is accessed
        THEN the result contains the start value of the earliest DateTimeInterval and the latest datetime
        """
        datetimes = [datetime(2020, 12, 1) + timedelta(weeks=n * 52)
                     for n in range(5)]
        dti1 = DateTimeInterval(start=datetime(
            2020, 12, 30), duration=Duration(days=1))
        dti2 = DateTimeInterval(start=dti1.end, duration=Duration(days=2))
        dti3 = DateTimeInterval(datetime(2020, 1, 1), datetime(2020, 2, 1))

        expected_bounds = dti3.start, datetimes[-1]

        # There's deliberate overlap with the DateTimeIntervals, as this should be supported
        extent = TemporalExtent(values=datetimes, intervals=[dti1, dti2, dti3])

        self.assertEqual(expected_bounds, extent.bounds)

    def test_bounds_mixed_min_is_unbounded_dti_max_is_datetime(self):
        """
        GIVEN a TemporalExtent that contains a mix of datetimes and DateTimeIntervals
        AND the lower bound is an unbounded DateTimeInterval
        AND the upper bound is a datetime
        WHEN TemporalExtent.bounds is accessed
        THEN the result contains None and the latest datetime
        """
        datetimes = [datetime(2019, 12, 1) + timedelta(weeks=n * 52)
                     for n in range(5)]
        dti1 = DateTimeInterval(end=datetime(2020, 12, 30), duration=Duration(days=1),
                                recurrences=DateTimeInterval.INFINITE_RECURRENCES)
        dti2 = DateTimeInterval(start=dti1.end, duration=Duration(days=2))
        dti3 = DateTimeInterval(datetime(2020, 1, 1), datetime(2020, 2, 1))

        expected_bounds = None, datetimes[-1]

        # There's deliberate overlap with the DateTimeIntervals, as this should be supported
        extent = TemporalExtent(values=datetimes, intervals=[dti1, dti2, dti3])

        self.assertEqual(expected_bounds, extent.bounds)

    def test_bounds_mixed_min_and_max_are_same_unbounded_dti(self):
        """
        GIVEN a TemporalExtent that contains a mix of datetimes and DateTimeIntervals
        AND one of the DateTimeIntervals is unbounded for both upper and lower bounds
        WHEN TemporalExtent.bounds is accessed
        THEN the result contains None for both upper and lower bounds

        Explicitly testing the case where a single DateTimeInterval provides both the upper and lower bound
        """
        datetimes = [datetime(2019, 12, 1) + timedelta(weeks=n * 52)
                     for n in range(5)]
        # DateTimeInterval with only a duration and infinite recurrences implies unbounded lower and upper bounds
        dti1 = DateTimeInterval(duration=Duration(
            days=1), recurrences=DateTimeInterval.INFINITE_RECURRENCES)
        dti2 = DateTimeInterval(start=dti1.end, duration=Duration(days=2))
        dti3 = DateTimeInterval(datetime(2020, 1, 1), datetime(2020, 2, 1))

        expected_bounds = None, None

        # There's deliberate overlap with the DateTimeIntervals, as this should be supported
        extent = TemporalExtent(values=datetimes, intervals=[dti1, dti2, dti3])

        self.assertEqual(expected_bounds, extent.bounds)

    def test_bounds_mixed_min_and_max_are_same_dti(self):
        """
        GIVEN a TemporalExtent that contains a mix of datetimes and DateTimeIntervals
        AND one of the DateTimeIntervals has both the earliest start datetime and latest end datetime
        WHEN TemporalExtent.bounds is accessed
        THEN the result contains the values from that DateTimeInterval

        Explicitly testing the case where a single DateTimeInterval provides both the upper and lower bound
        """
        datetimes = [datetime(2019, 12, 1) + timedelta(weeks=n * 52)
                     for n in range(5)]
        # DateTimeInterval with only a duration and infinite recurrences implies unbounded lower and upper bounds
        dti1 = DateTimeInterval(start=datetimes[0] - timedelta(days=1),
                                end=datetimes[-1] + timedelta(days=1))
        dti2 = DateTimeInterval(
            start=datetimes[0] + timedelta(days=1), duration=Duration(days=2))
        dti3 = DateTimeInterval(datetime(2020, 1, 1), datetime(2020, 2, 1))

        expected_bounds = dti1.start, dti1.end

        # There's deliberate overlap with the DateTimeIntervals, as this should be supported
        extent = TemporalExtent(values=datetimes, intervals=[dti1, dti2, dti3])

        self.assertEqual(expected_bounds, extent.bounds)

    def test_init_type_checking_values(self):
        """
        GIVEN a non-list
        WHEN passed to TemporalExtent.values
        THEN a TypeError is returned
        Added due to https://metoffice.atlassian.net/browse/CAP-364
        """
        datetimes = {"value": datetime(2019, 12, 1)}

        with self.assertRaisesRegex(TypeError, "Expected List of values, received <class 'dict'>"):
            TemporalExtent(values=datetimes)

    def test_init_type_checking_intervals(self):
        """
        GIVEN a non-list
        WHEN passed to TemporalExtent.intervals
        THEN a TypeError is returned
        Added due to https://metoffice.atlassian.net/browse/CAP-364
        """
        dti = DateTimeInterval(datetime(2020, 1, 1), datetime(2020, 12, 30))

        with self.assertRaisesRegex(TypeError,
                                    "Expected List of intervals, received <class 'edr_server.core.models.time.DateTimeInterval'>"):
            TemporalExtent(intervals=dti)

    def test_init_type_checking_values_entry(self):
        """
        GIVEN a list of datetimes with one bad entry
        WHEN passed to TemporalExtent.values
        THEN a TypeError is returned with value and type
        Added due to https://metoffice.atlassian.net/browse/CAP-364
        """
        datetimes = [datetime(2019, 12, 1) + timedelta(weeks=n * 52)
                     for n in range(5)]
        dti = [DateTimeInterval(datetime(2020, 1, 1), datetime(2020, 12, 30))]
        datetimes.append(1)

        with self.assertRaisesRegex(TypeError, "Expected all datetime values, received value '1' of type <class 'int'>"):
            TemporalExtent(values=datetimes, intervals=dti)

    def test_init_type_checking_intervals_entry(self):
        """
        GIVEN a list of DatetimeIntervals with one bad entry
        WHEN passed to TemporalExtent.intervals
        THEN a TypeError is returned with value and type
        Added due to https://metoffice.atlassian.net/browse/CAP-364
        """
        datetimes = [datetime(2019, 12, 1) + timedelta(weeks=n * 52)
                     for n in range(5)]
        dti1 = DateTimeInterval(datetime(2020, 1, 1), datetime(2020, 12, 30))
        dti2 = datetime(2021, 1, 1)

        with self.assertRaisesRegex(TypeError,
                                    "Expected all DateTimeIntervals, received value '2021-01-01 00:00:00' of type <class 'datetime.datetime'>"):
            TemporalExtent(values=datetimes, intervals=[dti1, dti2])

    def test_init_type_checking_trs(self):
        """
        GIVEN a non-CrsObject input
        WHEN passed to TemporalExtent
        THEN a TypeError is returned
        Added due to https://metoffice.atlassian.net/browse/CAP-364
        """
        datetimes = [datetime(2019, 12, 1) + timedelta(weeks=n * 52)
                     for n in range(5)]
        input = "bad input"

        with self.assertRaisesRegex(TypeError, "Expected CrsObject, received <class 'str'>"):
            TemporalExtent(values=datetimes, trs=input)


class SpatialExtentTest(unittest.TestCase):

    def test_init_type_checking_bbox(self):
        """
        GIVEN a non-polygon input
        WHEN passed to SpatialExtent
        THEN a TypeError is returned
        Added due to https://metoffice.atlassian.net/browse/CAP-361
        """
        input = "bad input"

        with self.assertRaisesRegex(TypeError, "Expected polygon, received <class 'str'>"):
            SpatialExtent(input)

    def test_init_type_checking_crs(self):
        """
        GIVEN a non-CrsObject input
        WHEN passed to SpatialExtent
        THEN a TypeError is returned
        Added due to https://metoffice.atlassian.net/browse/CAP-362
        """
        poly = Polygon([[0, 0], [1, 0], [1, 1]])
        input = "bad input"

        with self.assertRaisesRegex(TypeError, "Expected CrsObject, received <class 'str'>"):
            SpatialExtent(poly, input)


class VerticalExtentTest(unittest.TestCase):

    def test_from_json(self):
        """
        GIVEN a typical json_dict
        WHEN from_json is called
        THEN a VerticalExtent is returned
        """
        expected = VerticalExtent([1.65])

        json_dict = {'interval': ['ScalarBounds(lower=1.65, upper=1.65)'],
                     'values': [1.65],
                     'vrs': 'VERTCRS["WGS_1984",VDATUM["World Geodetic System 1984"],CS[vertical,1],AXIS["ellipsoidal height (h)",up,LENGTHUNIT["metre",1,ID["EPSG",9001]]]]',
                     'name': 'WGS_1984'}

        actual = VerticalExtent.from_json(json_dict)

        self.assertEqual(actual, expected)

    def test_init_type_checking_values(self):
        """
        GIVEN a non-list
        WHEN passed to VerticalExtent.values
        THEN a TypeError is returned
        """
        heights = {"value": 4}

        with self.assertRaisesRegex(TypeError, "Expected List of values, received <class 'dict'>"):
            VerticalExtent(values=heights)

    def test_init_type_checking_values_entry(self):
        """
        GIVEN a list of floats with one bad entry
        WHEN passed to VerticalExtent.values
        THEN a TypeError is returned with value and type
        """
        vals = list(np.arange(0, 1, 0.2))
        vals.append('1')

        with self.assertRaisesRegex(TypeError, "Expected all float values, received value '1' of type <class 'str'>"):
            VerticalExtent(values=vals)

    def test_init_type_checking_vrs(self):
        """
        GIVEN a non-CrsObject input
        WHEN passed to VerticalExtent
        THEN a TypeError is returned
        """
        vals = list(np.arange(0, 1, 0.2))
        input = "bad input"

        with self.assertRaisesRegex(TypeError, "Expected CrsObject, received <class 'str'>"):
            VerticalExtent(values=vals, vrs=input)
