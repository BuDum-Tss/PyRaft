from typing import Dict, Any


class SyncStorage:
    def __init__(self):
        self.index2objects: Dict[str, str] = {}

    def update(self, shared_id: str, value: Any):
        self.index2objects[shared_id] = value

    def get_value(self, key: str) -> str:
        return self.index2objects[key] if key in self.index2objects else None