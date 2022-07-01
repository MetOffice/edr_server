import dataclasses
from dataclasses import dataclass
from datetime import datetime
from typing import Generic, List, NamedTuple, Optional, TypeVar

import shapely.geometry

from .crs import DEFAULT_CRS, DEFAULT_TRS, DEFAULT_VRS, CrsObject
from .time import DateTimeInterval

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
    trs: CrsObject = DEFAULT_TRS

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}("
                f"values={self.values!r}, intervals={self.intervals!r}, trs=pyproj.CRS({self.trs.to_wkt()!r}))")

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
    # TODO support multiple bounding boxes (https://github.com/ADAQ-AQI/edr_server/issues/31)
    bbox: shapely.geometry.Polygon
    crs: CrsObject = DEFAULT_CRS

    def __repr__(self):
        return f"{self.__class__.__name__}(shapely.wkt.loads({self.bbox.wkt!r}), pyproj.CRS({self.crs.to_wkt()!r}))"

    @property
    def bounds(self) -> SpatialBounds:
        return self.bbox.bounds


@dataclass
class VerticalExtent:
    """"""
    values: List[float]
    vrs: CrsObject = DEFAULT_VRS

    # TODO: Initially, we're only supporting the "list of vertical levels", but we'd like to support all 3 forms
    #       described here:
    #       Vertical level intervals that data in the collection is available at these can be defined as follows:
    #       * min level / max level (e.g. "2/100")
    #       * number of repetitions / min level / interval (e.g."R5/100/50")
    #       * list of vertical levels (e.g. "2",10,"80","100"}
    #       The value `null` is supported and indicates an open vertical interval.

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.values!r}, pyproj.CRS({self.vrs.to_wkt()!r}))"

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
    temporal: Optional[TemporalExtent] = None
    vertical: Optional[VerticalExtent] = None
