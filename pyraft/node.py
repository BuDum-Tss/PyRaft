import uvicorn

#from pyraft.transport import prepare_receiver
#from pyraft.data import State, SyncStorage
#from pyraft.data.settings import Settings
#from pyraft.syncobjects import SyncObject


class Node:
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        #self.state = State(settings)
        #self.storage = SyncStorage()
        #self.transport_service: Receiver = Receiver(self.state, self.settings)
        #self.api = prepare_receiver(self.transport_service)
        #[host, port] = settings.self_address.split(":")
        #uvicorn.run(self.api, host=host, port=int(port))

    def index(self, shared_id: str, sync_object):
        self.storage.index(shared_id, sync_object)

    def update(self, shared_id: str, value):
        # TODO: redirect to leader
        pass
