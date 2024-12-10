from enum import Enum
from typing import Dict


class RoleName(Enum):
    follower = 0,
    candidate = 1,
    leader = 2


class Address:
    id: str
    host: str
    port: int

    @staticmethod
    def check_address(address: str):
        addr = address.split(":")
        if not addr[1].isdigit():
            raise ValueError("Invalid port")
        if addr[0].isalpha():
            return
        host = addr[0].split(".")
        if len(host) != 4:
            raise ValueError("Invalid address")
        for i in host:
            if not i.isdigit() or 256 < int(i) <= 0:
                raise ValueError("Invalid address")

    def __init__(self, node_id: str, address: str):
        Address.check_address(address)
        address = address.split(":")
        self.id = node_id
        self.host = address[0]
        self.port = int(address[1])

    def __str__(self):
        return f"{self.host}:{self.port}"


class Settings:

    @staticmethod
    def check_settings(self_id: str, nodes: Dict[str, str]):
        if self_id not in nodes.keys():
            raise ValueError("Node id must be in dict")
        if len(nodes.items()) < 3:
            raise ValueError("Nodes must be 3 ore more")

    def __init__(self, self_id: str, nodes: Dict[str, str]):
        Settings.check_settings(self_id, nodes)
        self.__node_id = self_id
        self.__nodes: Dict[str, Address] = {node_id: Address(node_id, address) for node_id, address in nodes.items()}

    @property
    def myself(self) -> Address:
        return self.__nodes[self.__node_id]

    @property
    def nodes(self) -> Dict[str, Address]:
        return self.__nodes
