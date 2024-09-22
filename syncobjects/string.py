from pyraft import Node, SyncObject


class SyncString(SyncObject):

    def __init__(self, shared_id: str, value=None, node: Node = None):
        super().__init__(shared_id, node)
        self.__value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value
        self.update()

    def syncdata(self) -> str:
        return self.__value

    def synchronize(self, syncdata: str):
        self.__value = syncdata
