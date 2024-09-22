from time import sleep

from .enums import RoleName
from .storage import SyncStorage
from .settings import Settings


class Log:
    def __init__(self, sync_storage: SyncStorage):
        self.log = []
        self.sync_storage = sync_storage

    def add(self, log_idx: int, shared_idx: str, value: str):
        self.log[log_idx] = (shared_idx, value)

    def apply(self, log_idx: int):
        shared_idx, value = self.log[log_idx]
        self.sync_storage.update(shared_idx, value)


class State:
    def __init__(self, settings: Settings, log: Log):
        self.settings = settings
        self.timer = None
        self.leader_id = ""

        self.role = RoleName.follower

        self.current_term = 0  # промежуток времени, в который работает один лидер
        self.voted_for = None  # id кандидата, за которого проголосовала нода
        self.log = log  # список изменений, которые приходят от лидера

        self.commit_index = 0  # индекс последнего полученного от лидера изменения (еще не применено)
        self.last_applied = 0  # индекс последнего примененного изменения
        # Лидер
        self.next_index = []  # индекс следующей записи, которую запрашивает от лидера эта нода
        self.match_index = []  # индекс самого последнего лога лидера

    @property
    def leader(self):
        while self.leader_id == "":
            sleep(1)
        return self.settings.nodes[self.leader_id]
