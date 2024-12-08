import unittest
from multiprocessing import Process
from time import sleep

from pyraft import Node, Settings
from pyraft.syncobj import SyncString


def run_node1(self):
    settings = Settings("node1", {"node1": "localhost:1111", "node2": "localhost:2222", "node3": "localhost:3333"})
    node = Node(settings)
    string: SyncString = SyncString("value", value="value", node=node)
    string.value = "hello"
    while string.value == "value":
        sleep(1)
    self.assertEqual(string.value, "hello")


def run_node2(self):
    settings = Settings("node2", {"node1": "localhost:1111", "node2": "localhost:2222", "node3": "localhost:3333"})
    node = Node(settings)
    string: SyncString = SyncString("value", value="value", node=node)
    while string.value == "value":
        sleep(1)
    self.assertEqual(string.value, "hello")


def run_node3(self):
    settings = Settings("node3", {"node1": "localhost:1111", "node2": "localhost:2222", "node3": "localhost:3333"})
    node = Node(settings)
    string: SyncString = SyncString("value", value="value", node=node)
    while string.value == "value":
        sleep(1)
    self.assertEqual(string.value, "hello")


class NodeTest(unittest.TestCase):
    def test_node(self):
        p1 = Process(target=run_node1)
        p2 = Process(target=run_node2)
        p3 = Process(target=run_node3)
        p1.start()
        p2.start()
        p3.start()
        p1.join()
        p2.join()
        p3.join()
