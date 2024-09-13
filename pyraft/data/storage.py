from pyraft.syncobjects import SyncObject


class SyncStorage:
    def __init__(self):
        self.index2objects = {}

    def index(self, shared_id: str, sync_object: SyncObject):
        self.index2objects[shared_id] = sync_object

    def update(self, shared_id: str, value):
        pass
