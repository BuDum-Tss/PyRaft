from abc import abstractmethod, ABC

from pyraft.core.api import ReceiverApi, SenderApi
from pyraft.data.messages import AppendRecordsReq, RequestVoteReq, RequestVoteResp
from pyraft.data.state import State, Log


class Role(ReceiverApi, ABC):
    def __init__(self,
                 state: State,
                 log: Log,
                 sender: SenderApi):
        self.state = state
        self.log = log
        self.sender = sender

    @abstractmethod
    def run(self):
        pass
