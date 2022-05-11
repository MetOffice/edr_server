import dataclasses
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, NamedTuple, Generic, TypeVar

import pyproj
import shapely.geometry

from ._types_and_defaults import DEFAULT_CRS, DEFAULT_VRS, DEFAULT_TRS
from .time import DateTimeInterval


@dataclass
class TemporalReferenceSystem:
    """
    I haven't found a library like pyproj that supports temporal reference systems, but would rather use one if it
    existed.

    EDR's core specification only supports Gregorian, however, so this will do for now. If implementors need something
     other than Gregorian, they can override the defaults.

    Based on a portion of
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/extent.yaml
    """
    name: str = "Gregorian"
    wkt: pyproj.CRS = DEFAULT_TRS


T = TypeVar("T")


class ScalarBounds(NamedTuple, Generic[T]):
    lower: T
    upper: T


class SpatialBounds(NamedTuple):
    minx: float
    miny: float
    maxx: float
    maxy: float


@dataclass
class TemporalExtent:
    """
    The specific times and time ranges covered by a dataset
    A temporal extent can be made up of one or more DateTimeIntervals, one or more specific datetimes, or a
    combination of both

    Based on a portion of
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/extent.yaml
    """
    values: List[datetime] = dataclasses.field(default_factory=list)
    intervals: List[DateTimeInterval] = dataclasses.field(default_factory=list)
    trs: TemporalReferenceSystem = TemporalReferenceSystem()

    @property
    def interval(self) -> "ScalarBounds[Optional[datetime]]":
        """
        An alias to `bounds`. Maintained for consistency with the serialised JSON for an extent
        (i.e. the `temporal.interval` portion of the schema) which contains the upper and lower bound of the extent
        """
        return self.bounds

    @property
    def bounds(self) -> "ScalarBounds[Optional[datetime]]":
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
            lower_bound = min(vals) if not open_lower_bound else None
            upper_bound = max(vals) if not open_upper_bound else None
            return ScalarBounds(lower_bound, upper_bound)
        else:
            return ScalarBounds(None, None)


@dataclass
class SpatialExtent:
    """
    Based on a portion of
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/extent.yaml
    """
    bbox: shapely.geometry.Polygon
    crs: pyproj.CRS = DEFAULT_CRS

    @property
    def bounds(self) -> SpatialBounds:
        return self.bbox.bounds


@dataclass
class VerticalExtent:
    """"""
    values: List[float]
    vrs: pyproj.CRS = DEFAULT_VRS

    # TODO: Initially, we're only supporting the "list of vertical levels", but we'd like to support all 3 forms
    #       described here:
    #       Vertical level intervals that data in the collection is available at these can be defined as follows:
    #       * min level / max level (e.g. "2/100")
    #       * number of repetitions / min level / interval (e.g."R5/100/50")
    #       * list of vertical levels (e.g. "2",10,"80","100"}
    #       The value `null` is supported and indicates an open vertical interval.

    @property
    def interval(self) -> "List[ScalarBounds[float]]":
        """
        In the Core only a single time interval is supported. Extensions may support
        multiple intervals. If multiple intervals are provided, the union of the
        intervals describes the vertical extent.
        """
        return [self.bounds]

    @property
    def bounds(self) -> "ScalarBounds[float]":
        return ScalarBounds(min(self.values), max(self.values))


@dataclass
class Extents:
    """
    A struct-like container for the geographic area and time range(s) covered by a dataset
    Based on
    https://github.com/opengeospatial/ogcapi-environmental-data-retrieval/blob/546c338/standard/openapi/schemas/extent.yaml
    """
    spatial: SpatialExtent
    temporal: Optional[TemporalExtent]
    vertical: Optional[VerticalExtent]
