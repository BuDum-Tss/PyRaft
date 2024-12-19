import logging
import threading

from pyraft.core.api import ReceiverApi, SenderApi
from pyraft.core.role import Role
from pyraft.core.util import Timings

from pyraft.data.state import State
from pyraft.data.util import RoleName
from pyraft.data.messages import RequestVoteResp, RequestVoteReq, AppendRecordsReq, AppendRecordsResp, SyncObjectModel

log = logging.getLogger("FOLLOWER")

class Follower(Role, ReceiverApi):
    heartbeat = None

    def __init__(self, state: State, sender: SenderApi):
        super().__init__(state, sender)
        self.heartbeat = threading.Event()

    def run(self) -> RoleName:
        while not (self.interrupted or self.state.role_changed):
            log.info(f"RUN - [{self.state.term}] - {self.state.log} - Heartbeat waiting start.")
            log.info(f"RUN - [{self.state.term}] - {self.state.log} - Waiting heartbeat...")
            self.heartbeat.wait(Timings.HEARTBEAT_TIME)
            if self.heartbeat.is_set():
                log.info(f"RUN - [{self.state.term}] - {self.state.log} - Heartbeat received.")
                self.heartbeat.clear()
            else:
                log.info(f"RUN - [{self.state.term}] - {self.state.log} - No heartbeat. Waiting election time...")
                with self.state:
                    self.state.candidate = None
                if self.interrupted or self.state.role_changed:
                    break
                self.heartbeat.wait(Timings.election_timeout())
                if self.state.candidate is not None:
                    log.info(f"RUN - [{self.state.term}] - {self.state.log} - Find candidate.")
                    self.heartbeat.clear()
                elif self.heartbeat.is_set():
                    log.info(f"RUN - [{self.state.term}] - {self.state.log} - Heartbeat received.")
                    with self.state:
                        self.state.candidate = self.state.leader
                else:
                    log.info(f"RUN - [{self.state.term}] - {self.state.log} - No leader. Changing role...")
                    break
                log.info(f"RUN - [{self.state.term}] - {self.state.log} - Heartbeat waiting finish.")
        return RoleName.candidate

    def append_records(self, data: AppendRecordsReq) -> AppendRecordsResp:
        if data.term < self.state.term:
            self.heartbeat.set()
            log.info(f"AR - [{self.state.term}] - {self.state.log} - AR sender has not actual term!")
            return AppendRecordsResp(term=self.state.term, last_log_index=self.log.last_log_index, success=False)
        self.state.term = data.term
        if data.prev_log_index > self.log.last_log_index or data.prev_log_term != self.log[data.prev_log_index].term:
            self.heartbeat.set()
            log.info(f"AR - [{self.state.term}] - {self.state.log} - AR sender is not actual!")
            return AppendRecordsResp(term=self.state.term, last_log_index=self.log.last_log_index, success=False)
        self._append_records(data)
        return AppendRecordsResp(term=self.state.term, last_log_index=self.log.last_log_index, success=True)

    def _append_records(self, data: AppendRecordsReq):
        log.info(F"AR - [{self.state.term}] - {self.state.log} - appending records {data.records}")
        self.state.leader = data.leader_id
        self.heartbeat.set()
        for i, record in enumerate(data.records):
            record_idx: int = data.prev_log_index + 1 + i
            if record_idx > self.log.last_log_index:
                self.log.append(record)
                log.info(F"AR - [{self.state.term}] - {self.state.log} - append record at index {record_idx}: {record}")
            elif record.term != self.log[record_idx].term:
                self.log[record_idx] = record
                log.info(F"AR - [{self.state.term}] - {self.state.log} - replace record at index {record_idx}: {record}")
                self.state.log.append(record)
        log.info(f"AR - [{self.state.term}] - {self.state.log} - apply to {data.commit}")
        self.log.apply_to(data.commit)

    def request_vote(self, data: RequestVoteReq) -> RequestVoteResp:
        if data.term < self.state.term:
            log.info(f"RV - [{self.state.term}] - {self.state.log} - RV sender has not actual term!")
            return RequestVoteResp(term=self.state.term, vote_granted=False)
        self.state.term = data.term
        if self.state.candidate is None or (data.last_log_index >= self.state.log.last_log_index
                and data.last_log_term >= self.state.log.last_log_term):
            log.info(f"RV - [{self.state.term}] - {self.state.log} - Self not actual! Voting for RV sender...")
            self.state.candidate = data
            return RequestVoteResp(term=self.state.term, vote_granted=True)
        logging.debug(f"RV - [{self.state.term}] - {self.state.log} -  RV sender is not actual!")
        return RequestVoteResp(term=self.state.term, vote_granted=False)

    def set_value(self, data: SyncObjectModel, ttl: float=None) -> tuple[int, str, int]:
        leader = self.state.leader
        if leader is None:
            return 503, "Leader not found", 0
        return self.sender.set_value(leader, data, ttl=ttl)
