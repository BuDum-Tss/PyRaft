from pyraft.data.messages import RequestVoteReq, RequestVoteResp, AppendRecordsReq, AppendRecordsResp, UpdateValueReq


class Receiver:
    def __init__(self, state, settings):
        self.settings = settings
        self.state = state

    def append_records(self, data: AppendRecordsReq) -> AppendRecordsResp:
        # TODO: implementation
        return AppendRecordsResp(term=0, success=True)

    def request_vote(self, data: RequestVoteReq) -> RequestVoteResp:
        # TODO: implementation
        if data.term < self.state.current_term:
            return RequestVoteResp(term=self.state.current_term, vote_granted=self.state.current_term)
        if (self.state.voted_for is None or data.candidate_id is None) and (
                data.last_log_term >= self.state.current_term and data.last_log_index >= self.state.last_log_index):
            return RequestVoteResp(term=self.state.current_term,
                                   vote_granted=True)
        else:
            return RequestVoteResp(term=self.state.current_term, vote_granted=False)

    def update(self, data: UpdateValueReq) -> int:
        # TODO: implementation
        return 307