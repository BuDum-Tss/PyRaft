from abc import ABC, abstractmethod
from typing import Tuple

from pyraft.data.messages import AppendRecordsReq, AppendRecordsResp, RequestVoteReq, RequestVoteResp, SyncObjectModel


class ReceiverApi(ABC):
    @abstractmethod
    def append_records(self, data: AppendRecordsReq) -> AppendRecordsResp:
        pass

    @abstractmethod
    def request_vote(self, data: RequestVoteReq) -> RequestVoteResp:
        pass

    @abstractmethod
    def set_value(self, data: SyncObjectModel, ttl: float=None) -> Tuple[int, str, int]:
        pass

    @abstractmethod
    def get_value(self, key: str) -> tuple[str, int]:
        pass


class SenderApi(ABC):
    @abstractmethod
    def append_records(self, address: str, data: AppendRecordsReq, timeout: float = 10.0) -> AppendRecordsResp:
        pass

    @abstractmethod
    def request_vote(self, address: str, data: RequestVoteReq, timeout: float = 10.0) -> RequestVoteResp:
        pass

    @abstractmethod
    def set_value(self, address: str, data: SyncObjectModel, ttl: float=None, timeout: float = 10.0) -> tuple[int, str, int]:
        pass