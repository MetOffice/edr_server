import json
from typing import Any, Dict, List
from urllib.parse import urljoin

from shapely import wkt
from tornado.escape import url_unescape
from tornado.gen import coroutine
from tornado.httpclient import AsyncHTTPClient
from tornado.web import HTTPError, RequestHandler

from edr_server.core.interface import EdrRequest
from edr_server.core.models.urls import EdrUrlResolver, URL
from edr_server.core.serialisation import EdrJsonEncoder


class QueryParameters(object):
    def __init__(self):
        self._params_dict = {}
        self._handle_f("f", None)  # Always set a return type.
        self._handle_crs("crs_details", None)  # Always set a CRS.

    def __getitem__(self, key):
        return self._params_dict[key]

    def __setitem__(self, key, value):
        self._params_dict[key] = value

    def __repr__(self):
        return repr(self._params_dict)

    def __str__(self):
        return str(self._params_dict)

    @property
    def parameters(self):
        return self._params_dict

    def get(self, key, default=None):
        result = default
        try:
            result = self.__getitem__(key)
        except KeyError:
            pass
        finally:
            return result

    def keys(self):
        return self._params_dict.keys()

    def values(self):
        return self._params_dict.values()

    def handle_parameter(self, key, values):
        """
        Handle an individual query parameter (`key`/`values` pair) from the query string.

        """
        value = None if not len(values) else url_unescape(values[0])
        if value is not None:
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
            result = {"values": value.split(",")}
        elif "/" in value:
            if value.startswith("R"):
                n, start, interval = value.lstrip("R").split("/")
                result = {"n": n, "start": start, "interval": interval}
            else:
                start, end = value.split("/")
                result = {"start": start, "end": end}
        else:
            result = {"value": value}
        return result

    def _handle_generic(self, key, value):
        """Write a key/value pair to `self` without modification."""
        self[key] = value

    def _handle_bbox(self, key, value):
        """Bounding box for cube queries. Of form `xmin ymin,xmax ymax`."""
        vmin, vmax = value.split(",")
        xmin, ymin = vmin.split(" ")
        xmax, ymax = vmax.split(" ")
        self[key] = {
            "xmin": float(xmin),
            "ymin": float(ymin),
            "xmax": float(xmax),
            "ymax": float(ymax),
        }

    def _handle_coords(self, key, value):
        """
        Coordinates of the location of the request, translated from
        well-known text (WKT) in the query string to a shapely object.

        """
        self[key] = wkt.loads(value)

    def _handle_crs(self, key, value):
        """Handle the query parameter `crs` - the coordinate reference system for the data."""
        if value is None:
            value = "WGS84"
        self[key] = value

    def _handle_datetime(self, key, value):
        self[key] = self._intervals(value)

    def _handle_f(self, key, value):
        """Handle the query parameter `f` - the requested return type for the data."""
        valid_types = ["json", "coveragejson"]
        if value is None:
            value = "json"
        if value.lower() not in valid_types:
            raise HTTPError(415, f"Return type {value!r} is not supported.")
        self[key] = value

    def _handle_parameter_name(self, key, value):
        self[key] = self._intervals(value)

    def _handle_z(self, key, value):
        """Handle the query parameter `z` - vertical coords."""
        self[key] = self._intervals(value)


class BaseRequestHandler(RequestHandler):
    """Extends tornado's RequestHandler in order to add some useful functionality that's common to all our Handlers"""

    url_resolver: EdrUrlResolver
    json_encoder: EdrJsonEncoder

    def initialize(self, **_kwargs):
        self.url_resolver = EdrUrlResolver(URL(f"{self.request.protocol}://{self.request.host}"))
        self.edr_request = EdrRequest(self.url_resolver)
        self.json_encoder = EdrJsonEncoder()

    def get_template_namespace(self) -> Dict[str, Any]:
        """
        The template namespace is the scope within which `tornado` renders templates.
        Overriding it like this allows us to add extra functionality to the namespace,
        notably adding the full URL reversal method `self.reverse_url_full`.

        """
        namespace = super().get_template_namespace()
        namespace["reverse_url_full"] = self.reverse_url_full
        return namespace

    def reverse_url_full(self, name: str, *args: Any, **kwargs: Dict[str, Any]):
        """
        Extend the functionality of `RequestHandler.reverse_url` to return the full URL
        rather than the URL relative to the host.

        Reference: https://stackoverflow.com/a/39612115/6676985.

        """
        host = "{protocol}://{host}".format(**vars(self.request))
        return urljoin(host, self.reverse_url(name, *args))

    def write_error(self, status_code: int, **kwargs: Any) -> None:
        self.set_header("Content-Type", "application/json")
        exc_info = kwargs.get("exc_info")
        if exc_info is not None:
            error_obj = exc_info[1]
            try:
                message = error_obj.log_message
            except AttributeError:
                message = f"{error_obj.__class__.__name__}: {error_obj}"
            self.write({
                "code": self.get_status(),
                "description": self._reason,
                "message": message,
            })
        else:
            self.write({
                "code": status_code,
                "description": self._reason,
                "message": kwargs["reason"],
            })


class Handler(BaseRequestHandler):
    """Generic handler for EDR queries."""

    collection_id: str
    query_parameters: QueryParameters
    handler_type: str

    def initialize(self, **kwargs):
        super().initialize(**kwargs)
        self.query_parameters = QueryParameters()

    def _get_render_args(self):
        """
        Request data from the data interface and form it into arguments to pass
        to `self.render_string` when rendering the response JSON.

        """
        raise NotImplementedError

    def _get_file(self):
        """Request data as a file download object from the data interface."""
        raise NotImplementedError

    def get(self, collection_id):
        """
        Handle a get request for data from EDR.
        Returned as JSON, unless the query specifies otherwise.

        """
        self.collection_id = collection_id
        self.handle_parameters()
        if self.query_parameters.get("f") == "json":
            self.render_template()
        elif self.query_parameters.get("f") in ["csv", "netcdf"]:
            self.get_file()
        else:
            raise HTTPError(501, f"Only JSON response type is implemented.")

    def handle_parameters(self):
        """Translate EDR concepts in the query arguments into standard Python objects."""
        for key in self.request.query_arguments.keys():
            param_vals = self.get_arguments(key)
            self.query_parameters.handle_parameter(key, param_vals)

    def render_template(self):
        """
        Render a templated EDR response with data relevant to this query.
        We dump and load the templated result to get inline JSON verification from the JSON library.

        """
        render_kwargs = self._get_render_args()
        fileformat = "covjson" if self.handler_type == "item" else "json"
        template_file = f"{self.handler_type}.{fileformat}"
        rendered_template = self.render_string(template_file, **render_kwargs)
        minified_rendered_template = json.dumps(json.loads(rendered_template)).encode("utf-8")
        self.write(minified_rendered_template)

    @coroutine
    def get_file(self):
        """
        Support downloading a file rather than returning a JSON response for this query.

        """
        if self.handler_type not in ["domain", "item"]:
            # Only handlers that return `Domain` type JSON can return data in any form.
            raise HTTPError(415, "File download request not supported by this query.")
        mime_type = self.query_parameters.get("f")
        if mime_type == "txt":
            content_type = "text/plain"
        else:
            content_type = f"application/{mime_type}"
        filename, url = self._get_file()
        self.set_header("Content-Type", content_type)
        self.set_header("Content-Disposition", f"attachment; filename={filename}")
        if url is not None:
            # File on remote (e.g. S3).
            def streaming_callback(chunk):
                self.write(chunk)
                self.flush()

            yield AsyncHTTPClient().fetch(url, streaming_callback=streaming_callback)
        else:
            # Local file to serve.
            with open(filename, "rb") as obfh:
                while True:
                    data = obfh.read(4096)
                    if not data:
                        break
                    self.write(data)
        self.finish()

    def write_error(self, status_code: int, **kwargs: Any) -> None:
        self.set_header("Content-Type", "application/json")
        exc_info = kwargs.get("exc_info")
        if exc_info is not None:
            error_obj = exc_info[1]
            try:
                message = error_obj.log_message
            except AttributeError:
                message = f"{error_obj.__class__.__name__}: {error_obj}"
            self.write({
                "code": self.get_status(),
                "description": self._reason,
                "message": message,
            })
        else:
            self.write({
                "code": status_code,
                "description": self._reason,
                "message": kwargs["reason"],
            })

    def reverse_url_full(self, name: str, *args: Any, **kwargs: Any):
        """
        Extend the functionality of `RequestHandler.reverse_url` to return the full URL
        rather than the URL relative to the host.

        Reference: https://stackoverflow.com/a/39612115/6676985.

        """
        host = "{protocol}://{host}".format(**vars(self.request))
        return urljoin(host, self.reverse_url(name, *args))


class _DomainOrFeatureHandler(Handler):
    """
    Superclass for any query handler that can return either `FeatureCollection`
    or `Domain` type JSON. This includes `Area`, `Radius` and `Position`.

    """

    def initialize(self, data_interface, **kwargs):
        super().initialize(**kwargs)
        self.data_interface = data_interface

    def get(self, collection_id):
        self.items_url = self.reverse_url_full("items_query", collection_id)
        super().get(collection_id)

    def _get_interface(self):
        provider_class = getattr(self.data_interface, self.__class__.__name__.replace("Handler", ""))
        return provider_class(
            self.collection_id,
            self.query_parameters.parameters,
            self.items_url
        )

    def _get_render_args(self) -> Dict:
        interface = self._get_interface()
        data, self.handler_type, error, error_code = interface.data()
        if data is None:
            if error is None:
                error = "No items found within specified coords."
                error_code = 404
            code = error_code if error_code is not None else 500
            raise HTTPError(code, error)

        render_args = {}
        if self.handler_type == "domain":
            render_args = {"domain": data}
        elif self.handler_type == "feature_collection":
            collection_bbox = interface.get_collection_bbox()
            render_args = {"features": data, "collection_bbox": collection_bbox}
        return render_args

    def _get_file(self):
        interface = self._get_interface()
        filename, url, error = interface.file_object()
        if filename is None:
            if error is None:
                raise HTTPError(404, "File not found.")
            else:
                raise HTTPError(500, error)
        return filename, url


class RootHandler(Handler):
    """Handle capabilities requests to the root of the server."""
    handler_type = "capabilities"

    def initialize(self, data_interface):
        super().initialize()
        self.data_interface = data_interface

    def get(self):
        super().get("")

    def _get_render_args(self) -> Dict:
        interface = self.data_interface.Capabilities()
        data = interface.data()
        return {"capability": data}


class APIHandler(Handler):
    """Handle API requests."""
    handler_type = "api"

    def initialize(self, data_interface):
        super().initialize()
        self.data_interface = data_interface

    def get(self):
        super().get("")


class ConformanceHandler(Handler):
    """Handle conformance requests."""
    handler_type = "conformance"

    def initialize(self, data_interface):
        super().initialize()
        self.data_interface = data_interface

    def get(self):
        super().get("")

    def _get_render_args(self) -> List:
        interface = self.data_interface.Conformance()
        return interface.data()

    def render_template(self) -> None:
        template = {"conformsTo": self._get_render_args()}
        self.write(template)


class ServiceHandler(Handler):
    """
    Handle EDR service requests:
      * description
      * license
      * terms and conditions.

    As these are all HTML documents, we redirect to the location where
    they are found rather than templating HTML documents here.

    """

    def initialize(self, data_interface):
        self.data_interface = data_interface

    def get(self):
        webdoc = self.request.path.split("/")[-1]
        data = self.data_interface.Service().data()
        if "description" in webdoc:
            redir_url = data.description_url
        elif "license" in webdoc:
            redir_url = data.license_url
        elif "terms" in webdoc:
            redir_url = data.terms_url
        else:
            raise HTTPError(404, "Not found")
        self.redirect(redir_url, permanent=True)


class AreaHandler(_DomainOrFeatureHandler):
    """Handle area requests."""
    handler_type = "domain"

    def initialize(self, data_interface, **kwargs):
        super().initialize(data_interface, **kwargs)


class CorridorHandler(Handler):
    """Handle corridor requests."""
    handler_type = "domain"

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
    handler_type = "items"  # feature_collection?

    def initialize(self, data_interface, **kwargs):
        super().initialize(**kwargs)
        self.data_interface = data_interface

    def _get_render_args(self) -> Dict:
        collection_url = self.reverse_url_full("collection", self.collection_id)
        interface = self.data_interface.Items(
            self.collection_id,
            self.query_parameters.parameters,
            collection_url
        )
        return {"items": interface.data()}


class ItemHandler(Handler):
    """Handle items requests."""
    handler_type = "item"

    def initialize(self, data_interface, **kwargs):
        super().initialize(**kwargs)
        self.data_interface = data_interface

    def get(self, collection_id, item_id):
        self.collection_id = collection_id
        self.item_id = item_id
        super().get(collection_id)

    def _get_interface(self):
        return self.data_interface.Item(
            self.collection_id,
            self.item_id,
            self.query_parameters.parameters
        )

    def _get_render_args(self) -> Dict:
        interface = self._get_interface()
        parameter = interface.data()
        if parameter is None:
            raise HTTPError(404, f"Item {self.item_id} was not found.")
        return {"parameter": parameter}

    def _get_file(self):
        interface = self._get_interface()
        filename, url, error = interface.file_object()
        if filename is None:
            if error is None:
                raise HTTPError(404, "File not found.")
            else:
                raise HTTPError(500, error)
        return filename, url


class LocationsHandler(Handler):
    """Handle location requests."""
    handler_type = "feature_collection"

    def initialize(self, data_interface, **kwargs):
        super().initialize(**kwargs)
        self.data_interface = data_interface

    def _get_render_args(self) -> Dict:
        interface = self.data_interface.Locations(
            self.collection_id,
            self.query_parameters.parameters
        )
        locs_list = interface.data()
        collection_bbox = interface.get_collection_bbox()
        return {"features": locs_list, "collection_bbox": collection_bbox}


class LocationHandler(Handler):
    """Handle location requests."""
    handler_type = "domain"

    def initialize(self, data_interface, **kwargs):
        self.data_interface = data_interface
        super().initialize(**kwargs)

    def get(self, collection_id, location_id):
        self.collection_id = collection_id
        self.location_id = location_id
        items_url = self.reverse_url_full("items_query", self.collection_id)
        self.interface = self.data_interface.Location(
            self.collection_id,
            self.location_id,
            self.query_parameters.parameters,
            items_url
        )
        super().get(collection_id)

    def _get_render_args(self) -> Dict:
        location, error_msg = self.interface.data()
        if location is None:
            if error_msg is None:
                error_msg = "Location not found"
            emsg = f"{error_msg} for {self.location_id!r} in collection with ID {self.collection_id!r}."
            raise HTTPError(404, emsg)
        return {"domain": location}

    def _get_file(self):
        file_object = self.interface.file_object()


class PositionHandler(_DomainOrFeatureHandler):
    """Handle position requests."""
    handler_type = "domain"

    def initialize(self, data_interface, **kwargs):
        super().initialize(data_interface, **kwargs)


class RadiusHandler(_DomainOrFeatureHandler):
    """Handle radius requests."""
    handler_type = "domain"

    def initialize(self, data_interface, **kwargs):
        super().initialize(data_interface, **kwargs)


class TrajectoryHandler(Handler):
    """Handle trajectory requests."""
    handler_type = "domain"

    def get(self, collection_name):
        """Handle a 'get trajectory' request."""
        # Not implemented!
        raise HTTPError(501, f"Get {self.handler_type} request is not implemented.")
