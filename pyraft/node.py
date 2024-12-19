from pyraft.core import Controller
from pyraft.core.api import SenderApi
from pyraft.data.state import State, Log
from pyraft.data.storage import SyncStorage
from pyraft.data.util import Settings, RoleName
from pyraft.transport.sender import HttpSender


class Node:
    def __init__(self, settings: Settings, sync_storage: SyncStorage = SyncStorage()):
        super().__init__()
        self.settings = settings
        self.sync_storage = sync_storage
        self.log = Log(sync_storage=self.sync_storage)
        self.state = State(settings=self.settings, log=self.log)
        self.sender: SenderApi = HttpSender()
        self.controller = Controller(RoleName.follower,  self.state, self.sender)

    def receiver(self):
        return self.controller.current

    def start(self):
        self.controller.start()

    def stop(self):
        self.controller.stop()
