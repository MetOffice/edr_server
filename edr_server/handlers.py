import json
from typing import Any
from urllib.parse import urljoin

from shapely import wkt
from tornado.web import HTTPError, RequestHandler


class QueryParameters(object):
    def __init__(self):
        self._params_dict = {}

    def __getitem__(self, key):
        return self._params_dict[key]

    def __setitem__(self, key, value):
        self._params_dict[key] = value

    def __repr__(self):
        return repr(self._params_dict)

    def __str__(self):
        return str(self._params_dict)

    def keys(self):
        return self._params_dict.keys()

    def values(self):
        return self._params_dict.values()

    def handle_parameter(self, key, values):
        """
        Handle an individual query parameter (`key`/`values` pair) from the query string.

        """
        value = None if not len(values) else values[0]
        if key == "f":
            # We always need to handle the return type `f` to make sure we have a default.
            self._handle_f(key, value)
        elif value is not None:
            try:
                meth = getattr(self, f"_handle_{key.replace('-', '_')}")
            except AttributeError:
                meth = self._handle_generic
            meth(key, value)

    def _intervals(self, value):
        """
        Handle different definitions of multiple values or intervals for a parameter.

        Intervals can be defined with one of the following:
          * `v`: a single value `v`,
          * `v1,v2,v3`: comma-separated discrete values `v1`, `v2` and `v3`,
          * `Rn/v_start/interval`: repeated interval (number, start and interval),
          * `v_start/v_end`: a range of all values from `v_start` to `v_end`.

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
        """Write a key/value pair to `self` without modification."""
        self[key] = value

    def _handle_bbox(self, key, value):
        """Bounding box for cube queries. Of form `xmin ymin, xmax ymax`."""
        vmin, vmax = value.split(",")
        xmin, ymin = vmin.split(" ")
        xmax, ymax = vmax.split(" ")
        self[key] = {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}

    def _handle_coords(self, key, value):
        """
        Coordinates of the location of the request, translated from
        well-known text (WKT) in the query string to a shapely object.

        """
        self[key] = wkt.loads(value)

    def _handle_datetime(self, key, value):
        self[key] = self._intervals(value)

    def _handle_f(self, key, value):
        """Handle the query parameter `f` - the requested return type for the data."""
        valid_types = ["json", "coveragejson"]
        if value is None:
            value = "json"
        if value.lower() not in valid_types:
            HTTPError(415, f"Return type {value!r} is not supported.")
        self[key] = value

    def _handle_parameter_name(self, key, value):
        self[key] = self._intervals(value)

    def _handle_z(self, key, value):
        """Handle the query parameter `z` - vertical coords."""
        self[key] = self._intervals(value)


class Handler(RequestHandler):
    """Generic handler for EDR queries."""
    def initialize(self, **kwargs):
        self.query_parameters = QueryParameters()

    def get(self, collection_name):
        """
        Handle a get request for data from EDR.
        Returned as JSON, unless the query specifies otherwise.

        """
        self.handle_parameters()

    def handle_parameters(self):
        """Translate EDR concepts in the query arguments into standard Python objects."""
        for key in self.request.query_arguments.keys():
            param_vals = self.get_arguments(key)
            self.query_parameters.handle_parameter(key, param_vals)
        
        if self.query_parameters["f"] == "json":
            self.render_template()

    def render_template(self):
        """Render a templated EDR response with data relevant to this query."""
        template_file = f"{self.handler_type}.json"
        data = self._get_data()
        self.render(template_file, **data)

    def write_error(self, status_code: int, **kwargs: Any) -> None:
        self.set_header("Content-Type", "application/json")
        self.write({
            "code": self.get_status(),
            "description": self._reason
        })

    def reverse_url_full(self, name: str, *args: Any, **kwargs: Any):
        """
        Extend the functionality of `RequestHandler.reverse_url` to return the full URL
        rather than the URL relative to the host.

        Reference: https://stackoverflow.com/a/39612115/6676985.

        """
        host = "{protocol}://{host}".format(**vars(self.request))
        return urljoin(host, self.reverse_url(name, *args, **kwargs))


class RootHandler(Handler):
    """Handle capabilities requests to the root of the server."""
    handler_type = "capabilities"
    def get(self):
        super().get("")

    def _get_data(self):
        return {
            "title": "A nonsense example",
            "description": "This is a nonsense example of templating a capabilities request.",
            "links_api_href": self.reverse_url_full("api").rstrip("?"),
            "links_conformance_href": self.reverse_url_full("conformance").rstrip("?"),
            "links_collections_href": self.reverse_url_full("collections").rstrip("?"),
            "keywords": ["Example", "Nonsense"],
            "provider_name": "Galadriel",
            "provider_url": None,
            "contact_email": "nonsense@example.com",
            "contact_phone": "07987 654321",
            "contact_fax": None,
            "contact_hours": "9 til 5",
            "contact_instructions": "Don't",
            "contact_address": "Over there",
            "contact_postcode": "ZZ99 9ZZ",
            "contact_city": "Neverland",
            "contact_state": "",
            "contact_country": "Wakanda",
        }


class AreaHandler(Handler):
    """Handle area requests."""
    handler_type = "area"
    def get(self, collection_name):
        """Handle a 'get area' request."""
        # Not implemented!
        raise HTTPError(501, f"Get {self.handler_type} request is not implemented.")


class CorridorHandler(Handler):
    """Handle corridor requests."""
    handler_type = "corridor"
    def get(self, collection_name):
        """Handle a 'get corridor' request."""
        # Not implemented!
        raise HTTPError(501, f"Get {self.handler_type} request is not implemented.")


class CubeHandler(Handler):
    """Handle cube requests."""
    handler_type = "cube"
    def get(self, collection_name):
        """Handle a 'get cube' request."""
        # Not implemented!
        raise HTTPError(501, f"Get {self.handler_type} request is not implemented.")


class ItemsHandler(Handler):
    """Handle items requests."""


class LocationsHandler(Handler):
    """Handle location requests."""


class PositionHandler(Handler):
    """Handle position requests."""


class RadiusHandler(Handler):
    """Handle radius requests."""
    handler_type = "radius"
    def get(self, collection_name):
        """Handle a 'get radius' request."""
        # Not implemented!
        raise HTTPError(501, f"Get {self.handler_type} request is not implemented.")


class TrajectoryHandler(Handler):
    """Handle trajectory requests."""
    handler_type = "trajectory"
    def get(self, collection_name):
        """Handle a 'get trajectory' request."""
        # Not implemented!
        raise HTTPError(501, f"Get {self.handler_type} request is not implemented.")