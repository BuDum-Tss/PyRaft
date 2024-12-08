import logging

from pyraft import Settings
from pyraft.core import Controller
from pyraft.core.api import SenderApi
from pyraft.data import State, Log, SyncStorage
from pyraft.data.enums import RoleName
from pyraft.transport.sender import HttpSender


class Node:
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.sync_storage = SyncStorage()
        self.log = Log(sync_storage=self.sync_storage)
        self.state = State(settings=self.settings, log=self.log)
        self.sender: SenderApi = HttpSender()
        self.controller = Controller(RoleName.follower,  self.state, self.sender)

    def receiver(self):
        return self.controller.current

    def start(self):
        self.controller.start()

    def __del__(self):
        self.controller.stop()
        logging.debug("Node destroyed")
