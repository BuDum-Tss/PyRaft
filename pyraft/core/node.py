import uvicorn

from pyraft.api import prepare_node_api
from pyraft.core.transport import TransportService
from pyraft.data.settings import Settings
from pyraft.data.state import State
from pyraft.data.storage import SyncStorage
from pyraft.syncobjects import SyncObject


class Node:
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.state = State(settings)
        self.storage = SyncStorage()

        self.transport_service: TransportService = TransportService(self.state, self.settings)
        self.api = prepare_node_api(self.transport_service)
        [host, port] = settings.self_address.split(":")
        uvicorn.run(self.api, host=host, port=int(port))

    def index(self, shared_id: str, sync_object: SyncObject):
        self.storage.index(shared_id, sync_object)

    def update(self, shared_id: str, value):
        # TODO: redirect to leader
        pass
