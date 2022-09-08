The `edr_server` code can be used as library or framework for implementing an EDR server.

This permits the implementor full control over how the server and data interface are initialised, configured, 
and started.

It's useful if you wish to do things like:
  * add custom command line options
  * load config from a custom location
  * change how your data interface is initialised (such as by providing additional parameters)

Normally, all the above things would require modification to the `edr_server` source code, which may make it harder to
update your server as new features and fixes are added.

The downside is that you need to provide your own version of `edr_server`'s `bin/run_edr_server` script.


## Installing

`pip install https://github.com/ADAQ-AQI/edr-server/archive/refs/heads/main.zip`

For **development** work:  
To install the code using pip in development mode, clone the repository and run:  
`pip install -e /path/to/repo/root/directory/`  
(where `/path/to/repo/root/directory/` is replaced with the path to the repo's root directory)

This will install the code using symlinks back to the source code, enabling changes to the code
to take effect without having to reinstall the package manually. (Although some changes, to things such as
the packaging config may still require a manual reinstall, most things won't)

## Writing the server startup script
This assumes a tornado server implementation from `edr_server.impl.tornado`, and is largely generic `tornado` server 
start-up boilerplate, such as what can be seen in the 
[tornado documentation](https://www.tornadoweb.org/en/stable/guide/structure.html)

**start_my_edr_server.py**:

```python
#!/usr/bin/env python

import logging

import edr_server.impl.tornado.server
import tornado.ioloop
from edr_server.core.interface import EdrDataInterface
from tornado.options import options, define

APP_LOGGER = logging.getLogger("tornado.application")


def start_server():
    # Setup tornado options
    define("port", default=8808, help="port to listen on")

    tornado.options.parse_command_line()

    # Setup tornado logging
    logging.basicConfig()
    logging.getLogger().setLevel(logging.ERROR)
    logging.getLogger("tornado").setLevel(options.logging.upper())

    # Create your data interface here ...
    # EdrDataInterface is a container for  various abstract interfaces
    # instantiate your concrete implementations of the abstract interfaces and pass them as
    # arguments to the EdrDataInterface constructor
    data_interface = EdrDataInterface(...)

    # Create the EDR Server tornado application
    app = edr_server.impl.tornado.server.make_app(data_interface)

    # Tell it which port to listen on
    app.listen(options.port)

    # Start the server
    APP_LOGGER.info(f"Listening on port {options.port}...")
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    start_server()

```

Once you've created your startup script, make it executable by running (on Unix OSs):
```bash
$ chmod a+x start_my_edr_server.py
```

## Using it
Execute your start-up script:
```bash
$ ./run_my_edr_server
Listening on port 8808...
```

This will kick off a tornado web server (running on localhost and on port 8808 by default, which was chosen at random) 
that runs the EDR Server.


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
