import unittest
from multiprocessing import Process

from pyraft import Node, Settings
from pyraft.core.api import SenderApi
from pyraft.data.messages import AppendRecordsReq, Record
from pyraft.transport.sender import HttpSender
from pyraft.syncobj import SyncString


def send_message():
    sender: SenderApi = HttpSender()
    req: AppendRecordsReq = AppendRecordsReq(idx=0,
                                             term=1,
                                             leader_id="node1",
                                             prev_log_index=0,
                                             prev_log_term=0,
                                             entries=[Record(shared_object_id="value", value="value2")])
    sender.append_records("localhost:2222", req)


class FollowerTest(unittest.TestCase):
    def test_append_requests(self):
        settings = Settings("node2", {"node1": "localhost:1111", "node2": "localhost:2222", "node3": "localhost:3333"})
        node = Node(settings)
        string: SyncString = SyncString("value", value="value", node=node)
        p1 = Process(target=send_message)
        p1.start()
        while string.value == "value":
            pass
        self.assertEqual(string.value, "value2")
