import random
import threading

from pyraft.core.roles.interface import Role
from pyraft.data.messages import RequestVoteResp, RequestVoteReq, AppendRecordsReq


class Follower(Role):
    def run(self):
        self.state.timer = threading.Timer(self.state.settings.min_election_timeout
                                           + random.Random().randint(0, 10) * 100, self.request_vote)

    def append_records(self, data: AppendRecordsReq):
        pass

    def request_vote(self, data: RequestVoteReq):
        pass

    def update(self, data: RequestVoteResp):
        pass
