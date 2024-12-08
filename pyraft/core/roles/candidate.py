import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from pyraft.core.api import ReceiverApi, SenderApi
from pyraft.core.role import Role
from pyraft.core.threading.overflow_value import OverflowValue
from pyraft.core.time import Timings
from pyraft.data import Address, State
from pyraft.data.enums import RoleName
from pyraft.data.messages import RequestVoteResp, RequestVoteReq, AppendRecordsReq, AppendRecordsResp


class Candidate(Role, ReceiverApi):
    voting = None
    votes = None

    def __init__(self,
                 state: State,
                 sender: SenderApi):
        super().__init__(state, sender)
        self.executor = None
        self.voting = threading.Event()
        self.new_role: RoleName = None
        self.state.rv_voted_for = RequestVoteReq(term=self.state.term,
                                                 candidate_id=self.state.settings.self_node.node_id,
                                                 last_log_index=self.log.last_log_index,
                                                 last_log_term=self.log.last_log_term)
        c = int(len(self.state.settings.nodes) / 2)
        logging.info(f"[{self.state.term}] - {self.state.log} - Need to win: {c}")
        self.votes = OverflowValue(default=1,
                                   capacity=c,
                                   on_overflow=lambda: self._become(RoleName.leader))
        self.futures = None

    def __del__(self):
        for future in as_completed(self.futures):
            future.result()

    def run(self):
        self.executor = ThreadPoolExecutor(max_workers=len(self.state.settings.nodes) - 1)
        while not self.interrupted:
            self.state.term += 1
            logging.info(f"[{self.state.term}] - {self.state.log} - New round. Request votes...")
            self.futures = self._request_votes()
            timeout = Timings.election_timeout()
            logging.info(f"Wait {timeout} sec")
            self.voting.wait(timeout)
            if self.voting.is_set():
                logging.debug(f"[{self.state.term}] - {self.state.log} - Voting finished. New role: {self.new_role}")
                return self.new_role
            for future in as_completed(self.futures):
                future.result()
        logging.info(f"[{self.state.term}] - {self.state.log} - New role")
        return self.new_role

    def _request_votes(self) -> list:
        data = RequestVoteReq(term=self.state.term,
                              candidate_id=self.state.settings.self_node.node_id,
                              last_log_index=self.log.last_log_index,
                              last_log_term=self.log.last_log_term)
        addresses: list[Address] = self.state.nodes
        return [self.executor.submit(self._request_vote_from, address, data) for address in addresses]

    def _request_vote_from(self, address: Address, data: RequestVoteReq):
        resp: RequestVoteResp = self.sender.request_vote(str(address), data, timeout=Timings.VOTE_TIMEOUT)
        if resp is None:
            return
        if resp.term > self.state.term:
            self.state.term = data.term
            self._become(RoleName.follower)
            return
        elif resp.vote_granted:
            self.votes.set(self.votes.get() + 1)
        return

    def _become(self, role: RoleName):
        logging.info(f"[{self.state.term}] - {self.new_role} ---> {role}")
        self.state.role_changed = True
        self.new_role = role
        self.voting.set()

    def append_records(self, data: AppendRecordsReq):
        if data.term > self.state.term:
            self.state.term = data.term
            self._become(RoleName.follower)
        return AppendRecordsResp(term=self.state.term,
                                 last_log_index=self.log.last_log_index,
                                 success=False)

    def request_vote(self, data: RequestVoteReq):
        logging.debug(f"[{self.state.term}] - {self.state.log} - requesting my vote...")
        if data.term > self.state.term:
            self.state.term = data.term
            self.state.rv_voted_for = data
            self._become(RoleName.follower)
            return RequestVoteResp(term=self.state.term, vote_granted=True)
        if data.term == self.state.term:
            if self.state.rv_voted_for is None or (data.last_log_index >= self.state.rv_voted_for.last_log_index
                                                   and data.last_log_term >= self.state.rv_voted_for.last_log_term):
                self.state.rv_voted_for = data
                self._become(RoleName.follower)
                return RequestVoteResp(term=self.state.term, vote_granted=True)
        else:
            pass
        logging.debug(f"[{self.state.term}] - {self.state.log} - I am more actual!!!")
        return RequestVoteResp(term=self.state.term, vote_granted=False)

    def set_value(self, data: RequestVoteResp):
        return 301, "Changing leader. Please, wait..."
