from pyraft.cluster import Cluster


class SyncObject:
    def __init__(self, shared_id: str, value=None, cluster: Cluster = None):
        self.__value = value
        self.__id = shared_id
        self.__cluster = cluster

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value
        self.__cluster.update(self.__id, self.__value)

    def __hash__(self):
        return hash(self.__value)