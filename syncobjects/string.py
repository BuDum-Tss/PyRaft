
from pyraft import Node, SyncObject


class SyncString(SyncObject):
    def __init__(self, shared_id: str, value=None, cluster: Node = None):
        super().__init__(shared_id, cluster)
        self.__value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value
        self.update(self.__value)

    def synchronize(self, value: str):
        self.__value = value
