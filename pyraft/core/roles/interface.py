from abc import abstractmethod

from pyraft.core.api import ReceiverApi, SenderApi
from pyraft.data.messages import AppendRecordsReq, RequestVoteReq, RequestVoteResp
from pyraft.data.state import State, Log


class Role(ReceiverApi):
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

    @abstractmethod
    def append_records(self, data: AppendRecordsReq):
        pass

    @abstractmethod
    def request_vote(self, data: RequestVoteReq):
        pass

    @abstractmethod
    def update(self, data: RequestVoteResp):
        pass
