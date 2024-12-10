from abc import abstractmethod

from pyraft.core.api import SenderApi, ReceiverApi
from pyraft.data.util import RoleName
from pyraft.data.state import State


class Role(ReceiverApi):
    def __init__(self,
                 state: State,
                 sender: SenderApi):
        self.interrupted = False
        self.state = state
        self.log = self.state.log
        self.sender = sender

    @abstractmethod
    def run(self) -> RoleName:
        pass

    def get_value(self, key: str) -> str:
        return self.state.log.sync_storage.get_value(key)

    def stop(self):
        self.interrupted = True
        self.state.role_changed = True
