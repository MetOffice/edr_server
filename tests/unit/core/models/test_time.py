import unittest
from datetime import datetime, timedelta

import pytest
from dateutil.tz import UTC, tzoffset

from edr_server.core.models.time import DateTimeInterval, Duration


class DateTimeIntervalTest(unittest.TestCase):

    def test_constant_inifinite_recurrences(self):
        """Verify that DateTimeInterval.INFINITE_RECURRENCES is set to the correct value"""
        self.assertEqual(-1, DateTimeInterval.INFINITE_RECURRENCES)

    def test_init_end_date_before_start_date(self):
        """GIVEN end date is before start date WHEN a DateTimeInterval is created THEN a ValueError is raised"""
        start_date = datetime.now()
        end_date = start_date - timedelta(days=1)

        self.assertRaises(ValueError, DateTimeInterval, start_date, end_date)

    def test__init__no_fields_set(self):
        """GIVEN no arguments are provided WHEN a DateTimeInterval is created THEN a ValueError is raised"""
        self.assertRaises(ValueError, DateTimeInterval)

    def test__init__recurrences_less_than_minus_1(self):
        """GIVEN recurrences is less than -1 WHEN a DateTimeInterval is created THEN a ValueError is raised"""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=1)

        # recurrences must be >= -1, so -2 is invalid
        self.assertRaises(ValueError, DateTimeInterval, start_date, end_date, recurrences=-2)

    def test__init__all_fields_set(self):
        """
        GIVEN start_date, end_date, and duration are provided
        WHEN a DateTimeInterval is created
        THEN a ValueError is raised

        The only valid combinations are:
        * start date & end date
        * start date & duration
        * duration & end date
        * duration only
        So everything else is not allowed
        """
        self.assertRaises(ValueError, DateTimeInterval, datetime.now(), datetime.now(), Duration(1))

    def test_init_only_start_date_set(self):
        """
        GIVEN only start_date is provided
        WHEN a DateTimeInterval is created
        THEN a ValueError is raised
        """
        self.assertRaises(ValueError, DateTimeInterval, datetime.now())

    def test_init_only_end_date_set(self):
        """
        GIVEN only end_date is provided
        WHEN a DateTimeInterval is created
        THEN a ValueError is raised
        """
        self.assertRaises(ValueError, DateTimeInterval, end=datetime.now())

    def test_init_only_duration_set(self):
        """
        GIVEN only duration is provided
        WHEN a DateTimeInterval is created
        THEN the correct DateTimeInterval is created
        """
        duration = Duration(1, 2, 3, 4)

        dti = DateTimeInterval(duration=duration)

        self.assertIsNone(dti.start)
        self.assertIsNone(dti.end)
        self.assertEqual(duration, dti.duration)

    def test_start_and_end_no_recurrence_implied(self):
        """
        WHEN a DateTimeInterval is created with a start and end date
        AND recurrence parameter is not passed
        THEN start property matches the passed parameter
        AND end property matches the passed parameter
        AND recurrence property is 0
        AND duration property is equal to `end` - `start`
        AND lower_bound property is equal to `start`
        AND upper_bound property is equal to `end`
        AND total_duration property is same as duration property
        """
        start = datetime(2022, 1, 1)
        end = datetime(2022, 1, 8)
        expected_duration = Duration(weeks=1)
        expected_recurrence = 0
        expected_lower_bound = start
        expected_upper_bound = end
        expected_total_duration = expected_duration

        dti = DateTimeInterval(start, end)

        self.assertEqual(start, dti.start)
        self.assertEqual(end, dti.end)
        self.assertEqual(expected_duration, dti.duration)
        self.assertEqual(expected_recurrence, dti.recurrences)
        self.assertEqual(expected_lower_bound, dti.lower_bound)
        self.assertEqual(expected_upper_bound, dti.upper_bound)
        self.assertEqual(expected_total_duration, dti.total_duration)

    def test_start_and_end_with_no_recurrence_explicit_none(self):
        """
        WHEN a DateTimeInterval is created with a start and end date and recurrence is None
        THEN start property matches the passed parameter
        AND end property matches the passed parameter
        AND recurrence property is 0
        AND duration property is equal to `end` - `start`
        AND lower_bound property is equal to `start`
        AND upper_bound property is equal to `end`
        AND total_duration property is same as duration property
        """
        start = datetime(2022, 1, 1)
        end = datetime(2022, 1, 8)
        expected_duration = Duration(weeks=1)
        expected_recurrence = 0
        expected_lower_bound = start
        expected_upper_bound = end
        expected_total_duration = expected_duration

        dti = DateTimeInterval(start, end, recurrences=None)

        self.assertEqual(start, dti.start)
        self.assertEqual(end, dti.end)
        self.assertEqual(expected_duration, dti.duration)
        self.assertEqual(expected_recurrence, dti.recurrences)
        self.assertEqual(expected_lower_bound, dti.lower_bound)
        self.assertEqual(expected_upper_bound, dti.upper_bound)
        self.assertEqual(expected_total_duration, dti.total_duration)

    def test_start_and_end_with_no_recurrence_explicit_0(self):
        """
        WHEN a DateTimeInterval is created with a start and end date and recurrence is 0
        THEN start property matches the passed parameter
        AND end property matches the passed parameter
        AND recurrence property is 0
        AND duration property is equal to `end` - `start`
        AND lower_bound property is equal to `start`
        AND upper_bound property is equal to `end`
        AND total_duration property is same as duration property
        """
        start = datetime(2022, 1, 1)
        end = datetime(2022, 1, 8)
        expected_duration = Duration(weeks=1)
        expected_recurrence = 0
        expected_lower_bound = start
        expected_upper_bound = end
        expected_total_duration = expected_duration

        dti = DateTimeInterval(start, end, recurrences=0)

        self.assertEqual(start, dti.start)
        self.assertEqual(end, dti.end)
        self.assertEqual(expected_duration, dti.duration)
        self.assertEqual(expected_recurrence, dti.recurrences)
        self.assertEqual(expected_lower_bound, dti.lower_bound)
        self.assertEqual(expected_upper_bound, dti.upper_bound)
        self.assertEqual(expected_total_duration, dti.total_duration)

    def test_start_and_end_with_recurrence(self):
        """
        WHEN a DateTimeInterval is created with a start and end date and recurrences
        THEN start property matches the passed parameter
        AND end property matches the passed parameter
        AND recurrence property matches the passed parameter
        AND duration property is equal to `end` - `start`
        AND lower_bound property is equal to `start`
        AND upper_bound property is equal to `start` + `total_duration`
        AND total_duration property is equal to `duration` * (`recurrences` + 1)
        """
        start = datetime(2022, 1, 1)
        end = datetime(2022, 1, 8)
        recurrences = 5
        expected_duration = Duration(weeks=1)
        expected_lower_bound = start
        # Just to highlight, but: `start` + `total_duration` == `end` + (`duration` * `recurrences`)
        expected_upper_bound = end + Duration.from_timedelta(expected_duration.to_timedelta() * recurrences)
        expected_total_duration = Duration.from_timedelta(expected_duration.to_timedelta() * (recurrences + 1))

        dti = DateTimeInterval(start, end, recurrences=recurrences)

        self.assertEqual(start, dti.start)
        self.assertEqual(end, dti.end)
        self.assertEqual(expected_duration, dti.duration)
        self.assertEqual(recurrences, dti.recurrences)
        self.assertEqual(expected_lower_bound, dti.lower_bound)
        self.assertEqual(expected_upper_bound, dti.upper_bound)
        self.assertEqual(expected_total_duration, dti.total_duration)

    def test_start_and_end_with_infinite_recurrence(self):
        """
        WHEN a DateTimeInterval is created with a start and end date and recurrences are infinite
        THEN start property matches the passed parameter
        AND end property matches the passed parameter
        AND recurrence property matches the passed parameter
        AND duration property is equal to `end` - `start`
        AND lower_bound property is equal to `start`
        AND upper_bound property is None
        AND total_duration property is None
        """
        start = datetime(2022, 1, 1)
        end = datetime(2022, 1, 8)
        recurrences = DateTimeInterval.INFINITE_RECURRENCES
        expected_duration = Duration(weeks=1)
        expected_lower_bound = start

        dti = DateTimeInterval(start, end, recurrences=recurrences)

        self.assertEqual(start, dti.start)
        self.assertEqual(end, dti.end)
        self.assertEqual(expected_duration, dti.duration)
        self.assertEqual(recurrences, dti.recurrences)
        self.assertEqual(expected_lower_bound, dti.lower_bound)
        # upper bound and total duration are None, because the interval's right bound is infinite
        # Our convention when we have both start and end dates, is that we use the start date as our fixed point
        # to begin recurring from, hence the upper bound is infinite, but the lower bound is not.
        self.assertIsNone(dti.upper_bound)
        self.assertIsNone(dti.total_duration)

    def test_start_and_duration_no_recurrence_implied(self):
        """
        WHEN a DateTimeInterval is created with a start and a duration
        AND recurrence parameter is not passed
        THEN start property matches the passed parameter
        AND end property is equal to `start` + `duration`
        AND recurrence property is 0
        AND duration property is equal to the passed parameter
        AND lower_bound property is equal to `start`
        AND upper_bound property is equal to `end`
        AND total_duration property is same as duration property
        """
        start = datetime(2022, 1, 1)
        duration = Duration(weeks=1)
        expected_end = datetime(2022, 1, 8)
        expected_recurrence = 0
        expected_lower_bound = start
        expected_upper_bound = expected_end
        expected_total_duration = duration

        dti = DateTimeInterval(start, duration=duration)

        self.assertEqual(start, dti.start)
        self.assertEqual(duration, dti.duration)
        self.assertEqual(expected_end, dti.end)
        self.assertEqual(expected_recurrence, dti.recurrences)
        self.assertEqual(expected_lower_bound, dti.lower_bound)
        self.assertEqual(expected_upper_bound, dti.upper_bound)
        self.assertEqual(expected_total_duration, dti.total_duration)

    def test_start_and_duration_with_no_recurrence_explicit_none(self):
        """
        WHEN a DateTimeInterval is created with a start and a duration and recurrence is None
        THEN start property matches the passed parameter
        AND end property is equal to `start` + `duration`
        AND recurrence property is 0
        AND duration property is equal to the passed parameter
        AND lower_bound property is equal to `start`
        AND upper_bound property is equal to `end`
        AND total_duration property is same as duration property
        """
        start = datetime(2022, 1, 1)
        duration = Duration(weeks=1)
        expected_end = datetime(2022, 1, 8)
        expected_recurrence = 0
        expected_lower_bound = start
        expected_upper_bound = expected_end
        expected_total_duration = duration

        dti = DateTimeInterval(start, duration=duration, recurrences=None)

        self.assertEqual(start, dti.start)
        self.assertEqual(duration, dti.duration)
        self.assertEqual(expected_end, dti.end)
        self.assertEqual(expected_recurrence, dti.recurrences)
        self.assertEqual(expected_lower_bound, dti.lower_bound)
        self.assertEqual(expected_upper_bound, dti.upper_bound)
        self.assertEqual(expected_total_duration, dti.total_duration)

    def test_start_and_duration_with_no_recurrence_explicit_0(self):
        """
        WHEN a DateTimeInterval is created with a start and a duration and recurrence is 0
        THEN start property matches the passed parameter
        AND end property is equal to `start` + `duration`
        AND recurrence property is 0
        AND duration property is equal to the passed parameter
        AND lower_bound property is equal to `start`
        AND upper_bound property is equal to `end`
        AND total_duration property is same as duration property
        """
        start = datetime(2022, 1, 1)
        duration = Duration(weeks=1)
        expected_end = datetime(2022, 1, 8)
        expected_recurrence = 0
        expected_lower_bound = start
        expected_upper_bound = expected_end
        expected_total_duration = duration

        dti = DateTimeInterval(start, duration=duration, recurrences=0)

        self.assertEqual(start, dti.start)
        self.assertEqual(duration, dti.duration)
        self.assertEqual(expected_end, dti.end)
        self.assertEqual(expected_recurrence, dti.recurrences)
        self.assertEqual(expected_lower_bound, dti.lower_bound)
        self.assertEqual(expected_upper_bound, dti.upper_bound)
        self.assertEqual(expected_total_duration, dti.total_duration)

    def test_start_and_duration_with_recurrence(self):
        """
        WHEN a DateTimeInterval is created with a start and duration and recurrences
        THEN start property matches the passed parameter
        AND end property is equal to `start` + `duration`
        AND recurrence property matches the passed parameter
        AND duration property matches the passed parameter
        AND lower_bound property is equal to `start`
        AND upper_bound property is equal to `start` + `total_duration`
        AND total_duration property is equal to `duration` * (`recurrences` + 1)
        """
        start = datetime(2022, 1, 1)
        duration = Duration(weeks=1)
        recurrences = 5
        expected_end = datetime(2022, 1, 8)
        expected_lower_bound = start
        # Just to highlight, but: `start` + `total_duration` == `end` + (`duration` * `recurrences`)
        expected_upper_bound = expected_end + Duration.from_timedelta(duration.to_timedelta() * recurrences)
        expected_total_duration = Duration.from_timedelta(duration.to_timedelta() * (recurrences + 1))

        dti = DateTimeInterval(start, duration=duration, recurrences=recurrences)

        self.assertEqual(start, dti.start)
        self.assertEqual(duration, dti.duration)
        self.assertEqual(recurrences, dti.recurrences)
        self.assertEqual(expected_end, dti.end)
        self.assertEqual(expected_lower_bound, dti.lower_bound)
        self.assertEqual(expected_upper_bound, dti.upper_bound)
        self.assertEqual(expected_total_duration, dti.total_duration)

    def test_start_and_duration_with_infinite_recurrence(self):
        """
        WHEN a DateTimeInterval is created with a start and duration and recurrences are infinite
        THEN start property matches the passed parameter
        AND end property is equal to `start` + `duration`
        AND recurrence property matches the passed parameter
        AND duration property matches the passed parameter
        AND lower_bound property is equal to `start`
        AND upper_bound property is None
        AND total_duration property is None
        """
        start = datetime(2022, 1, 1)
        duration = Duration(weeks=1)
        recurrences = DateTimeInterval.INFINITE_RECURRENCES
        expected_end = datetime(2022, 1, 8)
        expected_lower_bound = start

        dti = DateTimeInterval(start, duration=duration, recurrences=recurrences)

        self.assertEqual(start, dti.start)
        self.assertEqual(duration, dti.duration)
        self.assertEqual(recurrences, dti.recurrences)
        self.assertEqual(expected_end, dti.end)
        self.assertEqual(expected_lower_bound, dti.lower_bound)
        # upper bound and total duration are None, because the interval's right bound is infinite
        # In this case, as a start date was supplied, we use that as our fixed reference point for the beginning of the
        # interval, and the interval recurs infinitely from that point onwards.
        self.assertIsNone(dti.upper_bound)
        self.assertIsNone(dti.total_duration)

    def test_end_and_duration_no_recurrence_implied(self):
        """
        WHEN a DateTimeInterval is created with an end and a duration
        AND recurrence parameter is not passed
        THEN start property is equal to `end` - `duration`
        AND end property matches the passed parameter
        AND recurrence property is 0
        AND duration property matches the passed parameter
        AND lower_bound property is equal to `start`
        AND upper_bound property is equal to `end`
        AND total_duration property is same as duration property
        """
        end = datetime(2022, 1, 8)
        duration = Duration(weeks=1)
        expected_start = datetime(2022, 1, 1)
        expected_recurrence = 0
        expected_lower_bound = expected_start
        expected_upper_bound = end
        expected_total_duration = duration

        dti = DateTimeInterval(end=end, duration=duration)

        self.assertEqual(end, dti.end)
        self.assertEqual(duration, dti.duration)
        self.assertEqual(expected_start, dti.start)
        self.assertEqual(expected_recurrence, dti.recurrences)
        self.assertEqual(expected_lower_bound, dti.lower_bound)
        self.assertEqual(expected_upper_bound, dti.upper_bound)
        self.assertEqual(expected_total_duration, dti.total_duration)

    def test_end_and_duration_with_no_recurrence_explicit_none(self):
        """
        WHEN a DateTimeInterval is created with an end and a duration and recurrences is None
        THEN start property is equal to `end` - `duration`
        AND end property matches the passed parameter
        AND recurrence property is 0
        AND duration property matches the passed parameter
        AND lower_bound property is equal to `start`
        AND upper_bound property is equal to `end`
        AND total_duration property is same as duration property
        """
        end = datetime(2022, 1, 8)
        duration = Duration(weeks=1)
        expected_start = datetime(2022, 1, 1)
        expected_recurrence = 0
        expected_lower_bound = expected_start
        expected_upper_bound = end
        expected_total_duration = duration

        dti = DateTimeInterval(end=end, duration=duration, recurrences=None)

        self.assertEqual(end, dti.end)
        self.assertEqual(duration, dti.duration)
        self.assertEqual(expected_start, dti.start)
        self.assertEqual(expected_recurrence, dti.recurrences)
        self.assertEqual(expected_lower_bound, dti.lower_bound)
        self.assertEqual(expected_upper_bound, dti.upper_bound)
        self.assertEqual(expected_total_duration, dti.total_duration)

    def test_end_and_duration_with_no_recurrence_explicit_0(self):
        """
        WHEN a DateTimeInterval is created with an end and a duration and recurrences is 0
        THEN start property is equal to `end` - `duration`
        AND end property matches the passed parameter
        AND recurrence property is 0
        AND duration property matches the passed parameter
        AND lower_bound property is equal to `start`
        AND upper_bound property is equal to `end`
        AND total_duration property is same as duration property
        """
        end = datetime(2022, 1, 15)
        duration = Duration(weeks=2)
        expected_start = datetime(2022, 1, 1)
        recurrences = 0
        expected_lower_bound = expected_start
        expected_upper_bound = end
        expected_total_duration = duration

        dti = DateTimeInterval(end=end, duration=duration, recurrences=recurrences)

        self.assertEqual(end, dti.end)
        self.assertEqual(duration, dti.duration)
        self.assertEqual(expected_start, dti.start)
        self.assertEqual(recurrences, dti.recurrences)
        self.assertEqual(expected_lower_bound, dti.lower_bound)
        self.assertEqual(expected_upper_bound, dti.upper_bound)
        self.assertEqual(expected_total_duration, dti.total_duration)

    def test_end_and_duration_with_recurrence(self):
        """
        WHEN a DateTimeInterval is created with an end and duration and recurrences
        THEN start property is equal to `end` - `duration`
        AND end property matches the passed parameter
        AND recurrence property matches the passed parameter
        AND duration property matches the passed parameter
        AND lower_bound property is equal to `end` - `total_duration`
        AND upper_bound property is equal to `end`
        AND total_duration property is equal to `duration` * (`recurrences` + 1)
        """
        end = datetime(2022, 1, 8)
        duration = Duration(weeks=1)
        recurrences = 5
        expected_start = datetime(2022, 1, 1)
        expected_lower_bound = end - Duration.from_timedelta(duration.to_timedelta() * (recurrences + 1))
        expected_upper_bound = end
        expected_total_duration = Duration.from_timedelta(duration.to_timedelta() * (recurrences + 1))

        dti = DateTimeInterval(end=end, duration=duration, recurrences=recurrences)

        self.assertEqual(expected_start, dti.start)
        self.assertEqual(duration, dti.duration)
        self.assertEqual(recurrences, dti.recurrences)
        self.assertEqual(end, dti.end)
        self.assertEqual(expected_lower_bound, dti.lower_bound)
        self.assertEqual(expected_upper_bound, dti.upper_bound)
        self.assertEqual(expected_total_duration, dti.total_duration)

    def test_end_and_duration_with_infinite_recurrence(self):
        """
        WHEN a DateTimeInterval is created with an end and duration and recurrences are infinite
        THEN start property is equal to `end` - `duration`
        AND end property matches the passed parameter
        AND recurrence property matches the passed parameter
        AND duration property matches the passed parameter
        AND lower_bound property is None
        AND upper_bound property is equal to `end`
        AND total_duration property is None
        """
        end = datetime(2022, 1, 8)
        duration = Duration(weeks=1)
        recurrences = DateTimeInterval.INFINITE_RECURRENCES
        expected_start = datetime(2022, 1, 1)
        expected_upper_bound = end

        dti = DateTimeInterval(end=end, duration=duration, recurrences=recurrences)

        self.assertEqual(expected_start, dti.start)
        self.assertEqual(duration, dti.duration)
        self.assertEqual(recurrences, dti.recurrences)
        self.assertEqual(end, dti.end)
        self.assertEqual(expected_upper_bound, dti.upper_bound)
        # lower bound and total duration are None, because the interval's left bound is infinite
        # In this case, as an end date was supplied, we use that as our fixed reference point for the end of the
        # interval, and the interval recurs infinitely up to that point, but not beyond. (i.e. it recurs into the past)
        self.assertIsNone(dti.lower_bound)
        self.assertIsNone(dti.total_duration)

    def test_duration_only_no_recurrence_implied(self):
        """
        WHEN a DateTimeInterval is created with only a duration
        AND recurrence parameter is not passed
        THEN start property is None
        AND end property is None
        AND recurrence property is 0
        AND duration property matches the passed parameter
        AND lower_bound property is None
        AND upper_bound property is None
        AND total_duration property is same as duration property
        """
        duration = Duration(weeks=1)
        expected_recurrence = 0
        expected_total_duration = duration

        dti = DateTimeInterval(duration=duration)

        self.assertEqual(duration, dti.duration)
        self.assertIsNone(dti.start)
        self.assertIsNone(dti.end)
        self.assertEqual(expected_recurrence, dti.recurrences)
        self.assertIsNone(dti.lower_bound)
        self.assertIsNone(dti.upper_bound)
        self.assertEqual(expected_total_duration, dti.total_duration)

    def test_duration_only_with_no_recurrence_explicit_none(self):
        """
        WHEN a DateTimeInterval is created with only a duration
        AND recurrences parameter is None
        THEN start property is None
        AND end property is None
        AND recurrence property is 0
        AND duration property matches the passed parameter
        AND lower_bound property is None
        AND upper_bound property is None
        AND total_duration property is same as duration property
        """
        duration = Duration(weeks=1)
        expected_recurrence = 0
        expected_total_duration = duration

        dti = DateTimeInterval(duration=duration, recurrences=None)

        self.assertEqual(duration, dti.duration)
        self.assertIsNone(dti.start)
        self.assertIsNone(dti.end)
        self.assertEqual(expected_recurrence, dti.recurrences)
        self.assertIsNone(dti.lower_bound)
        self.assertIsNone(dti.upper_bound)
        self.assertEqual(expected_total_duration, dti.total_duration)

    def test_duration_only_with_no_recurrence_explicit_0(self):
        """
        WHEN a DateTimeInterval is created with a duration and recurrences is 0
        THEN start property is None
        AND end property is None
        AND recurrence property is 0
        AND duration property matches the passed parameter
        AND lower_bound property is None
        AND upper_bound property is None
        AND total_duration property is same as duration property
        """
        duration = Duration(weeks=1)
        recurrences = 0
        expected_total_duration = duration

        dti = DateTimeInterval(duration=duration, recurrences=recurrences)

        self.assertEqual(duration, dti.duration)
        self.assertIsNone(dti.start)
        self.assertIsNone(dti.end)
        self.assertEqual(recurrences, dti.recurrences)
        self.assertIsNone(dti.lower_bound)
        self.assertIsNone(dti.upper_bound)
        self.assertEqual(expected_total_duration, dti.total_duration)

    def test_duration_only_with_recurrence(self):
        """
        WHEN a DateTimeInterval is created with a duration and recurrences
        THEN start property is None
        AND end property is None
        AND recurrence property matches the passed parameter
        AND duration property matches the passed parameter
        AND lower_bound property is None
        AND upper_bound property is None
        AND total_duration property equals `duration` * (`recurrences` + 1)
        """
        duration = Duration(hours=12)
        recurrences = 5
        expected_total_duration = Duration.from_timedelta(duration.to_timedelta() * (recurrences + 1))

        dti = DateTimeInterval(duration=duration, recurrences=recurrences)

        self.assertEqual(duration, dti.duration)
        self.assertIsNone(dti.start)
        self.assertIsNone(dti.end)
        self.assertEqual(recurrences, dti.recurrences)
        self.assertIsNone(dti.lower_bound)
        self.assertIsNone(dti.upper_bound)
        self.assertEqual(expected_total_duration, dti.total_duration)

    def test_duration_only_with_infinite_recurrence(self):
        """
        WHEN a DateTimeInterval is created with a duration and recurrences is inifinte
        THEN start property is None
        AND end property is None
        AND recurrence property is 0
        AND duration property matches the passed parameter
        AND lower_bound property is None
        AND upper_bound property is None
        AND total_duration property is None
        """
        duration = Duration(weeks=1)
        recurrences = DateTimeInterval.INFINITE_RECURRENCES

        dti = DateTimeInterval(duration=duration, recurrences=recurrences)

        self.assertEqual(duration, dti.duration)
        self.assertIsNone(dti.start)
        self.assertIsNone(dti.end)
        self.assertEqual(recurrences, dti.recurrences)
        self.assertIsNone(dti.lower_bound)
        self.assertIsNone(dti.upper_bound)
        self.assertIsNone(dti.total_duration)


@pytest.mark.parametrize("dti1, dti2", [
    (DateTimeInterval(datetime(2022, 1, 1), datetime(2022, 1, 2)),
     DateTimeInterval(datetime(2022, 1, 1), datetime(2022, 1, 2))),
    (DateTimeInterval(datetime(2022, 1, 1), duration=Duration(days=1)),
     DateTimeInterval(datetime(2022, 1, 1), duration=Duration(days=1))),
    (DateTimeInterval(end=datetime(2022, 1, 1), duration=Duration(days=1)),
     DateTimeInterval(end=datetime(2022, 1, 1), duration=Duration(days=1))),
    (DateTimeInterval(duration=Duration(years=1)),
     DateTimeInterval(duration=Duration(years=1))),

    # Equivalent instances, created with different arguments
    (DateTimeInterval(datetime(2022, 1, 1), datetime(2022, 1, 2)),
     DateTimeInterval(datetime(2022, 1, 1), duration=Duration(days=1))),
    (DateTimeInterval(end=datetime(2022, 1, 2), duration=Duration(days=1)),
     DateTimeInterval(datetime(2022, 1, 1), duration=Duration(days=1))),

    (DateTimeInterval(datetime(2022, 1, 1), datetime(2022, 1, 2), recurrences=3),
     DateTimeInterval(datetime(2022, 1, 1), duration=Duration(days=1), recurrences=3)),
    (DateTimeInterval(datetime(2022, 1, 1), datetime(2022, 1, 2)),  # Compare implicit 0 with explicit 0
     DateTimeInterval(datetime(2022, 1, 1), duration=Duration(days=1), recurrences=0)),
    (DateTimeInterval(datetime(2022, 1, 1), datetime(2022, 1, 2)),
     # Compare implicit default recurrences with explicit None
     DateTimeInterval(datetime(2022, 1, 1), duration=Duration(days=1), recurrences=None)),
    (DateTimeInterval(end=datetime(2022, 1, 2), duration=Duration(days=1),
                      recurrences=DateTimeInterval.INFINITE_RECURRENCES),
     DateTimeInterval(datetime(2022, 1, 1), duration=Duration(days=1),
                      recurrences=DateTimeInterval.INFINITE_RECURRENCES)),
], ids=repr)
def test_datetimeinterval__eq__(dti1: DateTimeInterval, dti2: DateTimeInterval):
    """GIVEN 2 DateTimeIntervals that are expected to be equal WHEN __eq__ is called THEN True is returned"""
    # == implicitly calls the objects __eq__ rich comparison method
    assert dti1 == dti2
    assert (dti1 != dti2) is False
    assert dti2 == dti1
    assert (dti2 != dti1) is False


@pytest.mark.parametrize("dti1, dti2", [
    (DateTimeInterval(datetime(2022, 1, 1), datetime(2022, 1, 2)),
     DateTimeInterval(datetime(2022, 1, 1), datetime(2022, 1, 2), recurrences=1)),
    (DateTimeInterval(datetime(2022, 1, 1), duration=Duration(days=1)),
     DateTimeInterval(datetime(2022, 1, 1), duration=Duration(weeks=2))),
    (DateTimeInterval(end=datetime(2022, 1, 1), duration=Duration(days=1)),
     DateTimeInterval(end=datetime(2022, 1, 1), duration=Duration(weeks=1))),
    (DateTimeInterval(duration=Duration(years=1)),
     DateTimeInterval(duration=Duration(days=1))),
    (DateTimeInterval(duration=Duration(days=1)),

     DateTimeInterval(duration=Duration(days=1), recurrences=DateTimeInterval.INFINITE_RECURRENCES)),
    (DateTimeInterval(duration=Duration(days=1), recurrences=1),
     DateTimeInterval(duration=Duration(days=1), recurrences=DateTimeInterval.INFINITE_RECURRENCES)),
    (DateTimeInterval(duration=Duration(days=1), recurrences=0),
     DateTimeInterval(duration=Duration(days=1), recurrences=DateTimeInterval.INFINITE_RECURRENCES)),
    (DateTimeInterval(duration=Duration(days=1), recurrences=None),
     DateTimeInterval(duration=Duration(days=1), recurrences=DateTimeInterval.INFINITE_RECURRENCES)),
    (DateTimeInterval(duration=Duration(days=1), recurrences=1),
     DateTimeInterval(duration=Duration(days=1), recurrences=0)),

    (DateTimeInterval(datetime(2022, 1, 1), datetime(2022, 1, 2), recurrences=1),
     DateTimeInterval(datetime(2022, 1, 1), duration=Duration(days=1))),
    (DateTimeInterval(end=datetime(2022, 1, 2), duration=Duration(days=1)),
     DateTimeInterval(datetime(2022, 1, 1), duration=Duration(days=1), recurrences=2)),
    (DateTimeInterval(datetime(2022, 1, 1), datetime(2022, 1, 2), recurrences=3),
     DateTimeInterval(datetime(2022, 1, 1), duration=Duration(days=1))),
    (DateTimeInterval(end=datetime(2022, 1, 2), duration=Duration(days=2)),
     DateTimeInterval(datetime(2022, 1, 1), duration=Duration(days=1))),

    (DateTimeInterval(duration=Duration(days=1)), None),
    (DateTimeInterval(duration=Duration(days=1)), object()),
    (DateTimeInterval(duration=Duration(days=1)), 1),
    (DateTimeInterval(duration=Duration(days=1)), [1, 2, 3]),

], ids=repr)
def test_datetimeinterval__neq__(dti1: DateTimeInterval, dti2: DateTimeInterval):
    """GIVEN 2 DateTimeIntervals that are not expected to be equal WHEN __ne__ is called THEN True is returned"""
    # != implicitly calls the objects __ne__ rich comparison method
    assert dti1 != dti2
    assert (dti1 == dti2) is False
    assert dti2 != dti1
    assert (dti2 == dti1) is False


@pytest.mark.parametrize("str_dti, dti_obj", [
    # start/end interval tests
    ("2022-01-01T00:00:00Z/2022-01-01T12:00:00Z",
     DateTimeInterval(datetime(2022, 1, 1, tzinfo=UTC), datetime(2022, 1, 1, 12, tzinfo=UTC))),
    ("2022-01-01T00:00:00+00:00/2022-01-01T12:00:00+00:00",
     DateTimeInterval(datetime(2022, 1, 1, tzinfo=UTC), datetime(2022, 1, 1, 12, tzinfo=UTC))),
    # start/end interval tests - non UTC timezones
    ("2022-01-01T00:00:00+01:00/2022-01-01T12:00:00+01:00",
     DateTimeInterval(
         datetime(2022, 1, 1, tzinfo=tzoffset("", 3600)), datetime(2022, 1, 1, 12, tzinfo=tzoffset("", 3600)))
     ),
    ("2022-01-01T00:00:00-00:30/2022-01-01T12:00:00-00:30",
     DateTimeInterval(
         datetime(2022, 1, 1, tzinfo=tzoffset("", -1800)), datetime(2022, 1, 1, 12, tzinfo=tzoffset("", -1800)))),
    ("2022-01-01T00:00:00+0030/2022-01-01T12:00:00+0030",
     DateTimeInterval(
         datetime(2022, 1, 1, tzinfo=tzoffset("", 1800)), datetime(2022, 1, 1, 12, tzinfo=tzoffset("", 1800)))),
    ("2022-01-01T00:00:00-0030/2022-01-01T12:00:00-0030",
     DateTimeInterval(
         datetime(2022, 1, 1, tzinfo=tzoffset("", -1800)), datetime(2022, 1, 1, 12, tzinfo=tzoffset("", -1800)))),
    ("2022-01-01T00:00:00+12/2022-01-01T12:00:00+12",
     DateTimeInterval(
         datetime(2022, 1, 1, tzinfo=tzoffset("", 3600 * 12)),
         datetime(2022, 1, 1, 12, tzinfo=tzoffset("", 3600 * 12)))),
    ("2022-01-01T00:00:00-11/2022-01-01T12:00:00-11",
     DateTimeInterval(
         datetime(2022, 1, 1, tzinfo=tzoffset("", 3600 * -11)),
         datetime(2022, 1, 1, 12, tzinfo=tzoffset("", 3600 * -11)))),

    # start/duration tests
    ("2007-03-01T13:00:00Z/P1Y2M10DT2H30M",
     DateTimeInterval(datetime(2007, 3, 1, 13, tzinfo=UTC), duration=Duration(1, 2, 10, 2, 30))),

    # duration/end tests
    ("P1Y2M10DT2H30M/2008-05-11T15:30:00Z",
     DateTimeInterval(duration=Duration(1, 2, 10, 2, 30), end=datetime(2008, 5, 11, 15, 30, tzinfo=UTC))),

    # duration only tests
    ("P1Y2M10DT2H30M", DateTimeInterval(duration=Duration(1, 2, 10, 2, 30))),

    # Repeating interval tests
    ("R2/2022-01-01T00:00:00Z/2022-01-01T12:00:00Z",
     DateTimeInterval(datetime(2022, 1, 1, tzinfo=UTC), datetime(2022, 1, 1, 12, tzinfo=UTC), recurrences=2)),
    ("R5/2008-03-01T13:00:00Z/P1Y2M10DT2H30M",
     DateTimeInterval(datetime(2008, 3, 1, 13, tzinfo=UTC), duration=Duration(1, 2, 10, 2, 30), recurrences=5)),
    ("R0/P1Y2M10DT2H30M", DateTimeInterval(duration=Duration(1, 2, 10, 2, 30), recurrences=0)),
    ("R-1/P1Y2M10DT2H30M",
     DateTimeInterval(duration=Duration(1, 2, 10, 2, 30), recurrences=DateTimeInterval.INFINITE_RECURRENCES)),
])
def test_datetimeinterval_parse_str_valid(str_dti: str, dti_obj: DateTimeInterval):
    """Can we convert a valid ISO8601 duration string to a Duration object?"""
    # There are minor but important differences between these test cases and the object->str test cases, as the __str__
    # method uses a specific ISO compliant format and doesn't support generating all the different valid ISO flavours.
    # Which is why these test cases aren't shared like the equivalent Duration tests.

    assert DateTimeInterval.parse_str(str_dti) == dti_obj


@pytest.mark.parametrize("str_dti", [
    # Technically having -00:00 as the timezone offset is invalid, as should be +00:00. However, the dateutil library
    # handles this, and I don't think it's important enough to make it fail, so I've just left it here commented out
    # to acknowledge its validity as a test case and why we're not testing it
    # "2022-01-01T00:00:00-00:00/2022-01-01T12:00:00-00:00",
    "R-2/2022-01-01T00:00:00Z/2022-01-01T12:00:00Z"
])
def test_datetimeinterval_parse_str_invalid(str_dti: str):
    pytest.raises(ValueError, DateTimeInterval.parse_str, str_dti)


@pytest.mark.parametrize("dti_obj,str_dti", [
    # start/end interval tests
    (DateTimeInterval(datetime(2022, 1, 1, tzinfo=UTC), datetime(2022, 1, 1, 12, tzinfo=UTC)),
     "2022-01-01T00:00:00+00:00/2022-01-01T12:00:00+00:00"),
    (DateTimeInterval(datetime(2022, 1, 1, tzinfo=UTC), datetime(2022, 1, 1, 12, tzinfo=UTC)),
     "2022-01-01T00:00:00+00:00/2022-01-01T12:00:00+00:00"),
    # microseconds are ignored
    (DateTimeInterval(datetime(2022, 1, 1, 3, 4, 5, microsecond=6, tzinfo=UTC),
                      datetime(2022, 1, 1, 12, 1, 2, microsecond=3, tzinfo=UTC)),
     "2022-01-01T03:04:05+00:00/2022-01-01T12:01:02+00:00"),
    # start/end interval tests - non UTC timezones
    (DateTimeInterval(
        datetime(2022, 1, 1, tzinfo=tzoffset("", 3600)), datetime(2022, 1, 1, 12, tzinfo=tzoffset("", 3600))),
     "2022-01-01T00:00:00+01:00/2022-01-01T12:00:00+01:00"),
    (DateTimeInterval(
        datetime(2022, 1, 1, tzinfo=tzoffset("", -1800)), datetime(2022, 1, 1, 12, tzinfo=tzoffset("", -1800))),
     "2022-01-01T00:00:00-00:30/2022-01-01T12:00:00-00:30"),
    (DateTimeInterval(
        datetime(2022, 1, 1, tzinfo=tzoffset("", 1800)), datetime(2022, 1, 1, 12, tzinfo=tzoffset("", 1800))),
     "2022-01-01T00:00:00+00:30/2022-01-01T12:00:00+00:30"),
    (DateTimeInterval(
        datetime(2022, 1, 1, tzinfo=tzoffset("", -1800)), datetime(2022, 1, 1, 12, tzinfo=tzoffset("", -1800))),
     "2022-01-01T00:00:00-00:30/2022-01-01T12:00:00-00:30"),
    (DateTimeInterval(datetime(2022, 1, 1, tzinfo=tzoffset("", 3600 * 12)),
                      datetime(2022, 1, 1, 12, tzinfo=tzoffset("", 3600 * 12))),
     "2022-01-01T00:00:00+12:00/2022-01-01T12:00:00+12:00"),
    (DateTimeInterval(datetime(2022, 1, 1, tzinfo=tzoffset("", 3600 * -11)),
                      datetime(2022, 1, 1, 12, tzinfo=tzoffset("", 3600 * -11))),
     "2022-01-01T00:00:00-11:00/2022-01-01T12:00:00-11:00"),

    # start/duration tests
    (DateTimeInterval(datetime(2007, 3, 1, 13, tzinfo=UTC), duration=Duration(1, 2, 10, 2, 30)),
     "2007-03-01T13:00:00+00:00/P1Y2M10DT2H30M"),

    # duration/end tests
    (DateTimeInterval(duration=Duration(1, 2, 10, 2, 30), end=datetime(2008, 5, 11, 15, 30, tzinfo=UTC)),
     "P1Y2M10DT2H30M/2008-05-11T15:30:00+00:00"),

    # duration only tests
    (DateTimeInterval(duration=Duration(1, 2, 10, 2, 30)), "P1Y2M10DT2H30M"),

    # Repeating interval tests
    (DateTimeInterval(datetime(2022, 1, 1, tzinfo=UTC), datetime(2022, 1, 1, 12, tzinfo=UTC), recurrences=2),
     "R2/2022-01-01T00:00:00+00:00/2022-01-01T12:00:00+00:00"),
    (DateTimeInterval(datetime(2008, 3, 1, 13, tzinfo=UTC), duration=Duration(1, 2, 10, 2, 30), recurrences=5),
     "R5/2008-03-01T13:00:00+00:00/P1Y2M10DT2H30M"),
    (DateTimeInterval(duration=Duration(1, 2, 10, 2, 30), recurrences=0), "R0/P1Y2M10DT2H30M"),
    (DateTimeInterval(duration=Duration(1, 2, 10, 2, 30), recurrences=DateTimeInterval.INFINITE_RECURRENCES),
     "R-1/P1Y2M10DT2H30M"),
])
def test_datetimeinterval_str_valid(dti_obj: DateTimeInterval, str_dti: str, ):
    """Can we convert a Duration object to a valid ISO8601 string?"""
    # commas are valid as a separator, but we will always serialise using periods
    assert str(dti_obj) == str_dti
