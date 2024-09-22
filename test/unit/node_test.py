import unittest

from pyraft import Node, Settings
from syncobjects import SyncString


class NodeTest(unittest.TestCase):
    def test_node(self):
        settings = Settings("node1", {"node1": "localhost:1111", "node2": "localhost:2222", "node3": "localhost:3333"})
        node = Node(settings)
        str: SyncString = SyncString("value", node=node)
        str.value = "hello"
        str.value = "world"
        self.assertEqual(None, None)
