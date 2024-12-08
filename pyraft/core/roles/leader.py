import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from pyraft.core.api import ReceiverApi, SenderApi
from pyraft.core.role import Role
from pyraft.core.time import Timings
from pyraft.data import Address, State
from pyraft.data.enums import RoleName
from pyraft.data.messages import RequestVoteReq, AppendRecordsReq, Record, SyncObjectModel, RequestVoteResp, \
    AppendRecordsResp


class Leader(Role, ReceiverApi):
    heartbeat = None

    prev_index = None  # индекс следующей записи, которую запрашивает от лидера эта нода
    match_index = None  # индекс самого последнего лога лидера

    def __init__(self,
                 state: State,
                 sender: SenderApi):
        super().__init__(state, sender)
        self.heartbeat = threading.Event()
        self.prev_index = {}
        self.match_index = {}
        self.executor = None
        self.voted_for = None

    def run(self):
        self.executor = ThreadPoolExecutor(max_workers=len(self.state.settings.nodes) - 1)
        self.state.role_changed = False
        self.state.leader_id = self.state.settings.self_node.node_id
        while not self.interrupted:
            logging.info(f"RUN - [{self.state.term}] - {self.state.log} - Send changes.")
            with self.state:
                futures = self.send_changes()
            logging.info(f"RUN - [{self.state.term}] - {self.state.log}  - Wait futures...")
            self.heartbeat.wait(Timings.HEARTBEAT_TIME)
            for future in as_completed(futures):
                future.result()
            logging.info(f"RUN - [{self.state.term}] - {self.state.log}  - Check quorum...")
            with self.state:
                self.log.commit_index = self.update_commit_index()
        return RoleName.follower

    def update_commit_index(self) -> int:
        logging.info(self.prev_index)
        logging.info(self.match_index)
        indexes = {idx for node_id, idx in self.prev_index.items()
                   if idx > self.log.commit_index and self.log[idx].term == self.state.term}
        logging.info(indexes)
        index_counts = {}
        for index in indexes:
            index_counts[index] = list(self.prev_index.values()).count(index)
        logging.info(index_counts)
        for index, count in sorted(index_counts.items(), key=lambda x: -x[1]):
            logging.info((index, count))
            logging.info(count > len(self.state.nodes)/2)
            if count > len(self.state.nodes)/2:
                return index
        return self.log.commit_index

    def send_changes(self) -> list:
        addresses: list[Address] = self.state.nodes
        return [self.executor.submit(self.send_changes_to, address) for address in addresses]

    def send_changes_to(self, address: Address) -> None:
        logging.info(f"send_changes_to {address}")
        if address.node_id not in self.prev_index:
            logging.info(f"first request")
            data = AppendRecordsReq(term=self.state.term,
                                    leader_id=self.state.settings.self_node.node_id,
                                    prev_log_index=self.log.commit_index,
                                    prev_log_term=self.log.last_commit_term,
                                    records=[],
                                    commit=self.log.commit_index)
            logging.info(f"append_records send: {str(address)} - {data}")
            resp: AppendRecordsResp = self.sender.append_records(str(address), data)
            logging.info(f"append_records response: {str(address)} - {resp}")
            if resp is not None:
                self.prev_index[address.node_id] = resp.last_log_index
                self.match_index[address.node_id] = self.log.commit_index
        else:
            logging.info(f"heartbeat")
            prev_log_index = self.prev_index[address.node_id]
            data = AppendRecordsReq(term=self.state.term,
                                    leader_id=self.state.settings.self_node.node_id,
                                    prev_log_index=prev_log_index,
                                    prev_log_term=self.log[prev_log_index].term,
                                    records=self.log[prev_log_index + 1:self.log.last_log_index + 1],
                                    commit=self.log.commit_index)
            logging.info(f"append_records send: {str(address)} - {data}")
            resp: AppendRecordsResp = self.sender.append_records(str(address), data, timeout=Timings.HEARTBEAT_TIME-1)
            logging.info(f"append_records response: {str(address)} - {resp}")
            if resp:
                if resp.success:
                    self.prev_index[address.node_id] = data.prev_log_index + len(data.records)
                    #self.match_index[address.node_id] = data.prev_log_index + len(data.records)
                else:
                    self.prev_index[address.node_id] = resp.last_log_index + 1
                    self.match_index[address.node_id] = self.prev_index[address.node_id] - 1
        return None

    def parse_append_records_resp(self, request: AppendRecordsReq, sender_id, resp: AppendRecordsResp):
        if resp:
            if resp.success:
                self.prev_index[sender_id] = request.prev_log_index + len(request.records)
                self.match_index[sender_id] = request.prev_log_index + len(request.records)
            else:
                self.prev_index[sender_id] = self.prev_index[sender_id] - 1
                self.match_index[sender_id] = resp.last_log_index + 1

    def append_records(self, data: AppendRecordsReq):
        if data.term > self.state.term and data.prev_log_index > self.log.last_log_index:
            self.stop()
        return AppendRecordsResp(term=self.state.term,
                                 last_log_index=self.log.last_log_term,
                                 success=False)

    def request_vote(self, data: RequestVoteReq):
        logging.debug(self.state.term)
        if data.term < self.state.term:
            return RequestVoteResp(term=self.state.term, vote_granted=False)
        if (data.last_log_index >= self.state.log.last_log_index
                and data.last_log_term >= self.state.log.last_log_term):
            self.stop()
            return RequestVoteResp(term=self.state.term, vote_granted=True)
        self.state.term = data.term
        return RequestVoteResp(term=self.state.term, vote_granted=False)

    def set_value(self, data: SyncObjectModel):
        self.state.log.append(Record(term=self.state.term, key=data.key,value=data.value))
        return 200, "Ok"
