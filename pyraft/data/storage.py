from typing import Dict, Any


class SyncStorage:
    def __init__(self):
        self.index2objects: Dict[str, str] = {}

    def update(self, shared_id: str, value: Any, ttl: int = None) -> bool:
        self.index2objects[shared_id] = value
        return True

    def get_value(self, key: str) -> Any:
        return self.index2objects[key] if key in self.index2objects else None

    def get_version(self, key: str) -> int:
        return 0