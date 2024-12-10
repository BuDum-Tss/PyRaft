import argparse
import json
import uvicorn
from typing import Dict

from pyraft import Node
from pyraft.data.util import Settings
from pyraft.log import set_logging
from pyraft.transport.receiver import api


def set_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Raft server")
    parser.add_argument("-n", "--name", type=str, help="self name")
    parser.add_argument("-c", "--config", type=argparse.FileType('r'), help="config file")
    return parser


def main():
    parser = set_parser()
    args = parser.parse_args()
    name = args.name
    config: Dict[str, str] = json.load(args.config)
    addr = config[name]
    host, port = tuple(addr.split(":"))
    api.title = name
    set_logging(log_file = f"{name}.log")
    api.node = Node(Settings(name, config))
    try:
        uvicorn.run(api, host=host, port=int(port))
    except KeyboardInterrupt:
        pass