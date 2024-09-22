from .node_test import NodeTest
from .transport_test import TestTransport


def run():
    NodeTest().test_node()
    TestTransport().test_api()
