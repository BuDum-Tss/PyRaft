from typing import List

from pyraft.syncobjects import SyncObject


class Cluster:
    def __init__(self, address: str, node_addresses: List[str]):
        self.address = address
        self.node_addresses = node_addresses
        self.role = None
        self.indexed_objects = {}

    def index(self, shared_id: str, sync_object: SyncObject):
        self.indexed_objects[shared_id] = sync_object

    def update(self, shared_id: str, value):
        pass

    def __syncronize(self, shared_id: str):
        pass