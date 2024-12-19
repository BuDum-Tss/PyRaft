import logging
import threading
from typing import Tuple

from .messages import Record, RequestVoteReq
from .storage import SyncStorage
from .util import Settings

log = logging.getLogger("STATE")


class Log:
    def __init__(self, sync_storage: SyncStorage):
        self._log: list[Record] = [Record(term=0, key="", value="")]
        self.sync_storage = sync_storage
        self._commit_index: int = 0

    def __getitem__(self, item) -> Record:
        return self._log[item]

    def __setitem__(self, key, value):
        self._log[key] = value


    def __len__(self) -> int:
        return len(self._log)

    def __contains__(self, item: Tuple[int, int]) -> bool:
        index, term = item
        return self._log[index].term == term

    def append(self, record: Record):
        self._log.append(record)

    def apply_to(self, new_commit_index: int):
        for idx_for_apply in range(self.commit_index + 1, new_commit_index + 1):
            self.apply(idx_for_apply)
        self._commit_index = new_commit_index

    def apply(self, log_idx: int):
        record = self._log[log_idx]
        record.applied = self.sync_storage.update(record.key, record.value, ttl=record.ttl)
        log.info(f"LOG APPLIED: [{record.key}] = {record.value}")

    @property
    def commit_index(self) -> int:
        return self._commit_index

    @commit_index.setter
    def commit_index(self, value):
        if self._commit_index >= len(self._log):
            raise ValueError(
                f"commit_index must be smaller than logs number. Got: {self._commit_index}. Logs length: {len(self._log)}")
        self._commit_index = value

    @property
    def last_commit_term(self) -> int:
        return self._log[self._commit_index].term

    @property
    def last_log_index(self) -> int:
        return len(self._log) - 1

    @property
    def last_log_term(self) -> int:
        return self._log[-1].term

    def __str__(self):
        string = ""
        for i, record in enumerate(self._log):
            if i <= self._commit_index:
                string += f"[{record.term}]"
            else:
                string += f"({record.term})"
        return string


class State:
    def __init__(self, settings: Settings, log: Log):
        self.settings = settings
        self._leader: str = None
        self.candidate: RequestVoteReq | str = None
        self.log: Log = log
        self.term = 0
        self.lock = threading.Lock()
        self.role_changed: bool = False

    def __enter__(self):
        log.info("Try lock")
        self.lock.acquire()
        log.info("State locked")

    def __exit__(self, type, value, tb):
        log.info("Try unlock")
        if not self.role_changed:
            log.info("State unlocked")
            self.lock.release()

    @property
    def leader(self):
        if self._leader is None:
            return None
        return self.settings.nodes[self._leader]

    @leader.setter
    def leader(self, node_id: str):
        self._leader = node_id

    @property
    def nodes(self):
        return list(filter(lambda x: str(x) != str(self.settings.myself), self.settings.nodes.values()))
