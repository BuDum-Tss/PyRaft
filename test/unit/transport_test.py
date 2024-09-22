import unittest
from typing import Tuple

from pyraft.core.api import ReceiverApi
from pyraft.data import Address
from pyraft.data.messages import UpdateValueReq, RequestVoteReq, RequestVoteResp, AppendRecordsReq, AppendRecordsResp
from pyraft.transport.receiver import Proxy
from pyraft.transport.sender import HttpSender


class TestReceiver(ReceiverApi):
    def __init__(self, append_records_resp: AppendRecordsResp, request_vote_resp: RequestVoteResp,
                 update_value_resp: int):
        self.append_records_resp = append_records_resp
        self.request_vote_resp = request_vote_resp
        self.update_value_resp = update_value_resp
        self.append_records_req = None
        self.request_vote_req = None
        self.update_value_req = None

    def append_records(self, data: AppendRecordsReq) -> AppendRecordsResp:
        self.append_records_req = data
        return self.append_records_resp

    def request_vote(self, data: RequestVoteReq) -> RequestVoteResp:
        self.request_vote_req = data
        return self.request_vote_resp

    def update(self, data: UpdateValueReq) -> Tuple[int, str]:
        self.update_value_req = data
        return self.update_value_resp, "ok"


class TestTransport(unittest.TestCase):
    def test_api(self):
        append_records_req = AppendRecordsReq(term=1, leader_id="leader", prev_log_index=0, entries=[])
        request_vote_req = RequestVoteReq(term=1, candidate_id="candidate", last_log_index=0, last_log_term=0)
        update_value_req = UpdateValueReq(shared_object_id="id", value="value")
        append_records_resp = AppendRecordsResp(term=0, success=0)
        request_vote_resp = RequestVoteResp(term=0, vote_granted=True)
        update_value_resp = 200
        leader_id = "leader"
        address = "localhost:8000"
        receiver = TestReceiver(append_records_resp, request_vote_resp, update_value_resp)
        p = Proxy(receiver=lambda: receiver, self_node=Address(leader_id, address))
        p.start()
        sender = HttpSender()

        sender.update(address, update_value_req)
        self.assertEqual(update_value_req, receiver.update_value_req)

        sender.append_records("localhost:8000", append_records_req)
        self.assertEqual(append_records_resp, receiver.append_records_resp)
        sender.request_vote("localhost:8000", request_vote_req)
        self.assertEqual(request_vote_resp, receiver.request_vote_resp)
        p.shutdown()
