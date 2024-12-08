import logging
import threading
from typing import Tuple

from .messages import Record, RequestVoteReq
from .storage import SyncStorage
from .settings import Settings


class Log:
    def __init__(self, sync_storage: SyncStorage):
        self.log: list[Record] = [Record(term=0, key="", value="")]
        self.sync_storage = sync_storage
        self._commit_index: int = 0
        self.voted_for = None

    def __getitem__(self, item) -> Record:
        return self.log[item]

    def __len__(self) -> int:
        return len(self.log)

    def __contains__(self, item: Tuple[int, int]) -> bool:
        index, term = item
        return self.log[index].term == term

    def append(self, record: Record):
        self.log.append(record)

    def clear_after(self, rollback_idx: int):
        self.log = self.log[:rollback_idx]

    def apply_before(self, commit_index: int):
        for idx_for_apply in range(self.commit_index + 1, commit_index + 1):
            self.apply(idx_for_apply)
        self._commit_index = commit_index

    def apply(self, log_idx: int):
        record = self.log[log_idx]
        self.sync_storage.update(record.key, record.value)
        logging.info(f"LOG APLLIED: [{record.key}] = {record.value}")

    @property
    def commit_index(self) -> int:
        """
        :return: Индекс последнего примененного изменения
        """
        return self._commit_index

    @property
    def last_commit_term(self) -> int:
        """
        :return: Индекс последнего примененного изменения
        """
        return self.log[self._commit_index].term

    @property
    def last_log_index(self) -> int:
        return len(self.log) - 1

    @property
    def last_log_term(self) -> int:
        return self.log[-1].term

    @commit_index.setter
    def commit_index(self, value):
        self._commit_index = value

    def __str__(self):
        string = ""
        for i, log in enumerate(self.log):
            if i < self._commit_index:
                string += f"[{log.term}]"
            else:
                string += f"({log.term})"
        return string

class State:
    def __init__(self, settings: Settings, log: Log):
        self.settings = settings
        self.rv_leader: RequestVoteReq = None
        self.rv_voted_for: RequestVoteReq = None
        self.log: Log = log
        self.term = 0
        self.lock = threading.Lock()
        self.role_changed: bool = False


    def __enter__(self):
        logging.info("Try lock")
        self.lock.acquire()
        logging.info("State locked")

    def __exit__(self, type, value, tb):
        logging.info("Try unlock")
        if not self.role_changed:
            logging.info("State unlocked")
            self.lock.release()

    @property
    def leader(self):
        if self.rv_leader is None:
            return None
        return self.settings.nodes[self.rv_leader.candidate_id]

    @property
    def nodes(self):
        return list(filter(lambda x: str(x) != str(self.settings.self_node), self.settings.nodes.values()))
