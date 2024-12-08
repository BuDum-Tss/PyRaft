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
        self.__nodes: Dict[str, Address] = {node_id: Address(node_id, address) for node_id, address in nodes.items()}

    @property
    def self_node(self) -> Address:
        """
        :return: Эту ноду
        """
        return self.__nodes[self.__node_id]

    @property
    def nodes(self) -> Dict[str, Address]:
        """
        :return: Словарь идентификатор ноды -> адрес
        """
        return self.__nodes
