from pyraft.core.roles.interface import Role
from pyraft.data.messages import RequestVoteResp, RequestVoteReq, AppendRecordsReq


class Candidate(Role):
    def run(self):
        pass

    def append_records(self, data: AppendRecordsReq):
        pass

    def request_vote(self, data: RequestVoteReq):
        pass

    def update(self, data: RequestVoteResp):
        pass