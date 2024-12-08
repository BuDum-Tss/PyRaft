import logging
from copy import copy
from threading import Thread
from typing import Dict

from pyraft.core import Role
from pyraft.core.api import SenderApi
from pyraft.core.roles import Follower, Candidate, Leader
from pyraft.data import State
from pyraft.data.enums import RoleName


class Controller(Thread):
    def __init__(self, start_role, state: State, sender: SenderApi):
        super().__init__()
        self.state = state
        self.sender = sender
        self._role: Role = None
        self._interrupted = False
        self._role_name: RoleName = start_role

    def run(self):
        while not self._interrupted:
            logging.info(f" === {self._role_name} === ")
            match self._role_name:
                case RoleName.follower:
                    self._role = Follower(self.state, self.sender)
                case RoleName.candidate:
                    self._role = Candidate(self.state, self.sender)
                case RoleName.leader:
                    self._role = Leader(self.state, self.sender)
            self.state.role_changed = False
            if self.state.lock.locked():
                self.state.lock.release()
            logging.info(f"=== State === \n" +
                         f"role_changed = {self.state.role_changed}\n" +
                         f"term = {self.state.term}\n" +
                         f"locked = {self.state.lock.locked()}")
            self._role_name = self._role.run()

    def stop(self):
        self._interrupted = True
        self._role.stop()

    @property
    def current(self) -> Role:
        return self._role
