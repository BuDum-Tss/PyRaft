from abc import ABC, abstractmethod
from typing import Tuple

from pyraft.data.messages import AppendRecordsReq, AppendRecordsResp, RequestVoteReq, RequestVoteResp, UpdateValueReq


class ReceiverApi(ABC):
    @abstractmethod
    def append_records(self, data: AppendRecordsReq) -> AppendRecordsResp:
        pass

    @abstractmethod
    def request_vote(self, data: RequestVoteReq) -> RequestVoteResp:
        pass

    @abstractmethod
    def update(self, data: UpdateValueReq) -> Tuple[int, str]:
        pass


class SenderApi(ABC):
    @abstractmethod
    def append_records(self, address: str, data: AppendRecordsReq) -> AppendRecordsResp:
        pass

    @abstractmethod
    def request_vote(self, address: str, data: RequestVoteReq) -> RequestVoteResp:
        pass

    @abstractmethod
    def update(self, address: str, data: UpdateValueReq) -> int:
        pass
