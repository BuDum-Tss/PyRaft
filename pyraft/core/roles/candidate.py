import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from pyraft.core.api import ReceiverApi, SenderApi
from pyraft.core.role import Role
from pyraft.core.threading.overflow_value import OverflowValue
from pyraft.core.util import Timings

from pyraft.data.state import State
from pyraft.data.util import RoleName, Address
from pyraft.data.messages import RequestVoteResp, RequestVoteReq, AppendRecordsReq, AppendRecordsResp

log = logging.getLogger("CANDIDATE")

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
        self.state.candidate = RequestVoteReq(term=self.state.term,
                                              candidate_id=self.state.settings.myself.id,
                                              last_log_index=self.log.last_log_index,
                                              last_log_term=self.log.last_log_term)
        c = int(len(self.state.settings.nodes) / 2)
        logging.info(f"[{self.state.term}] - {self.state.log} - Need to win: {c}")
        self.votes = OverflowValue(default=1,
                                   capacity=c,
                                   on_overflow=lambda: self._become(RoleName.leader))
        self.futures = None


    def run(self):
        self.executor = ThreadPoolExecutor(max_workers=len(self.state.settings.nodes) - 1)
        while not (self.interrupted or self.state.role_changed):
            self.state.term += 1
            logging.info(f"[{self.state.term}] - {self.state.log} - New round. Request votes...")
            self.futures = self._request_votes()
            timeout = Timings.VOTE_TIMEOUT
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
                              candidate_id=self.state.settings.myself.id,
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

    def _become(self, new_role: RoleName):
        self.new_role = new_role
        self.voting.set()
        self.stop()

    def append_records(self, data: AppendRecordsReq):
        if data.term > self.state.term:
            self.state.term = data.term
            self._become(RoleName.follower)
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
            log.info(f"RV - [{self.state.term}] - {self.state.log} - Self not actual! Voting for sender...")
            self.state.candidate = data
            self._become(RoleName.follower)
            return RequestVoteResp(term=self.state.term, vote_granted=True)
        logging.debug(f"[{self.state.term}] - {self.state.log} -  RV sender is not actual!")
        return RequestVoteResp(term=self.state.term, vote_granted=False)

    def set_value(self, data: RequestVoteResp):
        return 301, "Changing leader. Please, wait..."
