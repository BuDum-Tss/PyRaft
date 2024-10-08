from typing import Dict

from pyraft.data.address import Address


def check(self_id: str, nodes: Dict[str, str]):
    if self_id not in nodes.keys():
        raise ValueError("Node id must be in dict")
    if len(nodes.items()) < 3:
        raise ValueError("Nodes must be 3 ore more")


class Settings:
    def __init__(self, self_id: str, nodes: Dict[str, str]):
        check(self_id, nodes)
        self.__node_id = self_id
        self.__nodes = {node_id: Address(node_id, address) for node_id, address in nodes.items()}
        self.__election_timeout = 500  # Время ожидания сообщения от лидера, после которого нода начинает голосование (msec)

    @property
    def min_election_timeout(self):
        """
        :return: Минимальное время ожидания запроса от лидера (ms).
        """
        return self.__election_timeout

    @property
    def self_node(self):
        """
        :return: Идентификатор этой ноды
        """
        return self.__nodes[self.__node_id]

    @property
    def nodes(self):
        """
        :return: Словарь идентификатор ноды -> адрес
        """
        return self.__nodes
