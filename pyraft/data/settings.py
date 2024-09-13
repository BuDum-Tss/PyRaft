from typing import Dict


class Settings:
    def __init__(self, self_id: str, nodes: Dict[str, str], access_token):
        self.__node_id = self_id
        self.__nodes = nodes
        self.__access_token = access_token

    @property
    def node_id(self):
        return self.__node_id

    @property
    def nodes(self):
        return self.__nodes

    @property
    def self_address(self):
        return self.__nodes[self.__node_id]

    @property
    def access_token(self):
        return self.__access_token()
