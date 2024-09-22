from typing import Dict

from abc import ABC, abstractmethod

from pyraft.node import Node


class SyncObject(ABC):
    def __init__(self, shared_id: str, cluster: Node = None):
        self.__id = shared_id
        self.__cluster = cluster

    def update(self, value: str):
        self.__cluster.update(self.__id, value)

    @abstractmethod
    def synchronize(self, value: str):
        pass

class SyncStorage:
    def __init__(self):
        self.index2objects: Dict[str, SyncObject] = {}

    def index(self, shared_id: str, sync_object: SyncObject):
        self.index2objects[shared_id] = sync_object

    def update(self, shared_id: str, value: str):
        self.index2objects[shared_id]._synchronize(value)

