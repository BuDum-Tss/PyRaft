from pyraft.core.roles.interface import Role
from pyraft.data.messages import RequestVoteResp, RequestVoteReq, AppendRecordsReq


class Leader(Role):

    def run(self):
        self.state.timer = None

    def append_records(self, data: AppendRecordsReq):
        pass

    def request_vote(self, data: RequestVoteReq):
        pass

    def update(self, data: RequestVoteResp):
        pass