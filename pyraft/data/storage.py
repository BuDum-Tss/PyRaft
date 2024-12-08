from typing import Dict

class SyncStorage:
    def __init__(self):
        self.index2objects: Dict[str, str] = {}

    def update(self, shared_id: str, value: str):
        self.index2objects[shared_id] = value

    def get_value(self, key: str) -> str:
        return self.index2objects[key]