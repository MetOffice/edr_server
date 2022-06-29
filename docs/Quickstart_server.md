The `edr_server` code can be used as standalone server.

In this use case the data interface is specified via config file. 
It requires the `edr_server` source code to be checked out to a local directory.  

It has some limitations, so is not so suited to implementors who desire fine-grained control over
things such as the instantiation of the data interface (e.g. to establish connections to other services)

It can work well for use cases such as serving data from static data files, however, as it can
avoid some boilerplate associated with using the `edr_server` as a framework.

## Installing

* Download the source code: `git clone https://github.com/ADAQ-AQI/edr-server.git`
* Update the config file in `etc/config.yml` with the import path of your implementation of `EdrServerDataInterface`
* Ensure that your `EdrServerDataInterface` is importable, such as by adding it to the `PYTHONPATH`

## Starting the server
Run the executable Python script `bin/run_server`. 

```bash
$ cd edr_server/bin
$ ./run_edr_server
Listening on port 8808...
```

This will kick off a tornado web server (running on localhost and on port 8808 by default, which was chosen at random) 
that runs the EDR Server. The port can be changed using the `--port` option to the `run_edr_server` command

Full details of command line options can be seen by running `./run_edr_server --help`. 

### Initial Setup
In the `tornado` implementation, the responses for the collections endpoints are pregenerated and cached.
The first time you start the server, the cache will be empty, and you will need to trigger a refresh by sending a `POST`
 request to the refresh_collections endpoint:
```pycon
>>> import requests
>>> r = requests.post("http://localhost:8808/admin/refresh_collections")
>>> print(r.status_code)  # 200 if everything worked, 500 if there was a problem; check the logs for further info
```

### Checking it's working
To test functionality, you could use the `requests` package to submit a request to the server:

```pycon
>>> import requests

>>> uri = "http://localhost:8808/collections/?f=json"
>>> r = requests.get(uri)
>>> r.json()
```

If the server is functioning correctly, the last line will print the contents of the `collections` JSON file being 
served by the EDR server to `STDOUT`.
