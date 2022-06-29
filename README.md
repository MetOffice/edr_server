# edr-server
An EDR (Environmental Data Retrieval) Server written in Python.

## Introduction

Environmental Data Retrieval is a web standard for requesting environmental data (data that describes the earth's environment in some way and may be geolocated; such as weather and climate data, or geological data) and presenting that data to the requesting system in a well-known format. 

The EDR standard an OGC (Open Geospatial Consortium) standard. Much more information on EDR is available [from the OGC](https://ogcapi.ogc.org/edr/).

This project aims to reduce the overhead of creating an EDR server by providing a server implementation
that allows users to provide their own data provider implementation.

Currently, the only server implementation is in [tornado](https://www.tornadoweb.org/en/stable/), but the project is 
written so that more implementations could be  added over time. For example, an implementation using 
[flask](https://flask.palletsprojects.com/en/2.1.x/) or [django](https://www.djangoproject.com/) or even an 
[AWS Lambda](https://aws.amazon.com/lambda/) & [AWS API Gateway](https://aws.amazon.com/api-gateway/) based implementation.

Implementors provide their own data provider by implementing the data interfaces defined in `edr_server.core`.  
By adhering to a common data interface, a single server implementation can be used by multiple data providers without
having to change the server code. 

Depending on the needs of your project, `edr_server` can be used in two ways:
* as a server
* as a library/framework

For further information on how to use `edr_server` in these different ways, please refer to:
* [Quickstart_server](docs/Quickstart_server.md)
* [Quickstart_library](docs/Quickstart_library.md)

## Troubleshooting

If something goes wrong on the server you can check the server's error log for details. This is by default printed in the terminal session hosting the running server. For example:

```bash
WARNING:tornado.access:404 GET /collections?f=json (127.0.0.1) 0.68ms
```

This error indicates that for some reason tornado was unable to find a handler for the path requested of the server, resulting in an error `404 (not found)` being raised by the server. If we had made this request to the server using requests, this is what we'd see from requests:

```pycon
>>> uri = "http://localhost:8808/collections?f=json"
>>> r = requests.get(uri)
>>> r
<Response [404]>
```

For the case of a 404 error, you'd want to check that the query string being passed to the server is correct; for example that it's a query that the server can handle and that it's not malformed. In this case the query string is malformed and should have a '/' between the route and the slug. That is, the full uri should be `"http://localhost:8808/collections/?f=json"`.

An error `500 (internal server error)` indicates that something has gone wrong in the Python code that is being run by the server to handle requests that it receives. In this case the traceback of the Python error that caused the `500` error should be printed to the terminal running the EDR server, and will enable investigating and fixing the root cause of the error.