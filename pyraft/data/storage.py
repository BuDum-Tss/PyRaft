from typing import Dict

from abc import ABC, abstractmethod


class SyncObject(ABC):
    def __init__(self, shared_id: str, node=None):
        self.__id = shared_id
        self.__node = node

    @abstractmethod
    def syncdata(self) -> str:
        pass

    def update(self):
        self.__node.update(self.__id, self.syncdata())

    @abstractmethod
    def synchronize(self, syncdata: str):
        pass


class SyncStorage:
    def __init__(self):
        self.index2objects: Dict[str, SyncObject | str] = {}

    def index(self, shared_id: str, sync_object: SyncObject):
        if shared_id not in self.index2objects:
            self.index2objects[shared_id] = sync_object
        else:
            value = self.index2objects[shared_id]
            self.index2objects[shared_id] = sync_object
            if isinstance(value, str):
                sync_object.synchronize(value)
            else:
                sync_object.synchronize(value.syncdata())

    def update(self, shared_id: str, value: str):
        if shared_id not in self.index2objects:
            self.index2objects[shared_id] = value
        else:
            self.index2objects[shared_id].synchronize(value)
