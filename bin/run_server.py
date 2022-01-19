#!/usr/bin/env python

import logging

from edr_server.server import make_app
import tornado.ioloop
from tornado.options import options, define


APP_LOGGER = logging.getLogger("tornado.application")

define("port", default=8808, help="port to listen on")

if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.ERROR)
    logging.getLogger("tornado").setLevel(options.logging.upper())

    app = make_app()
    app.listen(options.port)
    APP_LOGGER.info(f"Listening on port {options.port}...")

    tornado.ioloop.IOLoop.current().start()
