import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from pyraft.core.api import ReceiverApi, SenderApi
from pyraft.core.role import Role
from pyraft.core.util import Timings

from pyraft.data.state import State
from pyraft.data.util import RoleName, Address
from pyraft.data.messages import RequestVoteReq, AppendRecordsReq, Record, SyncObjectModel, RequestVoteResp, \
    AppendRecordsResp

log = logging.getLogger("LEADER")

class Leader(Role, ReceiverApi):

    def __init__(self,
                 state: State,
                 sender: SenderApi):
        super().__init__(state, sender)
        self.heartbeat = threading.Event()
        self.prev_index = {address.id : self.log.last_log_index for address in self.state.nodes}
        self.match_index = {}
        self.executor = None
        self.voted_for = None

    def run(self):
        self.state.candidate = None
        self.executor = ThreadPoolExecutor(max_workers=len(self.state.settings.nodes) - 1)
        self.state.role_changed = False
        self.state.leader_id = self.state.settings.myself.id
        while not self.interrupted:
            log.info(f"RUN - [{self.state.term}] - {self.state.log} - Heartbeat start.")
            log.info(f"RUN - [{self.state.term}] - {self.state.log} - Send changes...")
            with self.state:
                futures = self.send_changes()
            log.info(f"RUN - [{self.state.term}] - {self.state.log} - Waiting futures...")
            self.heartbeat.wait(Timings.HEARTBEAT_TIME)
            for future in as_completed(futures):
                future.result()
            log.info(f"RUN - [{self.state.term}] - {self.state.log} - Check quorum...")
            with self.state:
                self.log.commit_index = self.update_commit_index()
            log.info(f"RUN - [{self.state.term}] - {self.state.log} - Heartbeat end.")
        return RoleName.follower

    def update_commit_index(self) -> int:
        indexes = {idx for node_id, idx in self.prev_index.items()
                   if idx > self.log.commit_index and self.log[idx].term == self.state.term}
        index_counts = {}
        for index in indexes:
            index_counts[index] = list(self.prev_index.values()).count(index)
        log.info(f"RUN - [{self.state.term}] - {self.state.log} - Count indexes: {index_counts}\n{self.prev_index}")
        for index, count in sorted(index_counts.items(), key=lambda x: -x[1]):
            log.info((index, count))
            log.info(count > len(self.state.settings.nodes)/2)
            if count + 1 > len(self.state.settings.nodes)/2:
                log.info(f"RUN - [{self.state.term}] - {self.state.log} - Apply index: {index}")
                self.log.apply_to(index)
                return index
        return self.log.commit_index

    def send_changes(self) -> list:
        addresses: list[Address] = self.state.nodes
        return [self.executor.submit(self.send_changes_to, address) for address in addresses]

    def send_changes_to(self, address: Address) -> None:
        log.info(f"{address} - [{self.state.term}] - {self.state.log} - Send changes.")
        prev_log_index = self.prev_index[address.id]
        data = AppendRecordsReq(term=self.state.term,
                                leader_id=self.state.settings.myself.id,
                                prev_log_index=prev_log_index,
                                prev_log_term=self.log[prev_log_index].term,
                                records=self.log[prev_log_index + 1 :],
                                commit=self.log.commit_index)
        resp: AppendRecordsResp = self.sender.append_records(str(address), data, timeout=Timings.HEARTBEAT_TIME - 1)

        if resp:
            if resp.success:
                self.prev_index[address.id] = data.prev_log_index + len(data.records)
                self.match_index[address.id] = self.log.commit_index
            else:
                self.prev_index[address.id] = prev_log_index - 1
        return

    def append_records(self, data: AppendRecordsReq):
        if data.term > self.state.term and data.prev_log_index > self.log.last_log_index:
            self.stop()
            log.info(f"AR - [{self.state.term}] - {self.state.log} - Self not actual! Becoming follower...")
        return AppendRecordsResp(term=self.state.term,
                                 last_log_index=self.log.last_log_index,
                                 success=False)

    def request_vote(self, data: RequestVoteReq):
        if data.term < self.state.term:
            log.info(f"RV - [{self.state.term}] - {self.state.log} - RV sender has not actual term!")
            return RequestVoteResp(term=self.state.term, vote_granted=False)
        self.state.term = data.term
        if self.state.candidate is None or (data.last_log_index >= self.state.log.last_log_index
                and data.last_log_term >= self.state.log.last_log_term):
            log.info(f"RV - [{self.state.term}] - {self.state.log} - Self not actual! Becoming follower and voting for sender...")
            self.state.candidate = data
            self.stop()
            return RequestVoteResp(term=self.state.term, vote_granted=True)
        log.info(f"RV - [{self.state.term}] - {self.state.log} - RV sender is not actual!")
        return RequestVoteResp(term=self.state.term, vote_granted=False)

    def set_value(self, data: SyncObjectModel):
        self.state.log.append(Record(term=self.state.term, key=data.key,value=data.value))
        return 200, "Ok"
