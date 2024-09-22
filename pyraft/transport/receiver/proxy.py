import logging
import threading
from typing import Callable

from flask import Flask
from werkzeug.serving import make_server

from pyraft.core.api import ReceiverApi
from .api import NodeApi
from pyraft.data import Address


class Proxy(threading.Thread):

    def __init__(self, receiver: Callable[[], ReceiverApi], self_node: Address):
        threading.Thread.__init__(self)
        self.self_node = self_node
        self.app = self._prepare_app(self_node.node_id + " node API", receiver)
        self.server = make_server(self_node.host, self_node.port, self.app)
        self.ctx = self.app.app_context()
        self.ctx.push()

    def _prepare_app(self, name: str, receiver: Callable[[], ReceiverApi]) -> Flask:
        receiver_api = Flask(name)
        NodeApi.register(receiver_api, route_base='/', init_argument=receiver)
        receiver_api.debug = True
        receiver_api.use_reloader = False
        return receiver_api

    def run(self):
        logging.info('Starting server')
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()
