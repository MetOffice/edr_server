"""
Tests clean_air.models.Duration
Separate from the other tests for the clean_air.models module because there's so many of them
"""
import unittest
from datetime import datetime, timedelta

import pytest
from edr_server.core.models.time import Duration
from dateutil.relativedelta import relativedelta


class DurationTest(unittest.TestCase):

    def test_init_defaults(self):
        """GIVEN no arguments are passed WHEN a Duration is created THEN values default to 0"""
        d = Duration(weeks=1)  # We have to supply at least 1 value

        self.assertEqual(0, d.seconds)
        self.assertEqual(0, d.minutes)
        self.assertEqual(0, d.hours)
        self.assertEqual(0, d.days)
        self.assertEqual(0, d.months)
        self.assertEqual(0, d.years)

        d = Duration(years=1)  # Now check the default value for weeks
        self.assertEqual(0, d.weeks)

    def test_init_kwargs_ints(self):
        """WHEN a Duration is created using keyword arguments and integer values THEN the correct values are stored"""
        d = Duration(seconds=1, minutes=2, hours=3, days=4, months=5, years=6)

        self.assertEqual(1, d.seconds)
        self.assertEqual(2, d.minutes)
        self.assertEqual(3, d.hours)
        self.assertEqual(4, d.days)
        self.assertEqual(5, d.months)
        self.assertEqual(6, d.years)

        self.assertEqual(0, d.weeks)  # "weeks" cannot be combined with other args

    def test_init_kwargs_floats(self):
        """WHEN a Duration is created using keyword arguments and float values THEN the correct values are stored"""
        d = Duration(seconds=1.1, minutes=2.2, hours=3.3, days=4.4, months=5, years=6.6)

        self.assertEqual(1.1, d.seconds)
        self.assertEqual(2.2, d.minutes)
        self.assertEqual(3.3, d.hours)
        self.assertEqual(4.4, d.days)
        self.assertEqual(5, d.months)  # Floats not allowed here
        self.assertEqual(6.6, d.years)  # Floats not allowed here

        self.assertEqual(0, d.weeks)  # "weeks" cannot be combined with other args

    def test_init_positionals_ints(self):
        """
        WHEN a Duration is created using positional arguments and integer values THEN the correct values are stored
        """
        d = Duration(6, 5, 4, 3, 2, 1)

        self.assertEqual(1, d.seconds)
        self.assertEqual(2, d.minutes)
        self.assertEqual(3, d.hours)
        self.assertEqual(4, d.days)
        self.assertEqual(5, d.months)
        self.assertEqual(6, d.years)

        self.assertEqual(0, d.weeks)  # "weeks" cannot be combined with other args

    def test_init_positionals_floats(self):
        """WHEN a Duration is created using positional arguments and float values THEN the correct values are stored"""
        d = Duration(6.0, 5, 4.4, 3.3, 2.2, 1.1)

        self.assertEqual(1.1, d.seconds)
        self.assertEqual(2.2, d.minutes)
        self.assertEqual(3.3, d.hours)
        self.assertEqual(4.4, d.days)
        self.assertEqual(5, d.months)  # Floats not allowed here
        self.assertEqual(6.0, d.years)  # Floats not allowed here

        self.assertEqual(0, d.weeks)  # "weeks" cannot be combined with other args

    def test_init_weeks_int(self):
        """GIVEN weeks=1 WHEN a Duration is created THEN correct values are stored"""
        d = Duration(weeks=1)

        self.assertEqual(1, d.weeks)  # "weeks" cannot be combined with other args

        self.assertEqual(0, d.seconds)
        self.assertEqual(0, d.minutes)
        self.assertEqual(0, d.hours)
        self.assertEqual(0, d.days)
        self.assertEqual(0, d.months)
        self.assertEqual(0, d.years)

    def test_init_weeks_float(self):
        """GIVEN weeks=1 WHEN a Duration is created THEN correct values are stored"""
        d = Duration(weeks=1.1)

        self.assertEqual(1.1, d.weeks)  # "weeks" cannot be combined with other args

        self.assertEqual(0, d.seconds)
        self.assertEqual(0, d.minutes)
        self.assertEqual(0, d.hours)
        self.assertEqual(0, d.days)
        self.assertEqual(0, d.months)
        self.assertEqual(0, d.years)

    def test_init_negative_values(self):
        """GIVEN a negative value WHEN a Duration is created THEN a ValueError is raised"""
        # Negative values aren't allowed by ISO 8601
        self.assertRaises(ValueError, Duration, -1, 2, 3, 4, 5, 6)
        self.assertRaises(ValueError, Duration, 1, -2, 3, 4, 5, 6)
        self.assertRaises(ValueError, Duration, 1, 2, -3, 4, 5, 6)
        self.assertRaises(ValueError, Duration, 1, 2, 3, -4, 5, 6)
        self.assertRaises(ValueError, Duration, 1, 2, 3, 4, -5, 6)
        self.assertRaises(ValueError, Duration, 1, 2, 3, 4, 5, -6)
        self.assertRaises(ValueError, Duration, weeks=-7)

    def test_init_0_floats(self):
        """GIVEN a values of 0.0 WHEN a Duration is created THEN 0.0 is stored"""
        d = Duration(0.0, 0, 0.0, 0.0, 0.0, 0.0)

        self.assertEqual(0.0, d.seconds)
        self.assertIsInstance(d.seconds, float)
        self.assertEqual(0.0, d.minutes)
        self.assertIsInstance(d.minutes, float)
        self.assertEqual(0.0, d.hours)
        self.assertIsInstance(d.hours, float)
        self.assertEqual(0.0, d.days)
        self.assertIsInstance(d.days, float)
        self.assertEqual(0, d.months)
        self.assertIsInstance(d.months, int)
        self.assertEqual(0.0, d.years)
        self.assertIsInstance(d.years, float)

        d = Duration(weeks=0.0)
        self.assertEqual(0.0, d.weeks)
        self.assertIsInstance(d.weeks, float)

    def test_init_at_least_one_value_set(self):
        """GIVEN no arguments are given WHEN a Duration is created THEN a ValueError is raised"""
        self.assertRaises(ValueError, Duration)

    def test_init_float_months_rejected(self):
        """
        GIVEN `months` is a flot WHEN a Duration is created THEN a ValueError is raised

        (Decimal years and months are ambiguous, so not supported)
        """
        self.assertRaises(ValueError, Duration, months=0.5)


DURATION_ADDITION_TEST_CASES = [
    (Duration(1), Duration(1), Duration(2)),
    (Duration(1, 2, 3, 4, 5, 6), Duration(6, 5, 4, 3, 2, 1), Duration(7, 7, 7, 7, 7, 7)),
    (Duration(weeks=1), Duration(weeks=2), Duration(weeks=3)),
    # Weeks are converted to days when combined with anything other than weeks
    (Duration(1, 2, 3, 4, 5, 6), Duration(weeks=1), Duration(1, 2, 10, 4, 5, 6)),
    # Fractional amounts
    (Duration(years=0.5), Duration(years=0.5), Duration(years=1)),
    (Duration(days=0.5), Duration(days=0.5), Duration(days=1)),
    (Duration(hours=0.5), Duration(hours=0.5), Duration(hours=1)),
    (Duration(minutes=0.5), Duration(minutes=0.5), Duration(minutes=1)),
    (Duration(seconds=0.5), Duration(seconds=0.5), Duration(seconds=1)),
    (Duration(weeks=0.5), Duration(weeks=0.5), Duration(weeks=1)),
    (Duration(weeks=0.5), Duration(1, 2, 3, 4, 5, 6), Duration(1, 2, 6, 16, 5, 6)),

    # Overflowing fields
    (Duration(months=6), Duration(months=7), Duration(months=13)),
    (Duration(days=10), Duration(days=25), Duration(days=35)),
    (Duration(hours=20), Duration(hours=20), Duration(hours=40)),
    (Duration(minutes=59), Duration(minutes=59), Duration(minutes=118)),
    (Duration(seconds=59), Duration(seconds=59), Duration(seconds=118)),
    (Duration(weeks=123), Duration(weeks=321), Duration(weeks=444)),

    # DATETIME TEST CASES
    (Duration(1, 2, 3, 4, 5, 6), datetime(2003, 1, 1, 2, 3, 4), datetime(2004, 3, 4, 6, 8, 10)),
    (Duration(years=1), datetime(2003, 1, 1, 2, 3, 4), datetime(2004, 1, 1, 2, 3, 4)),
    (Duration(months=6), datetime(2003, 1, 1, 2, 3, 4), datetime(2003, 7, 1, 2, 3, 4)),
    (Duration(days=1), datetime(2003, 1, 1, 2, 3, 4), datetime(2003, 1, 2, 2, 3, 4)),
    (Duration(hours=12), datetime(2003, 1, 1, 2, 3, 4), datetime(2003, 1, 1, 14, 3, 4)),
    (Duration(minutes=50), datetime(2003, 1, 1, 2, 3, 4), datetime(2003, 1, 1, 2, 53, 4)),
    (Duration(seconds=30), datetime(2003, 1, 1, 2, 3, 4), datetime(2003, 1, 1, 2, 3, 34)),
    (Duration(weeks=1), datetime(2003, 1, 1, 2, 3, 4), datetime(2003, 1, 8, 2, 3, 4)),

    (Duration(months=25), datetime(2003, 1, 1, 2, 3, 4), datetime(2005, 2, 1, 2, 3, 4)),
    (Duration(days=400), datetime(2003, 1, 1, 2, 3, 4), datetime(2004, 2, 5, 2, 3, 4)),
    (Duration(hours=36), datetime(2003, 1, 1, 2, 3, 4), datetime(2003, 1, 2, 14, 3, 4)),
    (Duration(minutes=120), datetime(2003, 1, 1, 2, 3, 4), datetime(2003, 1, 1, 4, 3, 4)),
    (Duration(seconds=120), datetime(2003, 1, 1, 2, 3, 4), datetime(2003, 1, 1, 2, 5, 4)),
    (Duration(weeks=123), datetime(2003, 1, 1, 2, 3, 4), datetime(2005, 5, 11, 2, 3, 4)),

    (Duration(years=0.5), datetime(2003, 1, 1, 2, 3, 4), datetime(2003, 7, 2, 14, 3, 4)),
    (Duration(days=0.5), datetime(2003, 1, 1, 2, 3, 4), datetime(2003, 1, 1, 14, 3, 4)),
    (Duration(hours=0.5), datetime(2003, 1, 1, 2, 3, 4), datetime(2003, 1, 1, 2, 33, 4)),
    (Duration(minutes=0.5), datetime(2003, 1, 1, 2, 3, 4), datetime(2003, 1, 1, 2, 3, 34)),
    (Duration(seconds=0.5), datetime(2003, 1, 1, 2, 3, 4), datetime(2003, 1, 1, 2, 3, 4, 500000)),
    (Duration(weeks=0.5), datetime(2003, 1, 1, 2, 3, 4), datetime(2003, 1, 4, 14, 3, 4)),

    # TIMEDELTA TEST CASES
    (Duration(1, 2, 3, 4, 5, 6), timedelta(weeks=1, days=2, hours=3, minutes=4, seconds=5),
     Duration(1, 2, 12, 7, 9, 11)),
    (Duration(weeks=1), timedelta(weeks=1, days=2, hours=3, minutes=4, seconds=5),
     Duration(days=16, hours=3, minutes=4, seconds=5)),

    (Duration(1, 2, 3, 4, 5, 6), timedelta(weeks=1), Duration(1, 2, 10, 4, 5, 6)),
    (Duration(1, 2, 3, 4, 5, 6), timedelta(days=1), Duration(1, 2, 4, 4, 5, 6)),
    (Duration(1, 2, 3, 4, 5, 6), timedelta(hours=1), Duration(1, 2, 3, 5, 5, 6)),
    (Duration(1, 2, 3, 4, 5, 6), timedelta(minutes=1), Duration(1, 2, 3, 4, 6, 6)),
    (Duration(1, 2, 3, 4, 5, 6), timedelta(seconds=1), Duration(1, 2, 3, 4, 5, 7)),
    (Duration(1, 2, 3, 4, 5, 6), timedelta(milliseconds=500), Duration(1, 2, 3, 4, 5, 6.5)),
    (Duration(1, 2, 3, 4, 5, 6), timedelta(milliseconds=499), Duration(1, 2, 3, 4, 5, 6.499)),
    (Duration(1, 2, 3, 4, 5, 6), timedelta(microseconds=500000), Duration(1, 2, 3, 4, 5, 6.5)),
    (Duration(1, 2, 3, 4, 5, 6), timedelta(microseconds=499999), Duration(1, 2, 3, 4, 5, 6.499999)),

    (Duration(years=1), timedelta(weeks=1), Duration(years=1, days=7)),
    (Duration(months=25), timedelta(weeks=1), Duration(months=25, days=7)),
    (Duration(days=400), timedelta(days=1), Duration(days=401)),
    (Duration(hours=36), timedelta(hours=35), Duration(hours=71)),
    (Duration(minutes=120), timedelta(minutes=66), Duration(hours=3, minutes=6)),
    (Duration(seconds=120), timedelta(seconds=321), Duration(minutes=7, seconds=21)),
    (Duration(seconds=1), timedelta(milliseconds=2000), Duration(seconds=3)),
    (Duration(seconds=1), timedelta(milliseconds=1499), Duration(seconds=2.499)),
    (Duration(seconds=1), timedelta(milliseconds=1500), Duration(seconds=2.5)),
    (Duration(seconds=1), timedelta(microseconds=1000000), Duration(seconds=2)),
    (Duration(seconds=1), timedelta(microseconds=500000), Duration(seconds=1.5)),
    (Duration(seconds=1), timedelta(microseconds=490000), Duration(seconds=1.49)),

    (Duration(weeks=1), timedelta(weeks=1), Duration(weeks=2)),
    (Duration(weeks=1), timedelta(days=1), Duration(days=8)),
    (Duration(weeks=1), timedelta(hours=35), Duration(days=8, hours=11)),
    (Duration(weeks=1), timedelta(minutes=66), Duration(days=7, hours=1, minutes=6)),
    (Duration(weeks=1), timedelta(seconds=321), Duration(days=7, minutes=5, seconds=21)),
    (Duration(weeks=1), timedelta(milliseconds=2000), Duration(days=7, seconds=2)),
    (Duration(weeks=1), timedelta(milliseconds=1499), Duration(days=7, seconds=1.499)),
    (Duration(weeks=1), timedelta(milliseconds=1500), Duration(days=7, seconds=1.5)),
    (Duration(weeks=1), timedelta(microseconds=1000000), Duration(days=7, seconds=1)),
    (Duration(weeks=1), timedelta(microseconds=500000), Duration(days=7, seconds=0.5)),
    (Duration(weeks=1), timedelta(microseconds=490000), Duration(days=7, seconds=0.49)),

    (Duration(days=0.5), timedelta(weeks=1), Duration(days=7.5)),
    (Duration(hours=0.5), timedelta(weeks=1), Duration(days=7, hours=0.5)),
    (Duration(minutes=0.5), timedelta(weeks=1), Duration(days=7, minutes=0.5)),
    (Duration(seconds=0.5), timedelta(weeks=1), Duration(days=7, seconds=0.5)),
    (Duration(years=0.5), timedelta(weeks=1), Duration(days=189, hours=12)),
    (Duration(weeks=0.5), timedelta(weeks=1), Duration(weeks=1.5)),
]


@pytest.mark.parametrize("left_operand,right_operand,expected_result", DURATION_ADDITION_TEST_CASES, ids=repr)
def test_duration__add__(left_operand, right_operand, expected_result):
    """
    GIVEN operands A and B WHEN B is added to A THEN the expected result is returned.
    i.e. it tests what happens when we do `a_duration + an_object`.
    This tests the addition (`__add__`) method
    """
    assert left_operand + right_operand == expected_result


@pytest.mark.parametrize(
    # For these tests, we want to switch the transpose the operands, so they're reversed and use the __radd__ method
    # (at least where __add__ doesn't support the right operand)
    "left_operand,right_operand,expected_result", DURATION_ADDITION_TEST_CASES, ids=repr)
def test_duration__radd__(left_operand, right_operand, expected_result):
    """
    GIVEN operands A and B WHEN A is added to B THEN the expected result is returned.
    i.e. it tests what happens when we do `an_object + a_duration`.
    This tests the reflected addition (`__radd__`) method
    """
    assert right_operand + left_operand == expected_result


@pytest.mark.parametrize("left_operand,right_operand,expected_result", [
    (Duration(1), Duration(1), Duration(0)),
    (Duration(1, 2, 3, 4, 5, 6), Duration(1, 2, 3, 4, 5, 6), Duration(0, 0, 0, 0, 0, 0)),
    (Duration(7, 7, 7, 7, 7, 7), Duration(6, 5, 4, 3, 2, 1), Duration(1, 2, 3, 4, 5, 6)),
    (Duration(weeks=2), Duration(weeks=1), Duration(weeks=1)),
    # Weeks are converted to days when combined with anything other than weeks
    (Duration(1, 2, 10, 4, 5, 6), Duration(weeks=1), Duration(1, 2, 3, 4, 5, 6)),
    # Fractional amounts
    (Duration(years=0.5), Duration(years=0.5), Duration(years=0)),
    (Duration(days=0.5), Duration(days=0.5), Duration(days=0)),
    (Duration(hours=0.5), Duration(hours=0.5), Duration(hours=0)),
    (Duration(minutes=0.5), Duration(minutes=0.5), Duration(minutes=0)),
    (Duration(seconds=0.5), Duration(seconds=0.5), Duration(seconds=0)),
    (Duration(weeks=0.5), Duration(weeks=0.5), Duration(weeks=0)),

    # Overflowing fields
    (Duration(months=7), Duration(months=6), Duration(months=1)),
    (Duration(days=25), Duration(days=10), Duration(days=15)),
    (Duration(hours=40), Duration(hours=20), Duration(hours=20)),
    (Duration(minutes=59), Duration(minutes=59), Duration(minutes=0)),
    (Duration(seconds=59), Duration(seconds=59), Duration(seconds=0)),
    (Duration(weeks=321), Duration(weeks=123), Duration(weeks=198)),

    # TIMEDELTA TEST CASES
    (Duration(1, 2, 9, 4, 5, 6), timedelta(weeks=1, days=2, hours=3, minutes=4, seconds=5),
     Duration(1, 2, 0, 1, 1, 1)),
    (Duration(weeks=2), timedelta(weeks=1, days=2, hours=3, minutes=4, seconds=5),
     Duration(days=4, hours=20, minutes=55, seconds=55)),

    (Duration(1, 2, 7, 4, 5, 6), timedelta(weeks=1), Duration(1, 2, 0, 4, 5, 6)),
    (Duration(1, 2, 3, 4, 5, 6), timedelta(days=1), Duration(1, 2, 2, 4, 5, 6)),
    (Duration(1, 2, 3, 4, 5, 6), timedelta(hours=1), Duration(1, 2, 3, 3, 5, 6)),
    (Duration(1, 2, 3, 4, 5, 6), timedelta(minutes=1), Duration(1, 2, 3, 4, 4, 6)),
    (Duration(1, 2, 3, 4, 5, 6), timedelta(seconds=1), Duration(1, 2, 3, 4, 5, 5)),
    (Duration(1, 2, 3, 4, 5, 6), timedelta(milliseconds=500), Duration(1, 2, 3, 4, 5, 5.5)),
    (Duration(1, 2, 3, 4, 5, 6), timedelta(milliseconds=501), Duration(1, 2, 3, 4, 5, 5.499)),
    (Duration(1, 2, 3, 4, 5, 6), timedelta(microseconds=500000), Duration(1, 2, 3, 4, 5, 5.5)),
    (Duration(1, 2, 3, 4, 5, 6), timedelta(microseconds=500001), Duration(1, 2, 3, 4, 5, 5.499999)),

    (Duration(years=1), timedelta(weeks=1), Duration(days=358)),
    (Duration(days=400), timedelta(days=1), Duration(days=399)),
    (Duration(hours=36), timedelta(hours=35), Duration(hours=1)),
    (Duration(minutes=120), timedelta(minutes=66), Duration(minutes=54)),
    (Duration(seconds=3), timedelta(milliseconds=2000), Duration(seconds=1)),
    (Duration(seconds=2), timedelta(milliseconds=1499), Duration(seconds=0.5009999999999999)),
    (Duration(seconds=2), timedelta(milliseconds=1500), Duration(seconds=0.5)),
    (Duration(seconds=2), timedelta(microseconds=1000000), Duration(seconds=1)),
    (Duration(seconds=1), timedelta(microseconds=500000), Duration(seconds=0.5)),
    (Duration(seconds=1), timedelta(microseconds=490000), Duration(seconds=0.51)),

    (Duration(weeks=1), timedelta(weeks=1), Duration(weeks=0)),
    (Duration(weeks=1), timedelta(days=1), Duration(days=6)),
    (Duration(weeks=1), timedelta(hours=35), Duration(days=5, hours=13)),
    (Duration(weeks=1), timedelta(minutes=66), Duration(days=6, hours=22, minutes=54)),
    (Duration(weeks=1), timedelta(seconds=321), Duration(days=6, hours=23, minutes=54, seconds=39)),
    (Duration(weeks=1), timedelta(milliseconds=2000), Duration(days=6, hours=23, minutes=59, seconds=58)),
    (Duration(weeks=1), timedelta(milliseconds=1499), Duration(days=6, hours=23, minutes=59, seconds=58.501)),
    (Duration(weeks=1), timedelta(milliseconds=1500), Duration(days=6, hours=23, minutes=59, seconds=58.5)),
    (Duration(weeks=1), timedelta(microseconds=1000000), Duration(days=6, hours=23, minutes=59, seconds=59)),
    (Duration(weeks=1), timedelta(microseconds=500000), Duration(days=6, hours=23, minutes=59, seconds=59.5)),
    (Duration(weeks=1), timedelta(microseconds=490000), Duration(days=6, hours=23, minutes=59, seconds=59.51)),

    (Duration(days=7.5), timedelta(weeks=1), Duration(days=0.5)),
    (Duration(hours=168.5), timedelta(weeks=1), Duration(hours=0.5)),
    (Duration(minutes=10080.5), timedelta(weeks=1), Duration(minutes=0.5)),
    (Duration(seconds=604800.5), timedelta(weeks=1), Duration(seconds=0.5)),
    (Duration(weeks=1.5), timedelta(weeks=1), Duration(weeks=0.5)),
], ids=repr)
def test_duration__sub__(left_operand, right_operand, expected_result):
    """
    GIVEN operands A and B WHEN B is subtracted from A THEN the expected result is returned.
    i.e. it tests what happens when we do `a_duration - an_object`.
    This tests the subtraction (`__sub__`) method
    """
    assert left_operand - right_operand == expected_result


@pytest.mark.parametrize(
    # For these tests, we want to switch the transpose the operands, so they're reversed and use the __radd__ method
    # (at least where __add__ doesn't support the right operand)
    "left_operand,right_operand,expected_result", [
        # DATETIME TEST CASES
        (datetime(2003, 1, 1, 2, 3, 4), Duration(1, 2, 3, 4, 5, 6), datetime(2001, 10, 28, 21, 57, 58)),

        (datetime(2003, 1, 1, 2, 3, 4), Duration(years=1), datetime(2002, 1, 1, 2, 3, 4)),
        (datetime(2003, 1, 1, 2, 3, 4), Duration(months=6), datetime(2002, 7, 1, 2, 3, 4)),
        (datetime(2003, 1, 1, 2, 3, 4), Duration(days=1), datetime(2002, 12, 31, 2, 3, 4)),
        (datetime(2003, 1, 1, 2, 3, 4), Duration(hours=12), datetime(2002, 12, 31, 14, 3, 4)),
        (datetime(2003, 1, 1, 2, 3, 4), Duration(minutes=50), datetime(2003, 1, 1, 1, 13, 4)),
        (datetime(2003, 1, 1, 2, 3, 4), Duration(seconds=30), datetime(2003, 1, 1, 2, 2, 34)),
        (datetime(2003, 1, 1, 2, 3, 4), Duration(weeks=1), datetime(2002, 12, 25, 2, 3, 4)),

        (datetime(2003, 1, 1, 2, 3, 4), Duration(months=25), datetime(2000, 12, 1, 2, 3, 4)),
        (datetime(2003, 1, 1, 2, 3, 4), Duration(days=400), datetime(2001, 11, 27, 2, 3, 4)),
        (datetime(2003, 1, 1, 2, 3, 4), Duration(hours=36), datetime(2002, 12, 30, 14, 3, 4)),
        (datetime(2003, 1, 1, 2, 3, 4), Duration(minutes=120), datetime(2003, 1, 1, 0, 3, 4)),
        (datetime(2003, 1, 1, 2, 3, 4), Duration(seconds=120), datetime(2003, 1, 1, 2, 1, 4)),
        (datetime(2003, 1, 1, 2, 3, 4), Duration(weeks=123), datetime(2000, 8, 23, 2, 3, 4)),

        (datetime(2003, 1, 1, 2, 3, 4), Duration(years=0.5), datetime(2002, 7, 2, 14, 3, 4)),
        (datetime(2003, 1, 1, 2, 3, 4), Duration(days=0.5), datetime(2002, 12, 31, 14, 3, 4)),
        (datetime(2003, 1, 1, 2, 3, 4), Duration(hours=0.5), datetime(2003, 1, 1, 1, 33, 4)),
        (datetime(2003, 1, 1, 2, 3, 4), Duration(minutes=0.5), datetime(2003, 1, 1, 2, 2, 34)),
        (datetime(2003, 1, 1, 2, 3, 4), Duration(seconds=0.5), datetime(2003, 1, 1, 2, 3, 3, 500000)),
        (datetime(2003, 1, 1, 2, 3, 4), Duration(weeks=0.5), datetime(2002, 12, 28, 14, 3, 4)),

        # TIMEDELTA TEST CASES
        (timedelta(weeks=1, days=2, hours=4, minutes=5, seconds=6), Duration(0, 0, 3, 4, 5, 6), Duration(days=6)),
        (timedelta(weeks=2, days=2, hours=3, minutes=4, seconds=5), Duration(weeks=2),
         Duration(days=2, hours=3, minutes=4, seconds=5)),
        (timedelta(weeks=2, days=2, hours=3, minutes=4, seconds=5), Duration(days=2),
         Duration(days=14, hours=3, minutes=4, seconds=5)),
        (timedelta(weeks=2, days=2, hours=3, minutes=4, seconds=5), Duration(hours=2),
         Duration(days=16, hours=1, minutes=4, seconds=5)),
        (timedelta(weeks=2, days=2, hours=3, minutes=4, seconds=5), Duration(minutes=2),
         Duration(days=16, hours=3, minutes=2, seconds=5)),
        (timedelta(weeks=2, days=2, hours=3, minutes=4, seconds=5), Duration(seconds=2),
         Duration(days=16, hours=3, minutes=4, seconds=3)),

        (timedelta(weeks=2), Duration(0, 0, 7, 4, 5, 6), Duration(days=6, hours=19, minutes=54, seconds=54)),
        (timedelta(days=4), Duration(0, 0, 3, 4, 5, 6), Duration(hours=19, minutes=54, seconds=54)),
        (timedelta(hours=96), Duration(0, 0, 3, 4, 5, 6), Duration(hours=19, minutes=54, seconds=54)),
        (timedelta(minutes=5760), Duration(0, 0, 3, 4, 5, 6), Duration(hours=19, minutes=54, seconds=54)),
        (timedelta(seconds=345600), Duration(0, 0, 3, 4, 5, 6), Duration(hours=19, minutes=54, seconds=54)),
        (timedelta(seconds=1), Duration(seconds=0.5), Duration(seconds=0.5)),
        (timedelta(milliseconds=1000), Duration(seconds=0.5), Duration(seconds=0.5)),
        (timedelta(milliseconds=1000), Duration(seconds=0), Duration(seconds=1)),
        (timedelta(milliseconds=500), Duration(seconds=0.5), Duration(seconds=0)),
        (timedelta(milliseconds=500), Duration(seconds=0), Duration(seconds=0.5)),
        (timedelta(milliseconds=499), Duration(seconds=0.499), Duration(seconds=0)),
        (timedelta(milliseconds=499), Duration(seconds=0), Duration(seconds=0.499)),
        (timedelta(microseconds=500000), Duration(seconds=0), Duration(seconds=0.5)),
        (timedelta(microseconds=499999), Duration(seconds=0), Duration(seconds=0.499999)),

        (timedelta(weeks=52), Duration(weeks=1), Duration(days=357)),  # 52 weeks = 364 days, not 365!
        (timedelta(days=400), Duration(days=1), Duration(days=399)),
        (timedelta(hours=36), Duration(hours=35), Duration(hours=1)),
        (timedelta(minutes=120), Duration(minutes=66), Duration(minutes=54)),
        (timedelta(milliseconds=3000), Duration(seconds=2), Duration(seconds=1)),
        (timedelta(milliseconds=1499), Duration(seconds=1), Duration(seconds=0.4990000000000001)),
        (timedelta(milliseconds=2000), Duration(seconds=0.5), Duration(seconds=1.5)),
        (timedelta(microseconds=2000000), Duration(seconds=1), Duration(seconds=1)),
        (timedelta(microseconds=1000000), Duration(seconds=0.5), Duration(seconds=0.5)),
        (timedelta(microseconds=1000000), Duration(seconds=0.49), Duration(seconds=0.51)),

        (timedelta(weeks=1), Duration(days=6.5), Duration(days=0.5)),
        (timedelta(weeks=1), Duration(hours=167.5), Duration(hours=0.5)),
        (timedelta(weeks=1), Duration(minutes=10079.5), Duration(minutes=0.5)),
        (timedelta(weeks=1), Duration(seconds=604799.5), Duration(seconds=0.5)),
        (timedelta(weeks=1), Duration(weeks=0.5), Duration(weeks=0.5)),
    ],
    ids=repr)
def test_duration__rsub__(left_operand, right_operand, expected_result):
    """
    GIVEN operands A and B WHEN B is subtracted from A THEN the expected result is returned.
    i.e. it tests what happens when we do `an_object - a_duration`.
    This tests the reflected subtraction (`__radd__`) method
    """
    assert left_operand - right_operand == expected_result


@pytest.mark.parametrize("left_operand, right_operand", [
    (Duration(years=1), Duration(months=13)),
    (Duration(years=1), Duration(months=1)),

    # Can't convert from months-> days, due to variation in the length of month, so the following subtractions
    # can't be calculated
    (Duration(months=1), Duration(weeks=1)),
    (Duration(months=1), Duration(days=1)),
    (Duration(months=1), Duration(hours=1)),
    (Duration(months=1), Duration(minutes=1)),
    (Duration(months=1), Duration(seconds=1)),
    (Duration(months=1), timedelta(milliseconds=1)),
    (Duration(months=1), timedelta(microseconds=1)),

    (timedelta(weeks=1, days=2, hours=3, minutes=4, seconds=5), Duration(1, 2, 3, 4, 5, 6)),
    (Duration(days=1), timedelta(days=2)),
    (Duration(hours=1), timedelta(hours=2)),
    (Duration(minutes=1), timedelta(minutes=2)),
    (Duration(seconds=1), timedelta(seconds=2)),

    (Duration(seconds=120), timedelta(seconds=321)),

    (Duration(days=0.5), timedelta(weeks=1)),
    (Duration(hours=0.5), timedelta(weeks=1)),
    (Duration(minutes=0.5), timedelta(weeks=1)),
    (Duration(seconds=0.5), timedelta(weeks=1)),
    (Duration(weeks=0.5), timedelta(weeks=1)),
    (Duration(weeks=0.5), Duration(1, 2, 3, 5, 5, 6)),

], ids=repr)
def test_duration_invalid_subtractions(left_operand, right_operand):
    """
    GIVEN operands A and B WHEN B is subtracted from A THEN a ValueError is thrown.
    A subtraction is invalid when the resulting Duration object is invalid.
    In practice, this means it would result in a negative field, which is not allowed.
    This results in an exception being thrown by the Duration's __init__ when attempting to create the result of the
    calculation.
    """
    with pytest.raises(ValueError):
        left_operand - right_operand


@pytest.mark.parametrize("attr_name", ["seconds", "minutes", "hours", "days", "months", "years", "weeks"])
def test_duration_attrs_read_only(attr_name):
    """Test that attributes are read-only"""
    d = Duration(2, 3, 4, 5, 6, 7)
    pytest.raises(AttributeError, setattr, d, attr_name, 1)


@pytest.mark.parametrize("incompatible_kwarg", ["seconds", "minutes", "hours", "days", "months", "years"])
def test_duration_init_weeks_mutually_exclusive(incompatible_kwarg):
    """
    GIVEN weeks keyword argument is specified
    AND another keyword argument is specified
    WHEN Duration is created
    THEN ValueError is raised

    Put differently, if you use the weeks keyword argument, you can't use any of the other ones. This test will test
    what happens when you use 'weeks' along with each of the other keyword arguments.
    """
    # 0 is treated as a value for the purposes of this behaviour, as None is how we represent "not specified".
    # A 0 value will show up in the serialised string representation, whereas a None will not
    pytest.raises(ValueError, Duration, **{"weeks": 0, incompatible_kwarg: 0})


@pytest.mark.parametrize("dur,expected", [
    (Duration(seconds=1), Duration(seconds=1)),
    (Duration(minutes=1), Duration(minutes=1)),
    (Duration(hours=1), Duration(hours=1)),
    (Duration(days=1), Duration(days=1)),
    (Duration(weeks=1), Duration(weeks=1)),
    (Duration(months=1), Duration(months=1)),
    (Duration(years=1), Duration(years=1)),

    (Duration(seconds=60), Duration(minutes=1)),
    (Duration(minutes=60), Duration(hours=1)),
    (Duration(hours=24), Duration(days=1)),
    (Duration(days=7), Duration(weeks=1)),
    (Duration(days=14), Duration(weeks=2)),
    (Duration(days=365), Duration(years=1)),
    (Duration(months=12), Duration(years=1)),

    (Duration(seconds=61), Duration(minutes=1, seconds=1)),
    (Duration(minutes=61), Duration(hours=1, minutes=1)),
    (Duration(hours=25), Duration(days=1, hours=1)),
    (Duration(days=8), Duration(days=8)),
    (Duration(days=14, seconds=1), Duration(days=14, seconds=1)),
    (Duration(days=366), Duration(years=1, days=1)),
    (Duration(months=18), Duration(years=1, months=6)),

    (Duration(seconds=0.5), Duration(seconds=0.5)),
    (Duration(minutes=0.5), Duration(seconds=30)),
    (Duration(hours=0.5), Duration(minutes=30)),
    (Duration(days=0.5), Duration(hours=12)),
    (Duration(weeks=0.5), Duration(days=3, hours=12)),
    (Duration(weeks=1.5), Duration(days=10, hours=12)),
    # non-integer months not allowed
    (Duration(years=0.5), Duration(days=182, hours=12)),

    (Duration(days=1.5), Duration(days=1, hours=12)),
    (Duration(years=1.5), Duration(years=1, days=182, hours=12))
], ids=repr)
def test_duration_normalized(dur: Duration, expected: Duration):
    actual = dur.normalized()
    assert actual == expected
    # Also need to check individual fields,
    # since Duration.__eq__ treats equivalent values expressed differently as equal

    assert actual.years == expected.years
    assert actual.months == expected.months
    assert actual.days == expected.days
    assert actual.hours == expected.hours
    assert actual.minutes == expected.minutes
    assert actual.seconds == expected.seconds
    assert actual.weeks == expected.weeks


DURATION_STR_CONVERSION_TEST_CASES = [
    (Duration(3, 6, 4, 12, 30, 5), "P3Y6M4DT12H30M5S"),
    (Duration(1, 2, 10, 2, 30), "P1Y2M10DT2H30M"),
    (Duration(seconds=0), "PT0S"),
    (Duration(days=0), "P0D"),
    (Duration(days=23, hours=23), "P23DT23H"),
    (Duration(4), "P4Y"),
    (Duration(months=1), "P1M"),
    (Duration(minutes=1), "PT1M"),
    (Duration(days=0.5), "P0.5D"),
    (Duration(days=0.5), "P0,5D"),
    (Duration(hours=36), "PT36H"),
    (Duration(days=1, hours=12), "P1DT12H"),
    (Duration(days=2.3, hours=2.3), "P2.3DT2.3H"),
    (Duration(weeks=4), "P4W"),
    (Duration(weeks=1.5), "P1.5W"),
    (Duration(weeks=1.5), "P1,5W"),
    (Duration(weeks=0), "P0W"),
    (Duration(weeks=0.0), "P0.0W"),
]


@pytest.mark.parametrize("dur_obj,str_dur", DURATION_STR_CONVERSION_TEST_CASES)
def test_duration_parse_str_valid(dur_obj: Duration, str_dur: str):
    """Can we convert a valid ISO8601 duration string to a Duration object?"""
    assert Duration.parse_str(str_dur) == dur_obj


@pytest.mark.parametrize("dur_obj,str_dur", DURATION_STR_CONVERSION_TEST_CASES)
def test_duration_str_valid(dur_obj: Duration, str_dur: str):
    """Can we convert a Duration object to a valid ISO8601 string?"""
    # commas are valid as a separator, but we will always serialise using periods
    assert str(dur_obj) == str_dur.replace(",", ".")


@pytest.mark.parametrize(
    "invalid_str_dur", [
        "P3Y6M4W4DT12H30M5S",  # Can't have weeks (W) with anything else
        "3Y6M4W4DT12H30M5S",  # Must have a leading P
        "P3Y6M4W4D12H30M5S",  # T separator is required between Y/M/W/D and H/M/S parts
        "P-1D",  # Negatives not allowed
        "P3S6M4HT12D30M5Y",  # In the spec, order matters, so I won't take on the complexity of figuring it out
        # And now for some bad input values for good measure
        None,
        -1,
        ["P3Y6M4W4DT12H30M5S"],
        ["P", "3Y", "6M", "4W", "4D", "T", "12H", "30M", "5S"],
        "",  # Empty string is not a valid representation
    ],
    ids=lambda val: f"invalid_str_{val!r}"  # Fixes a test report issue due to empty string case
)
def test_duration_str_conversion_invalid(invalid_str_dur: str):
    """
    GIVEN an invalid string WHEN converting the string to a Duration object is attempted THEN a ValueError is raised
    """
    pytest.raises(ValueError, Duration.parse_str, invalid_str_dur)


@pytest.mark.parametrize("dur, expected_td", (
        (Duration(1, 2, 3, 4, 5, 6.07), timedelta(days=428, hours=4, minutes=5, seconds=6, microseconds=70000)),
        (Duration(years=1), timedelta(days=365)),
        (Duration(months=1), timedelta(days=30)),
        (Duration(days=9, hours=3, minutes=4, seconds=11.07),
         timedelta(days=9, hours=3, minutes=4, seconds=11, microseconds=70000)),

        (Duration(weeks=54), timedelta(weeks=54)),
        (Duration(weeks=1), timedelta(weeks=1)),
        (Duration(weeks=0.5), timedelta(weeks=0.5)),

        (Duration(days=428), timedelta(days=428)),
        (Duration(days=1), timedelta(days=1)),
        (Duration(days=0.75), timedelta(days=0.75)),

        (Duration(hours=48), timedelta(days=2)),
        (Duration(hours=1), timedelta(hours=1)),
        (Duration(hours=0.123), timedelta(hours=0.123)),

        (Duration(minutes=360), timedelta(hours=6)),
        (Duration(minutes=1), timedelta(minutes=1)),
        (Duration(minutes=0.5), timedelta(seconds=30)),

        (Duration(seconds=3600), timedelta(hours=1)),
        (Duration(seconds=1), timedelta(seconds=1)),
        (Duration(seconds=0.5), timedelta(milliseconds=500)),
        (Duration(seconds=54.321), timedelta(milliseconds=54321)),
        (Duration(seconds=0.0005), timedelta(microseconds=500)),
), ids=repr)
def test_duration_to_timedelta(dur: Duration, expected_td: timedelta):
    """GIVEN a Duration WHEN Duration.to_timedelta is called THEN the equivalent timedelta is returned"""
    assert dur.to_timedelta() == expected_td


@pytest.mark.parametrize("td, expected_dur", (
        (timedelta(weeks=1, days=2, hours=3, minutes=4, seconds=5, milliseconds=6000, microseconds=70000),
         Duration(days=9, hours=3, minutes=4, seconds=11.07)),

        (timedelta(weeks=1), Duration(weeks=1)),
        (timedelta(weeks=0.5), Duration(weeks=0.5)),
        (timedelta(days=1), Duration(days=1)),
        (timedelta(hours=1), Duration(hours=1)),
        (timedelta(minutes=1), Duration(minutes=1)),
        (timedelta(seconds=1), Duration(seconds=1)),
        (timedelta(microseconds=500), Duration(seconds=0.0005)),
        (timedelta(milliseconds=54321), Duration(seconds=54.321)),
), ids=repr)
def test_duration_from_timedelta(td, expected_dur):
    """GIVEN a timedelta WHEN Duration.from_timedelta is called THEN the equivalent Duration is returned"""
    assert Duration.from_timedelta(td) == expected_dur


@pytest.mark.parametrize("dur, expected_rd", (
        (Duration(1, 2, 3, 4, 5, 6.07),
         relativedelta(years=1, months=2, days=3, hours=4, minutes=5, seconds=6, microseconds=70000)),
        (Duration(years=1), relativedelta(years=1)),
        (Duration(months=1), relativedelta(months=1)),
        (Duration(days=3, hours=3, minutes=4, seconds=6.07),
         relativedelta(days=3, hours=3, minutes=4, seconds=6, microseconds=70000)),

        (Duration(weeks=54), relativedelta(weeks=54)),
        (Duration(weeks=1), relativedelta(weeks=1)),
        (Duration(weeks=0.5), relativedelta(days=3, hours=12)),

        (Duration(days=428), relativedelta(years=1, days=63)),
        (Duration(days=1), relativedelta(days=1)),
        (Duration(days=0.75), relativedelta(hours=18)),

        (Duration(hours=48), relativedelta(days=2)),
        (Duration(hours=1), relativedelta(hours=1)),
        (Duration(hours=0.25), relativedelta(minutes=15)),

        (Duration(minutes=360), relativedelta(hours=6)),
        (Duration(minutes=1), relativedelta(minutes=1)),
        (Duration(minutes=0.5), relativedelta(seconds=30)),

        (Duration(seconds=3600), relativedelta(hours=1)),
        (Duration(seconds=1), relativedelta(seconds=1)),
        (Duration(seconds=0.0005), relativedelta(microseconds=500)),
), ids=repr)
def test_duration_to_relativedelta(dur: Duration, expected_rd: relativedelta):
    """GIVEN a Duration WHEN Duration.to_relativedelta is called THEN the equivalent relativedelta is returned"""

    assert dur.to_relativedelta() == expected_rd


@pytest.mark.parametrize("rd, expected_dur", (
        (relativedelta(weeks=1, days=2, hours=3, minutes=4, seconds=5, microseconds=70000),
         Duration(days=9, hours=3, minutes=4, seconds=5.07)),

        (relativedelta(weeks=1), Duration(weeks=1)),
        (relativedelta(days=1), Duration(days=1)),
        (relativedelta(days=400), Duration(days=400)),
        (relativedelta(hours=1), Duration(hours=1)),
        (relativedelta(hours=36), Duration(hours=36)),
        (relativedelta(minutes=1), Duration(minutes=1)),
        (relativedelta(minutes=120), Duration(minutes=120)),
        (relativedelta(seconds=1), Duration(seconds=1)),
        (relativedelta(seconds=180), Duration(seconds=180)),
        (relativedelta(microseconds=500), Duration(seconds=0.0005)),
        (relativedelta(microseconds=4255000), Duration(seconds=4.255)),
), ids=repr)
def test_duration_from_relativedelta(rd: relativedelta, expected_dur: Duration):
    """GIVEN a relativedelta WHEN Duration.from_relativedelta is called THEN the equivalent Duration is returned"""
    assert Duration.from_relativedelta(rd) == expected_dur
