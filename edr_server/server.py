import tornado.ioloop
from tornado.web import Application

import collection


def make_app():
    return Application([
        (r"/collections/", collection.CollectionsHandler),
    ])


if __name__ == "__main__":
    port = 8808
    print(f"Listening on port {port}...")
    app = make_app()
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()