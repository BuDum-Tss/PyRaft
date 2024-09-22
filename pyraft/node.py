import logging
from typing import Dict

from pyraft import Settings
from pyraft.core.api import ReceiverApi, SenderApi
from pyraft.core.roles import Role, Follower, Candidate, Leader
from pyraft.data import State, Log, SyncStorage
from pyraft.data.enums import RoleName
from pyraft.data.messages import UpdateValueReq
from pyraft.transport.receiver import Proxy
from pyraft.transport.sender import HttpSender


class Node:
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.sync_storage = SyncStorage()
        self.log = Log(sync_storage=self.sync_storage)
        self.state = State(settings=self.settings, log=self.log)
        self.sender: SenderApi = HttpSender()
        self.receiver: Dict[RoleName, Role] = {
            RoleName.follower: Follower(self.state, self.log, self.sender),
            RoleName.candidate: Candidate(self.state, self.log, self.sender),
            RoleName.leader: Leader(self.state, self.log, self.sender)
        }
        self.proxy = Proxy(receiver=lambda: self.receiver[self.state.role], self_node=self.settings.self_node)
        self.proxy.start()

    def index(self, shared_id: str, sync_object):
        self.sync_storage.index(shared_id, sync_object)
        logging.debug(f"INDEX OBJECT:{shared_id}")

    def update(self, shared_id: str, value):
        code = self.sender.update(str(self.state.leader), UpdateValueReq(shared_object_id=shared_id, value=value))
        logging.debug(f"UPDATE OBJECT:{shared_id} to VALUE: {value} - CODE: {code}")