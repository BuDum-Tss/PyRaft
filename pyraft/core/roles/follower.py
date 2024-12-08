import logging
import threading

from pyraft.core.api import ReceiverApi, SenderApi
from pyraft.core.role import Role
from pyraft.core.time import Timings
from pyraft.data import State
from pyraft.data.enums import RoleName
from pyraft.data.messages import RequestVoteResp, RequestVoteReq, AppendRecordsReq, AppendRecordsResp, SyncObjectModel


class Follower(Role, ReceiverApi):
    heartbeat = None

    def __init__(self, state: State, sender: SenderApi):
        super().__init__(state, sender)
        self.heartbeat = threading.Event()

    def __del__(self):
        pass

    def run(self) -> RoleName:
        self.state.leader_id = None
        while not self.interrupted:
            logging.info(f"[{self.state.term}] - {self.state.log} - Waiting heartbeat...")
            self.heartbeat.wait(Timings.BROADCAST_TIME)
            if self.heartbeat.is_set():
                logging.info(f"[{self.state.term}] - {self.state.log} - Heartbeat received.")
                self.heartbeat.clear()
            else:
                logging.info(f"[{self.state.term}] - {self.state.log} - No heartbeat. Waiting election time...")
                with self.state:
                    self.state.rv_voted_for = None
                self.heartbeat.wait(Timings.election_timeout())
                if self.state.rv_voted_for is not None:
                    logging.info(f"[{self.state.term}] - {self.state.log} - Find candidate.")
                elif self.heartbeat.is_set():
                    logging.info(f"[{self.state.term}] - {self.state.log} - Heartbeat received.")
                    with self.state:
                        self.state.rv_voted_for = self.state.rv_leader
                else:
                    logging.info(f"[{self.state.term}] - {self.state.log} - No leader. Changing role...")
                    break
        return RoleName.candidate

    def append_records(self, data: AppendRecordsReq) -> AppendRecordsResp:
        if data.term > self.state.term:
            self.state.term = data.term
        # 1
        elif data.term < self.state.term:
            self.heartbeat.set()
            return AppendRecordsResp(term=self.state.term, last_log_index=self.log.last_log_index, success=False)
        # 2
        if data.prev_log_index > self.log.last_log_index or data.prev_log_term != self.log[data.prev_log_index].term:
            self.heartbeat.set()
            return AppendRecordsResp(term=self.state.term, last_log_index=self.log.last_log_index, success=False)

        self._append_records(data)
        return AppendRecordsResp(term=self.state.term, last_log_index=self.log.last_log_index, success=True)

    def _append_records(self, data: AppendRecordsReq):
        logging.info(F"[{self.state.term}] - {self.state.log} - appending records {data.records}")
        self.state.leader_id = data.leader_id
        self.heartbeat.set()
        for i, record in enumerate(data.records):
            record_idx: int = data.prev_log_index + i + 1
            if record_idx <= self.log.last_log_index:
                if record.term != self.log[record_idx].term:
                    # 3
                    self.log.clear_after(record_idx + 1)
                    self.log.append(record)
                    logging.info(F"[{self.state.term}] - {self.state.log} - append record: {record}")
            else:
                # 4
                self.state.log.append(record)
        logging.info(F"[{self.state.term}] - {self.state.log} - apply before {data.commit}")
        self.log.apply_before(data.commit + 1)

    def request_vote(self, data: RequestVoteReq) -> RequestVoteResp:
        logging.debug(f"[{self.state.term}] - {self.state.log} - requesting my vote...")
        if data.term > self.state.term:
            self.state.term = data.term
            self.state.rv_voted_for = data
            return RequestVoteResp(term=self.state.term, vote_granted=True)
        if data.term >= self.state.term:
            if self.state.rv_voted_for is None or (data.last_log_index >= self.state.rv_voted_for.last_log_index
                                                   and data.last_log_term >= self.state.rv_voted_for.last_log_term):
                self.state.rv_voted_for = data
                return RequestVoteResp(term=self.state.term, vote_granted=True)
        else:
            pass
        logging.debug(f"[{self.state.term}] - {self.state.log} - I am more actual!!!")
        return RequestVoteResp(term=self.state.term, vote_granted=False)

    def set_value(self, data: SyncObjectModel) -> tuple[int, str]:
        leader = self.state.leader
        if leader is None:
            return 503, "Leader not found"
        return 301, f"http://{leader}/update"
