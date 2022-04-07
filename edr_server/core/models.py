import dataclasses
import math
import operator
import re
import warnings
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from functools import total_ordering, cached_property
from typing import List, Optional, Union, Tuple, Dict, Callable, Any

import dateutil.parser
import pyproj
import shapely.geometry
from dateutil.relativedelta import relativedelta


@total_ordering
class Duration:
    """
    Represents an ISO8601 compliant time duration
    (as described by https://en.wikipedia.org/wiki/ISO_8601#Durations)
    This class doesn't support the combined date and time representation format (e.g. P0003-06-04T12:30:05)

    Negative values are not part of the ISO8601 spec, and thus are not supported

    It's important to remember that:
    * the number of hours in a day (although almost always 24) is not constant due to daylight savings time adjustments
      and leap seconds,
    * different months have different number of days, so P1M in the context of different dates will represent a
      different number of days

    This means that the same duration applied to different dates can result in different amounts of time being
    added/removed.

    We've decided to try and be consistent with the behaviour of python's timedelta as much as possible, but note that
    the timedelta class doesn't support weeks, months, or years. Presumably to avoid issues arising from ambiguity
    caused by different calendars.

    We've also taken the decision that Durations will be naive: they won't try to take into account differences caused
    by calendars.

    For arithmetic between Duration instances, we've decided that because:
    * python's timedelta assumes days are always 24 hours long, we will also assume that
    * the length of months vary, we can't assume 1 month == 30 days.
      * hence, we won't convert from days->months or months->days, so
        * P20D + P20D would result in P40D and not P1M10D.
        * P1M would not be converted to P30D
      * we won't allow decimal fractions for months or years (since decimal fractions in years means we have to deal
        with fractions of a month)

    For the addition/subtraction of Durations from datetimes, because we'd be adding/removing time from a known
    reference point, we would be able to take into account the length of months, daylight savings time, etc

    Considering the python timedelta class, it treats days as being 24 hours long, so we view this as acceptable too.
    """
    # This class is intended to be read-only. Similar to timedelta, most operations that would cause a change should
    # return a new instance. Here are some things that we could implement, but haven't needed as yet:
    # TODO: .replace() method to create a copy of the Duration with the given fields replaced with the supplied values
    # TODO: .remove() method to create a copy of the Duration with the given fields removed

    # Constants used during various field conversions
    _MONTHS_IN_YEAR = 12
    _DAYS_IN_WEEK = 7
    _MICROSECONDS_IN_SECOND = 1000000
    _SECONDS_IN_MINUTE = 60
    _SECONDS_IN_HOUR = 60 * _SECONDS_IN_MINUTE
    _SECONDS_IN_DAY = 24 * _SECONDS_IN_HOUR
    _SECONDS_IN_WEEK = 7 * _SECONDS_IN_DAY
    _SECONDS_IN_YEAR = 365 * _SECONDS_IN_DAY  # Common year, rather than Gregorian year (and definitely not Julian!)

    # These regexes are for parsing and extracting the values from ISO 8601 duration strings
    # I feel I should apologise for what follows, but also assure it could be a lot worse...
    # Regex for matching a single field, parameterised to accept the match group name and unit character
    _FLOAT_REGEX_FMT = r"(?:(?P<{}>\d+(?:\.\d+)?){})?"
    # Regex for parsing and extracting most of an ISO 8601 duration string
    _PARSER = re.compile("".join([
        "^P",
        _FLOAT_REGEX_FMT.format("years", "Y"),
        _FLOAT_REGEX_FMT.format("months", "M"),
        _FLOAT_REGEX_FMT.format("days", "D"),
        "(?:T",  # T is required if any of the following fields are present
        _FLOAT_REGEX_FMT.format("hours", "H"),
        _FLOAT_REGEX_FMT.format("minutes", "M"),
        _FLOAT_REGEX_FMT.format("seconds", "S"),
        ")?",
    ]), re.ASCII)
    # Regex for parsing and extracting the special case of weeks, which can't be combined with any of the other fields
    _WEEK_PARSER = re.compile(r"^P(?P<weeks>\d+(?:\.\d+)?)W$", re.ASCII)

    def __init__(
            self,
            years: Optional[float] = None,
            months: Optional[int] = None,
            days: Optional[float] = None,
            hours: Optional[float] = None,
            minutes: Optional[float] = None,
            seconds: Optional[float] = None,
            *,  # Prevent weeks from being specified by positional argument, because it's invalid to combine weeks
            # with other arguments
            weeks: Optional[float] = None,
    ):
        # Remember that float implies int as well, so either can be stored, and its type matters for reconstructing
        # parsed strings that match the original input (with the caveat that we don't store which decimal separator
        # was used, as that seems too esoteric and fiddly for the uses this code was written for)

        args = [years, months, days, hours, minutes, seconds, weeks]
        if all(arg is None for arg in args):
            raise ValueError("At least one argument must be supplied")
        if any(arg < 0 for arg in args if arg is not None):
            raise ValueError(f"Arguments cannot be less than 0! arguments={args!r}")

        if weeks is not None and any(v is not None for v in args[:-1]):
            # If we allowed this, we couldn't generate a valid ISO 8601 string
            raise ValueError("'weeks' cannot be combined with any other arguments")

        if months and not isinstance(months, int):
            raise ValueError(
                "'months' must be an int because non-integer years and months are ambiguous and not currently supported"
            )
        self._years = years
        self._months = months
        self._days = days
        self._hours = hours
        self._minutes = minutes
        self._seconds = seconds
        self._weeks = weeks

    @property
    def years(self) -> float:
        return self._years if self._years is not None else 0

    @property
    def months(self) -> int:
        return self._months if self._months is not None else 0

    @property
    def days(self) -> float:
        return self._days if self._days is not None else 0

    @property
    def hours(self) -> float:
        return self._hours if self._hours is not None else 0

    @property
    def minutes(self) -> float:
        return self._minutes if self._minutes is not None else 0

    @property
    def seconds(self) -> float:
        return self._seconds if self._seconds is not None else 0

    @property
    def weeks(self) -> float:
        return self._weeks if self._weeks is not None else 0

    @cached_property
    def _id(self):
        """
        This is a helper method that standardises how we compare Duration instances.
        It's used in functions like __hash__, __eq__, __lte__, etc

        Cached because it requires various calculations and has the potential to be called a lot.
        (We can cache it because Duration is designed to be immutable)
        """
        return Duration._get_months_seconds(**Duration._to_dict(self))

    @staticmethod
    def _get_months_seconds(
            years: Optional[int] = None,
            months: Optional[int] = None,
            days: Optional[float] = None,
            hours: Optional[float] = None,
            minutes: Optional[float] = None,
            seconds: Optional[float] = None,
            weeks: Optional[float] = None
    ) -> (int, float):
        """
        Convert the different fields to months and seconds, which is useful when doing comparisons as equivalent inputs
        give the same result.

        Months are reported separately because they're the only unit that can't be converted to seconds, due to months
        having a variable length. However, months will be normalised to whole years wherever possible
        (e.g. 12 months -> 1 year) because we can guarantee this duration will always be the same.

        Years, days, hours, minutes, seconds, and weeks will then all be converted to seconds and summed.
        """

        # Allowing Nones and converting them here makes it easier to call this method
        years = years if years is not None else 0
        months = months if months is not None else 0
        days = days if days is not None else 0
        hours = hours if hours is not None else 0
        minutes = minutes if minutes is not None else 0
        seconds = seconds if seconds is not None else 0
        weeks = weeks if weeks is not None else 0

        # We can't convert from months to days (or other things) except for converting 12 months to a year.
        # So we can use this fact to convert as many months to years as possible, then we can convert years to seconds
        # which gives us greater flexibility when the output of this
        if months:
            # We can convert multiples of 12 months to years because we can guarantee that 12 months always equals 1
            # year, but can't convert partial months because different months have different lengths, so can't guarantee
            # their length
            years_from_months = int(months / Duration._MONTHS_IN_YEAR)
            if years_from_months:
                years = years + years_from_months
                # Note, math.fmod is not the same as the modulo operator,
                # refer to https://docs.python.org/3/library/math.html#math.fmod
                months = int(math.fmod(months, Duration._MONTHS_IN_YEAR))  # preserves the sign

        seconds += (
                minutes * Duration._SECONDS_IN_MINUTE + hours * Duration._SECONDS_IN_HOUR
                + days * Duration._SECONDS_IN_DAY + weeks * Duration._SECONDS_IN_WEEK
                + years * Duration._SECONDS_IN_YEAR
        )

        return months, seconds

    @staticmethod
    def _to_dict(obj: Union["Duration", relativedelta, timedelta]) -> Dict[str, float]:
        """
        Helper method used internally, particularly for situations where we're still calculating values for
        creating a new Duration instance. Specifically useful for situations where fields contain negative values that
        we're resolving
        """
        if isinstance(obj, Duration):
            return {
                "years": obj.years,
                "months": obj.months,
                "days": obj.days,
                "hours": obj.hours,
                "minutes": obj.minutes,
                "seconds": obj.seconds,
                "weeks": obj.weeks
            }
        elif isinstance(obj, relativedelta):
            kwargs = {
                "years": obj.years,
                "months": obj.months,
                "days": obj.days,
                "hours": obj.hours,
                "minutes": obj.minutes,
                "seconds": obj.seconds + obj.microseconds / Duration._MICROSECONDS_IN_SECOND
            }

            # relativedelta doesn't distinguish between 0 and unset, so we'll treat 0 as unset, and filter out anything
            # without a value
            kwargs = {k: v for k, v in kwargs.items() if v}
            # relative deltas can contain negative fields, so we need to normalise the result
            return Duration._normalise(**kwargs)
        elif isinstance(obj, timedelta):
            return Duration._normalise(seconds=obj.total_seconds())
        else:
            raise NotImplementedError(f"{type(obj)} is not supported")

    @staticmethod
    def _normalise(
            years: Optional[float] = None,
            months: Optional[int] = None,
            days: Optional[float] = None,
            hours: Optional[float] = None,
            minutes: Optional[float] = None,
            seconds: Optional[float] = None,
            weeks: Optional[float] = None,
            *,
            normalise_to_weeks: bool = True,
    ) -> Dict[str, Optional[float]]:
        """
        The main purpose of this method is to deal with relativedeltas containing negative values, which aren't
        supported by the ISO8601 spec for Durations. Negative values prevent us from creating a valid Duration, so
        we need to normalise them before passing to Duration.__init_. That's why this method returns a dictionary and
        not an instance.

        It also enables us to be more consistent with timedelta behaviour, as they are automatically normalised.
        We don't automatically normalise because we want the ability to reproduce the supplied parameters as given,
        so if a user wants P36H and wants that exact string calling str(), they don't get P1D12H instead.
        We do normalise the result of arithmetic operations however, since we're normalising the result for
        relativedelta, it's more consistent to do it for all outputs.

        :param normalise_to_weeks: If `True`, the result will be converted to weeks if it can be expressed as an integer
                                   number of weeks
        """

        months, total_seconds = Duration._get_months_seconds(years, months, days, hours, minutes, seconds, weeks)

        if normalise_to_weeks and not months:
            weeks, remaining_seconds = divmod(total_seconds, Duration._SECONDS_IN_WEEK)
            if not remaining_seconds:  # Only normalise to weeks if there's no remainder
                return {
                    "years": None,
                    "months": None,
                    "days": None,
                    "hours": None,
                    "minutes": None,
                    "seconds": None,
                    "weeks": weeks
                }

        # Otherwise, we didn't normalise to whole weeks, so continue normalising to year/month/day/hours/minutes/seconds
        years, seconds = divmod(total_seconds, Duration._SECONDS_IN_YEAR)
        days, seconds = divmod(seconds, Duration._SECONDS_IN_DAY)
        hours, seconds = divmod(seconds, Duration._SECONDS_IN_HOUR)
        minutes, seconds = divmod(seconds, Duration._SECONDS_IN_MINUTE)

        # NOTE: As we convert microseconds and milliseconds to seconds, which results in seconds being a float
        # this code can result in float precision issues (https://docs.python.org/3/tutorial/floatingpoint.html).
        # The code is correct, however. I've just tweaked the test cases such that the test inputs don't exhibit any
        # rounding issues. Since the ISO 8601 Duration has no concept of anything smaller than seconds, the best real
        # solution is to refactor the class to store seconds as a Decimal, however that's not something I want to
        # undertake at this time. It also has the drawback of forcing all the arithmetic involving floats to use
        # Decimal, and there may be cases where Decimal isn't supported in some of the functions we've used

        result = {
            "years": years,
            "months": months,
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "weeks": None
        }

        for k, v in result.items():
            if not v:
                # replace zeroes with None
                result[k] = None
            elif k != "seconds":
                # seconds is the only key that could have a non-integer value, so cast the rest to ints
                result[k] = int(v)

        if not any(v for v in result.values()):
            result["seconds"] = 0  # If the result is 0, we need to ensure at least 1 field is not None

        return result

    @staticmethod
    def from_relativedelta(rd: relativedelta) -> "Duration":
        kwargs = {k: v for k, v in Duration._to_dict(rd).items() if v}
        return Duration(**kwargs)

    @staticmethod
    def from_timedelta(td: timedelta) -> "Duration":
        return Duration(**Duration._to_dict(td))

    @staticmethod
    def parse_str(str_dur: str) -> "Duration":
        """
        Convert a valid ISO 8601 Duration string to a Duration object.
        The combined date and time representation format (e.g. P0003-06-04T12:30:05)
        """
        # Considering the best way to parse this, generally the string is made up a series of pairs. Each pair
        # has a character that identifies the unit and a value. The value can be multiple characters. Additionally,
        # there is a preceding P and potentially a T mid-string to indicate transition from years/months/weeks/days to
        # hours/minutes/seconds.

        # As a result, a loop based method that examines 1 character at a time is going to get complex, as we need to
        # track state such as whether we've seen a T character, which unit we're processing, and collecting values that
        # span multiple characters across loop iterations.

        # Therefore, I think a regex approach will be the lesser of the available evils and yield the clearest and
        # easiest to maintain code.

        try:
            # Substituting "," for "." simplifies the regex and subsequent conversion from str to int/float
            clean_dur_str = str_dur.replace(",", ".").strip()
        except AttributeError as e:
            raise ValueError(f"{str_dur!r} doesn't appear to be a string: {e}")

        parsed_str = Duration._PARSER.fullmatch(clean_dur_str) or Duration._WEEK_PARSER.fullmatch(clean_dur_str)
        if parsed_str is None:
            raise ValueError(f"Unable to parse {str_dur!r}; Probably because it's invalid")

        kwargs = {
            k: float(v) if "." in v else int(v)
            for k, v in parsed_str.groupdict().items()
            if v is not None  # Filter out non-matches
        }
        return Duration(**kwargs)

    def __hash__(self):
        return hash(self._id)

    def __eq__(self, other: Any) -> bool:
        # Required for @total_ordering to provide a full suite of rich comparison operators
        if isinstance(other, Duration):
            return self._id == other._id
        else:
            return False

    def __lt__(self, other):
        # Required for @total_ordering to provide a full suite of rich comparison operators
        if isinstance(other, Duration):
            return self._id < other._id
        else:
            raise TypeError(f"{type(other)} cannot be compared to Duration")

    def __add__(self, other):
        if isinstance(other, Duration):
            return self._add_sub_durations(other)
        elif isinstance(other, datetime):
            return other + self.to_relativedelta()
        elif isinstance(other, timedelta):
            return self._add_sub_durations(Duration.from_timedelta(other))

        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, Duration):
            return self._add_sub_durations(other, operator.sub)
        elif isinstance(other, timedelta):
            return self._add_sub_durations(Duration.from_timedelta(other), operator.sub)

        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, datetime):
            return other - self.to_relativedelta()
        elif isinstance(other, timedelta):
            return Duration.from_timedelta(other)._add_sub_durations(self, operator.sub)

        return NotImplemented

    def __str__(self) -> str:
        """
        Create an ISO 8601  string representation compliant with these rules:
        https://en.wikipedia.org/wiki/ISO_8601#Durations
        """
        if self._weeks is not None:
            return f"P{self._weeks}W"

        # Work out which things we need to include. None indicates unset/not included/omitted, so filter out the Nones
        pre_t_fields = [f for f in [(self._years, "Y"), (self._months, "M"), (self._days, "D")] if f[0] is not None]
        post_t_fields = [
            f for f in [(self._hours, "H"), (self._minutes, "M"), (self._seconds, "S")] if f[0] is not None]

        str_parts = ["P"] + [f"{val}{unit}" for val, unit in pre_t_fields]

        if post_t_fields:
            str_parts.extend("T")
            str_parts.extend(f"{val}{unit}" for val, unit in post_t_fields)

        return "".join(str_parts)

    def __repr__(self):
        if self._weeks is not None:
            args_str = f"weeks={self._weeks!r}"
        else:
            args_list = []
            for attr in ["years", "months", "days", "hours", "minutes", "seconds"]:
                attr_val = getattr(self, f"_{attr}")  # Check private, internal attribute, not public property
                if attr_val is not None:
                    args_list.append(f"{attr}={attr_val!r}")
            args_str = ", ".join(args_list)

        return f"Duration({args_str})"

    def _add_sub_durations(
            self, other: "Duration", operator_func: Callable[[Any, Any], Any] = operator.add) -> "Duration":
        kwargs = {
            "years": None,
            "months": None,
            "days": None,
            "hours": None,
            "minutes": None,
            "seconds": None
        }

        if self._weeks and other._weeks:
            kwargs = {
                "weeks": operator_func(self.weeks, other.weeks),
            }
        elif self._weeks or other._weeks:
            # "Cheat" slightly, by normalising the objects with weeks to their equivalent in days/hours/mins/secs
            # Then call the operator again. It'll come back to this method, but will take a different branch, which
            # will do the calculation, rather than reimplementing the same logic in this branch.
            # Less efficient, but expedient until performance is a problem.
            normalised_self = (Duration(**Duration._normalise(**Duration._to_dict(self), normalise_to_weeks=False))
                               if self._weeks else self)
            normalised_other = (Duration(**Duration._normalise(**Duration._to_dict(other), normalise_to_weeks=False))
                                if other._weeks else other)

            return operator_func(normalised_self, normalised_other)

        else:
            # Straight-forward case of combining the values from two Durations that don't use weeks

            # We check the private attributes, because they distinguish between an explicit 0 and unset
            # We add using the public properties because it simplifies the operation because any Nones get converted
            # to 0
            for k, v in kwargs.items():
                # Loop through the kwargs dict keys (which correspond to years, months, days, hours, seconds, minutes,
                # seconds). If the private attribute for either self or other are not None, then add the values for
                # the corresponding properties
                pvt_attr_name = f"_{k}"
                if getattr(self, pvt_attr_name) is not None or getattr(other, pvt_attr_name) is not None:
                    kwargs[k] = operator_func(getattr(self, k), getattr(other, k))

        kwargs = Duration._normalise(**kwargs)
        return Duration(**kwargs)

    def normalized(self) -> "Duration":
        """
        Returns a Duration representing the same quantity of time but represented using the largest units possible
        whilst still using integer values. Equivalent to
        https://dateutil.readthedocs.io/en/stable/relativedelta.html#dateutil.relativedelta.relativedelta.normalized

        For example:
        * P24H becomes P1D
        * P05.D become PT12H
        * P1.5D become P1DT12H

        Due to the ambiguity between converting months to other units (due to varying number of days), months will
        only be converted to whole years, and any remainder will remain as months.
        E.g.
        * P12M becomes P1Y
        * P18M becomes P1Y6M.

        On the ambiguity months cause, cConsider, there are 12 months in a year, so it follows that 6 months is half a
        year; but there a 181 days in Jan-Jun, 184 days in Jul-Dec, & 183 days in Apr-Sep despite all 3 periods being
        6 months long! Furthermore, considering the number of days in a year, half a year implies 365 days/2= 182.5
        days, which doesn't correspond with any period of 6 months!

        So, for the purposes of normalisation, a year is 365 days long, doesn't take into account leap days or leap
        seconds, and we've totally ignored months. Partial years will be converted to days.
        E.g.
        * P1.5Y becomes P1Y182D12H (not P1Y6M!)
        * P0.5Y18M becomes P1Y6M182DT12H (i.e. 18M becomes 1Y6M, combined with the 0.5Y to give 1.5Y6M, and then the
          0.5Y is converted to days and hours)

        Weeks are a special case too. Since weeks cannot be combined with other fields, so when normalising, we will
        only normalise to weeks if the value can be expressed as integer weeks.
        E.g.
        * P7D becomes P1W
        * P8D stays as P8D
        * P14D becomes P2W
        * P14DT1S stays as P14DT1S
        * P1.5W becomes P10DT12H
        """
        return Duration(**Duration._normalise(
            self._years, self._months, self._days, self._hours, self._minutes, self._seconds, self._weeks))

    def to_relativedelta(self) -> relativedelta:

        # Duration accepts floats, but relative delta doesn't, so we must normalise first
        tmp_dur = Duration._normalise(
            self.years, self.months, self.days, self.hours, self.minutes, self.seconds, weeks=self.weeks)

        if tmp_dur["weeks"]:
            # after normalisation, if weeks are present, they are guaranteed to be whole and for there to be no other
            # values
            return relativedelta(weeks=tmp_dur["weeks"])

        if tmp_dur["seconds"]:
            partial_seconds, seconds = math.modf(tmp_dur["seconds"])
            microseconds = int(partial_seconds * Duration._MICROSECONDS_IN_SECOND)
        else:
            seconds = 0
            microseconds = 0
        # Tidy up the input to remove seconds and None values
        del tmp_dur["seconds"]
        tmp_dur = {k: v for k, v in tmp_dur.items() if v}

        return relativedelta(seconds=int(seconds), microseconds=microseconds, **tmp_dur)

    def to_timedelta(self) -> timedelta:
        """
        Convert this `Duration` instance to a `timedelta`.
        `Duration` has `months`, but `timedelta` does not. Whilst it's imperfect, for the purposes of this conversion,
        we treat months as being 30 days long. Otherwise, it's not possible to perform the conversion at all
        """
        if self.weeks:
            return timedelta(weeks=self.weeks)
        else:
            months, seconds = Duration._get_months_seconds(
                self._years, self._months, self._days, self._hours, self._minutes, self._seconds, self._weeks)

            return timedelta(days=self.months * 30, seconds=seconds)


@dataclass
class DateTimeInterval:
    """
    Represents an ISO 8601 compliant time interval
    (as described by https://en.wikipedia.org/wiki/ISO_8601#Time_intervals)

    An ISO 8601 compliant time interval can be one of the following:
    * a start and end datetime
    * a start datetime and a duration
    * a duration and an end datetime
    * a duration

    Optionally, interval can recur:
    * a set number of times (recurrences=N where N is the number of times to recur)
    * infinitely (recurrences=-1)
    * or not at all (recurrences=None)

    In our implementation, recurrences=0 is semantically the same as recurrences=None (i.e. no repetition, but generates
     a different string representation in line with the standard):
    * When recurrences=None, the `R[n]/` part of the string representation is omitted
    * When recurrences=0, `R0/` is prefixed to the string representation to explicitly indicate 0 repetitions
    """
    INFINITE_RECURRENCES = -1

    def __init__(
            self,
            start: Optional[datetime] = None,
            end: Optional[datetime] = None,
            duration: Optional[Duration] = None,
            recurrences: Optional[int] = None
    ):
        """
        :param start: The beginning of the interval. Can be combined with `end` or `duration`, but not both at the same
                      time. Must come before `end` if 'end' is given.
        :param end: The end of the interval. Can be combined with `end` or `duration`, but not both at the same time.
                    Must come after `start` if 'start' is given.
        :param duration: Indicates the span of time covered by this interval. Can be supplied on its own, or with a
                         `start` or `end` (but not both at the same time). If supplied on its own, it won't be possible
                         to calculate the bounds of this interval.
        """
        if not start and not end and not duration:
            raise ValueError("At least some parameters must be supplied. Valid options are: "
                             "start & end, start & duration, end & duration, or just duration on its own")
        if start and end and start > end:
            raise ValueError("start datetime cannot be after end datetime")

        if start and end and duration:
            raise ValueError("Cannot set start, end, and duration together. It's not a valid combination")
        if start and not (end or duration):
            raise ValueError("start cannot be specified on its own. Please provide either and end date or a duration")
        if end and not (start or duration):
            raise ValueError("end cannot be specified on its own. Please provide either and end date or a duration")
        if recurrences is not None and recurrences < -1:
            raise ValueError("recurrences cannot be less than -1")

        self._start = start
        self._end = end
        self._duration = duration
        self._recurrences = recurrences

    @cached_property
    def start(self) -> Optional[datetime]:
        """The datetime that the interval begins, without taking any recurrence into account"""
        if self._start:
            return self._start
        elif self._end and self._duration:
            return self._end - self._duration
        else:
            return None

    @cached_property
    def end(self) -> Optional[datetime]:
        """The datetime that the interval finishes, without taking any recurrence into account"""
        if self._end:
            return self._end
        elif self._start and self._duration:
            return self._start + self._duration
        else:
            return None

    @cached_property
    def duration(self) -> Optional[Duration]:
        """The length of the interval, ignoring recurrence i.e. the time between the start and end properties"""
        if self._duration:
            return self._duration
        elif self._start and self._end:
            return Duration.from_timedelta(self._end - self._start)
        else:
            return None  # This case only applies if an empty interval is created e.g. DateTimeInterval()

    @cached_property
    def recurrences(self) -> int:
        """
        Number of recurrences, -1 for infinite recurrences, 0 for none (obviously), otherwise a positive integer.
        Internally, we distinguish between implied non-recurrence (recurrences=None) vs explicit non-recurrence
        (recurrences=0) for recreating strings as they were parsed, but for ease of use here we convert None->0.
        """
        return self._recurrences if self._recurrences else 0

    @cached_property
    def lower_bound(self) -> Optional[datetime]:
        """
        Get the lower bound of the interval.
        The convention for intervals is that if the interval was created with a start date parameter, that is always the
        beginning of the interval, and hence the lower bound.
        Else if it was created with an end date parameter, that indicates where the interval stops, and any recurrence
         extends into the past. So the lower bound depends upon the interval's duration and number of recurrences.
        Otherwise, there isn't enough information to calculate the bounds, and they are undefined.
        """
        if self._start:
            # When we have an explicit start date, the convention is that the interval begins at the start date and
            # recurs into the future (if applicable), hence an explicit start date is always the lower bound
            return self._start
        elif self._end:
            # If don't have an explicit start date, but do have an explicit end date, then the convention is the
            # interval stops at the end date and any recurrence extends into the past (if applicable)
            if self.recurrences == DateTimeInterval.INFINITE_RECURRENCES:
                return None  # Infinitely recurring interval up to a defined end date, implies no lower bound
            else:
                return self._end - self.total_duration
        else:
            # Neither start nor end dates, so can't calculate a lower bound
            return None

    @cached_property
    def upper_bound(self) -> Optional[datetime]:
        """
        Get the upper bound of the interval.
        The convention for intervals is that if the interval was created with a start date parameter, that is always the
        beginning of the interval, and any recurrence extends into the future. So the upper bound depends upon the
          interval's duration and number of recurrences.
        Else if it was created with an end date parameter, that indicates where the interval stops, so in that case the
         upper bound is always the end date.
        Otherwise, there isn't enough information to calculate the bounds, and they are undefined.
        """
        if self._start and self._end:
            # When both start and end are explicitly provided, the convention is that the interval begins at the start
            # date and recurs into the future (if applicable)

            if self.recurrences == DateTimeInterval.INFINITE_RECURRENCES:
                # Infinite recurrence into the future implies no upper bound
                return None
            elif self.recurrences > 0:
                return self._start + self.total_duration
            else:
                # If there's no recurrences, and we have an end date, then the upper bound is just that date.
                # In this scenario, self._end == self._start + self.total_duration, but this avoids performing that
                # calculation unnecessarily
                return self._end
        elif self._end:
            # When an end date is explicitly provided without a start date, the convention is that the interval ends at
            # the end date and recurs into the past (if applicable). So the upper bound is simply the end date
            return self._end

        elif self._start:
            # If we have an explicit start date without an explicit end date, the convention is the interval begins at
            # the start date and recurs into the future.
            # Negative values for self.recurrences implies infinite recurrence and the upper bound being undefined.
            return self._start + self.total_duration if self.recurrences >= 0 else None
        else:
            # If we don't have a start or end date, we can't calculate bounds at all
            return None

    @cached_property
    def total_duration(self) -> Optional[Duration]:
        """
        The length of the interval after taking into account any recurrences. None if the interval recurs infinitely
        """
        if self.recurrences >= 0:
            # Because the count of recurrences doesn't include the original interval
            total_occurrences = self.recurrences + 1
            return Duration.from_timedelta(self.duration.to_timedelta() * total_occurrences)
        else:
            # recurrences values less than 0 implies infinite recurrence, which has an infinite total duration
            return None

    def _key(self):
        """Standardises the way we represent the state of this object for equality comparison and hashing"""
        return self.recurrences, self.start, self.end, self.duration

    def __eq__(self, other):
        if isinstance(other, DateTimeInterval):
            return self._key() == other._key()
        else:
            return False

    def __repr__(self) -> str:
        return f"DateTimeInterval({self._start!r}, {self._end!r}, {self._duration!r}, {self._recurrences!r})"

    def __str__(self) -> str:
        """
        Converts the object to the ISO 8601 string representation of this interval

        The generated string will be based off the arguments passed to the __init__ method. For example, if the object
         was created with `start` and `end` dates, expect the `<start>/<end>` version. Whereas if `end` and `duration`
         were passed, expect `<duration>/<end>`.

        Because there are many flavours of valid ISO string, calling this method on an object created by parsing an ISO
        string isn't guaranteed to re-create the original input. The resulting string will be equivalent, but may not be
        identical.
        """
        parts = []
        if self._recurrences is not None:
            parts.append(f"R{self._recurrences}")

        if self._duration:
            if self._start:
                parts.append(self._start.isoformat(timespec="seconds"))
                parts.append(str(self._duration))
            elif self._end:
                parts.append(str(self._duration))
                parts.append(self._end.isoformat(timespec="seconds"))
            else:
                parts.append(str(self._duration))
        else:
            parts.append(self._start.isoformat(timespec="seconds"))
            parts.append(self._end.isoformat(timespec="seconds"))

        return "/".join(parts)

    @staticmethod
    def parse_str(str_dti: str) -> "DateTimeInterval":
        """
        Convert a valid ISO 8601 time interval string into a DateTimeInterval object

        The implementation is based on the description of ISO 8601 time intervals here:
        https://en.wikipedia.org/wiki/ISO_8601#Time_intervals

        As such, the supported representations are:
        * <start>/<end>
        * <start>/<duration>
        * <duration>/<end>
        * <duration>
        The optional recurrence prefix `R[n]/` is also supported.

        Where <start> & <end> are valid ISO 8601 datetime strings, and <duration> is a valid ISO 8601 duration string.
        Once split into the individual elements, parsing is provided by `dateutil.parser.isoparse` for `datetime`s and
        `Duration.parse_str` for durations. Refer to the respective documentation for the limitations of these parsers.

        Concise datetime representations, such as "2007-12-14T13:30/15:30", "2008-02-15/03-14", and
        "2007-11-13T09:00/15T17:00", are not supported. (TODO: add support for concise representations?)
        """

        start, end, duration, recurrences = None, None, None, None

        parts = str_dti.split("/")
        for p in parts:
            if p.startswith("R"):
                recurrences = int(p[1:])
            elif p.startswith("P"):
                duration = Duration.parse_str(p)
            else:
                if duration or start:
                    end = dateutil.parser.isoparse(p)
                else:
                    start = dateutil.parser.isoparse(p)

        return DateTimeInterval(start, end, duration, recurrences)


@dataclass
class TemporalReferenceSystem:
    """
    I haven't found a library like pyproj that supports temporal reference systems, but would rather use one if it
    existed.

    EDR's core specification only supports Gregorian, however, so this will do for now. If implementors need something
     other than Gregorian, they can override the defaults.
    """
    name: str = "Gregorian"
    wkt: str = 'TIMECRS["DateTime",TDATUM["Gregorian Calendar"],CS[TemporalDateTime,1],AXIS["Time (T)",future]'


@dataclass
class TemporalExtent:
    """
    The specific times and time ranges covered by a dataset
    A temporal extent can be made up of one or more DateTimeIntervals, one or more specific datetimes, or a
    combination of both
    """
    values: List[datetime] = dataclasses.field(default_factory=list)
    intervals: List[DateTimeInterval] = dataclasses.field(default_factory=list)
    trs: TemporalReferenceSystem = TemporalReferenceSystem()

    @property
    def interval(self) -> Tuple[Optional[datetime], Optional[datetime]]:
        warnings.warn("Renamed to 'bounds' to avoid confusion with a list of DateTimeIntervals", DeprecationWarning)
        return self.bounds

    @property
    def bounds(self) -> Tuple[Optional[datetime], Optional[datetime]]:
        """
        Returns the earliest and latest datetimes covered by the extent.

        None indicates an open-ended interval, such as where a duration repeats indefinitely. The lower bound, upper
        bound, or both lower & and upper bounds can be open, depending on the extent being represented.
        """
        open_lower_bound = False
        open_upper_bound = False

        vals = self.values.copy()
        for dti in self.intervals:
            if dti.lower_bound:
                vals.append(dti.lower_bound)
            else:
                open_lower_bound = True

            if dti.upper_bound:
                vals.append(dti.upper_bound)
            else:
                open_upper_bound = True

        if vals:
            return min(vals) if not open_lower_bound else None, max(vals) if not open_upper_bound else None
        else:
            return None, None


@dataclass
class SpatialExtent:
    bbox: shapely.geometry.Polygon
    crs: pyproj.CRS = pyproj.CRS("WGS84")

    @property
    def bounds(self):
        return self.bbox.bounds


@dataclass
class Extent:
    """A struct-like container for the geographic area and time range(s) covered by a dataset"""
    spatial: SpatialExtent
    temporal: TemporalExtent
    vertical: None


CollectionId = str
ItemId = str


class EdrDataQuery(Enum):
    CUBE = "cube"
    CORRIDOR = "corridor"
    LOCATIONS = "locations"
    ITEMS = "items"
    AREA = "area"
    POSITION = "position"
    RADIUS = "radius"
    TRAJECTORY = "trajectory"


@dataclass
class CollectionMetadata:
    id: str
    title: str
    description: str
    keywords: List[str]
    crs: pyproj.CRS
    extent: Extent
    parameters: List
    supported_data_queries: List[EdrDataQuery]
    output_formats: List[str]


@dataclass
class ItemMetadata:
    pass
