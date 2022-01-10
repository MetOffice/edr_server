import json

from tornado.web import HTTPError, RequestHandler


class QueryParameters(RequestHandler):
    def __init__(self) -> None:
        self._params_dict = {
            "coords": None,
            "datetime": None,
            "z": None,
            "parameter-name": None,
            "f": None,
            "crs": None,
        }

    def __getitem__(self, key):
        return self._params_dict[key]

    def __setitem__(self, key, value):
        self._params_dict[key] = value

    def keys(self):
        return self._params_dict.keys()

    def handle_parameters(self, key, values):
        if not len(values):
            value = None
        elif len(values) == 1:
            value, = values
        else:
            emsg = f"Expected exactly 1 parameter for {key!r}, got {len(values)}: {values}."
            raise ValueError(emsg)
        if value is not None:
            try:
                meth = getattr(self, f"_handle_{key.replace('-', '_')}")
            except AttributeError:
                self._handle_generic(key, value)
            else:
                meth(value)

    def _intervals(self, value):
        """
        Handle different definitions of multiple values or intervals for a parameter.

        Intervals can be one of the following:
          * `v`: a single value `v`,
          * `v1,v2,v3`: `n` comma-separated discrete values,
          * `Rn/v_start/interval`: repeating intervals (number, start and interval),
          * `v_start/v_end`: a range of all values from v_start to v_end.

        """
        if "," in value:
            result = value.split(",")
        elif "/" in value:
            if value.startswith("R"):
                n, start, interval = value.lstrip("R").split("/")
                result = {"n": n, "start": start, "interval": interval}
            else:
                start, end = value.split("/")
                result = {"start": start, "end": end}
        else:
            result = value
        return result

    def _handle_generic(self, key, value):
        """Just write a key/value pair to `self` without modification."""
        self[key] = value

    def _handle_bbox(self, value):
        """Bounding box for cube queries. Of form `xmin ymin, xmax ymax`."""
        key = "bbox"
        vmin, vmax = value.split(",")
        xmin, ymin = vmin.split(" ")
        xmax, ymax = vmax.split(" ")
        self[key] = {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}

    def _handle_coords(self, value):
        key = "coords"
        self[key] = value

    def _handle_crs(self, value):
        key = "crs"
        self[key] = value

    def _handle_datetime(self, value):
        key = "datetime"
        self[key] = self._intervals(value)

    def _handle_f(self, value):
        """Handle the query parameter `f` - the requested return type for the data."""
        key = "f"
        valid_types = ["json", "coveragejson"]
        if not len(value):
            value = "json"
        if value.lower() not in valid_types:
            HTTPError(415, f"Return type {value!r} is not supported.")
        self[key] = value

    def _handle_parameter_name(self, value):
        key = "parameter-name"
        self[key] = self._intervals(value)

    def _handle_width(self, value):
        """For unsupported radius queries."""
        raise NotImplementedError

    def _handle_width_units(self, value):
        """For unsupported radius queries."""
        raise NotImplementedError

    def _handle_z(self, value):
        """Handle the query parameter `z` - vertical coords."""
        key = "z"
        self[key] = self._intervals(value)


class _Handler(RequestHandler):
    """Generic handler for EDR queries."""
    def initialize(self):
        self.query_parameters = QueryParameters()

    def get(self, collection_name):
        """Handle a get request for data from EDR. Returned as JSON, unless the query specifies otherwise."""
        self.handle_parameters()
        self.write(f"Get {self.handler_type} request called for collection {collection_name!r}.")

    def handle_parameters(self):
        # print(self.get_query_arguments())
        for key in self.query_parameters.keys():
            param_vals = self.get_arguments(key)
            self.query_parameters.handle_parameters(key, param_vals)


class AreaHandler(_Handler):
    """Handle area requests."""
    handler_type = "area"
    def get(self, collection_name):
        """Handle a 'get area' request."""
        # Not implemented!
        raise HTTPError(501, f"Get {self.handler_type} request is not implemented.")


class CorridorHandler(_Handler):
    """Handle corridor requests."""
    handler_type = "corridor"
    def get(self, collection_name):
        """Handle a 'get corridor' request."""
        # Not implemented!
        raise HTTPError(501, f"Get {self.handler_type} request is not implemented.")


class CubeHandler(_Handler):
    """Handle cube requests."""
    handler_type = "cube"
    def get(self, collection_name):
        """Handle a 'get cube' request."""
        # Not implemented!
        raise HTTPError(501, f"Get {self.handler_type} request is not implemented.")


class ItemsHandler(_Handler):
    """Handle items requests."""
    handler_type = "items"


class LocationsHandler(_Handler):
    """Handle location requests."""
    handler_type = "location"


class PositionHandler(_Handler):
    """Handle position requests."""
    handler_type = "position"


class RadiusHandler(_Handler):
    """Handle radius requests."""
    handler_type = "radius"
    def get(self, collection_name):
        """Handle a 'get radius' request."""
        # Not implemented!
        raise HTTPError(501, f"Get {self.handler_type} request is not implemented.")


class TrajectoryHandler(_Handler):
    """Handle trajectory requests."""
    handler_type = "trajectory"
    def get(self, collection_name):
        """Handle a 'get trajectory' request."""
        # Not implemented!
        raise HTTPError(501, f"Get {self.handler_type} request is not implemented.")