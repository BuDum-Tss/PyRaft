from typing import Dict

from pyraft.data.address import Address


class Settings:
    def __init__(self, self_id: str, nodes: Dict[str, str]):
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
    def self(self):
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