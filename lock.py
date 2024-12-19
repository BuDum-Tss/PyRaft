import argparse
import json
import logging

from random import random
from threading import Timer
from time import sleep

import requests
import random
from typing import Any, override, List, Dict

import uvicorn

from pyraft import Node, SyncStorage
from pyraft.data.util import Settings
from pyraft.log import set_logging
from pyraft.transport.receiver import api


class DistributedLock:
    TIMEOUT = 20

    def __init__(self, name: str, owner: str, nodes: List[str]):
        self.name = name
        self.owner = owner
        self.nodes = nodes
        self.version = None
        self.locked = False

    def __enter__(self):
        while not self.locked:
            self.try_lock()

    def __exit__(self, type, value, tb):
        self.locked = self.unlock()
        #print(f"{self.name} locked: {self.locked}")

    @property
    def server(self):
        return self.nodes[random.randint(0, len(self.nodes) - 1)]

    def try_lock(self):
        self.locked, self.version, error = self._compare_and_swap(self.name, True, False, self.version)
        #print(f"{self.locked}, {self.version}, {error} - c&s lock 1")
        if error != 200:
            self.locked, self.version, error = self._compare_and_swap(self.name, True, None, self.version)
            #print(f"{self.locked}, {self.version}, {error} - c&s lock 2")
        return self.locked

    def unlock(self):
        locked, version, error = self._compare_and_swap(self.name, None, True, self.version)
        #print(f"{locked}, {version}, {error} - c&s unlock")
        #print(f"{self.name} locked: {locked}")
        return locked

    def _compare_and_swap(self, key, swap_value, compare_value, version=None) -> tuple[bool | None, int | None, int]:
        with requests.Session() as session:
            print(f"c&s({key}, {swap_value}, {compare_value})")

            data = {
                "key": key,
                "value": {
                    "compare": {"value": compare_value, "owner": self.owner} if compare_value is not  None else None,
                    "swap": {"value": swap_value, "owner": self.owner} if swap_value is not  None else None,
                    "owner": self.owner,
                    "version": version
                }
            }
            print(json.dumps(data))
            while True:
                try:
                    server = self.server
                    print(server)
                    post_response: requests.Response = session.post(f"http://{server}/set", data=json.dumps(data),
                                                                    headers={"Content-Type": "application/json",
                                                                             "TTL": str(self.TIMEOUT)},
                                                                    timeout=self.TIMEOUT)
                    break
                except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                    print("ConnectionError. Selecting new server...")
                    pass
            if post_response.status_code == 200 or post_response.status_code == 409:
                return post_response.status_code == 200, post_response.headers['Version'] if post_response.headers['Version'] != 'None' else None, post_response.status_code
            else:
                return None, None, post_response.status_code


class LockStorage(SyncStorage):

    def __init__(self):
        super().__init__()
        self.data = {}
        self.versions = {}
        self.timers = {}

    @override
    def update(self, key: str, value: Any, ttl: int = None) -> bool:
        if "compare" in value and self.get_value(key) == value["compare"] and self.get_version(key) == value["version"]:
            logging.info("c&s applied")
        elif "compare" in value:
            logging.info("c&s rejected")
            return False
        self.data[key] = value
        self.versions[key] = self.versions[key] + 1 if key in self.versions else 0
        if ttl:
            self.timers[key] = Timer(ttl, lambda: self.auto_delete(key))
            self.timers[key].start()
        return True

    def auto_delete(self, key: str):
        self.data.pop(key)
        self.versions.pop(key)
        self.timers.pop(key)

    @override
    def get_value(self, key: str) -> Any:
        return self.data[key] if key in self.data else None

    @override
    def get_version(self, key: str) -> int:
        print(f"get_version({key}) -> {self.versions}")
        return self.versions[key] if key in self.versions else None


# philosopher

def set_lock_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Raft server")
    parser.add_argument("-l", "--left", type=str, help="left fork id")
    parser.add_argument("-r", "--right", type=str, help="right fork id")
    parser.add_argument("-c", "--config", type=argparse.FileType('r'), help="config nodes file")
    return parser


def philosopher():
    parser = set_lock_parser()
    args = parser.parse_args()
    config: Dict[str, str] = json.load(args.config)
    print("philosopher came to lunch")
    name =  args.left+"_philo_"+args.right
    left_fork = DistributedLock(args.left, name, list(config.values()))
    right_fork = DistributedLock(args.right,name, list(config.values()))
    try:
        while True:
            print("philosopher thinking...")
            sleep(random.randint(10, 30))
            print("philosopher takes forks")
            with left_fork:
                print("philosopher took left fork")
                with right_fork:
                    print("philosopher took right fork")
                    print("philosopher start eating...")
                    sleep(10)
                    print("philosopher finished eating")
    except InterruptedError:
        print("philosopher left lunch")
        pass


# Node

def set_node_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Raft server")
    parser.add_argument("-n", "--name", type=str, help="self name")
    parser.add_argument("-c", "--config", type=argparse.FileType('r'), help="config file")
    return parser


def node():
    parser = set_node_parser()
    args = parser.parse_args()
    name = args.name
    config: Dict[str, str] = json.load(args.config)
    addr = config[name]
    host, port = tuple(addr.split(":"))
    api.title = name
    set_logging(log_file=f"{name}.log")
    api.node = Node(Settings(name, config), sync_storage=LockStorage())
    try:
        uvicorn.run(api, host=host, port=int(port))
    except KeyboardInterrupt:
        pass
