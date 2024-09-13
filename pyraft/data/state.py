
from pyraft.data.enums import Role
from pyraft.data.settings import Settings


class State:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.leader_id = ""
        self.role = Role.follower

        self.current_term = 0  # промежуток времени, в который работает один лидер
        self.voted_for = None  # id кандидата, за которого проголосовала нода
        self.log: list = []  # список изменений, которые приходят от лидера

        self.commit_index = 0  # индекс последнего полученного от лидера изменения (еще не применено)
        self.last_applied = 0  # индекс последнего примененного изменения
        # Лидер
        self.next_index = []  # индекс следующей записи, которую запрашивает от лидера эта нода
        self.match_index = []  # индекс самого последнего лога лидера

    @property
    def leader_address(self):
        return self.settings.node_id[self.leader_id]
