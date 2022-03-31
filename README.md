# edr-server
An EDR (Environmental Data Retrieval) Server written in Python.

## Introduction

Environmental Data Retrieval is a web standard for requesting environmental data (data that describes the earth's environment in some way and may be geolocated; such as weather and climate data, or geological data) and presenting that data to the requesting system in a well-known format. 

The EDR standard an OGC (Open Geospatial Consortium) standard. Much more information on EDR is available [from the OGC](https://ogcapi.ogc.org/edr/).

## Installing

`pip install https://github.com/ADAQ-AQI/edr-server/archive/refs/heads/main.zip`

For **development** work:  
To install the code using pip in development mode, clone the repository and run:  
`pip install -e /path/to/repo/root/directory/`  
(where `/path/to/repo/root/directory/` is replaced with the path to the repo's root directory)

This will install the code using symlinks back to the source code, enabling changes to the code
to take effect without having to reinstall the package manually. (Although some changes, to things such as
the packaging config may still require a manual reinstall, most things won't)

## Using it

Run the executable Python script `bin/run_server`. It is added to the PATH by the pip installer, so it can be
executed like this:

```bash
$ run_edr_server
Listening on port 8808...
```

This will kick off a tornado web server (running on localhost and on port 8808 by default, which was chosen at random) 
that runs the EDR Server.

To test functionality, you could use the `requests` package to submit a request to the server:

```pycon
>>> import requests

>>> uri = "http://localhost:8808/collections/?f=json"
>>> r = requests.get(uri)
>>> r.json()
```

If the server is functioning correctly, the last line will print the contents of the `collections` JSON file being served by the EDR server to `STDOUT`.

### Troubleshooting

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