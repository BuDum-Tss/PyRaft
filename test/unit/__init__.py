from .follower_test import FollowerTest
from .node_test import NodeTest
from .transport_test import TestTransport


def run():
    FollowerTest().test_append_requests()
    #NodeTest().test_node()
    #TestTransport().test_api()
