import argparse
import json
from typing import Dict

from pyraft import Node
from pyraft.syncobjects import SyncObject


def main(self_address: str, node_addresses: Dict[str, str]):
    cluster = Node(self_address, list(node_addresses.values()))
    obj = SyncObject("sync_value", value="default", cluster=cluster)
    while True:
        input_args = input("> ").split(" ")
        match input_args[0]:
            case "exit":
                break
            case "set":
                obj.value = input_args[1]
            case "get":
                print(obj.value)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Videos to images')
    parser.add_argument('name', type=str, help='Server name')
    args = parser.parse_args()
    with open("config.json", 'r') as file:
        node_addresses: dict = json.load(file)
    if args.name not in node_addresses:
        print("Node not found at config")
    self_address = node_addresses[args.name]
    del node_addresses[args.name]
    main(self_address, node_addresses)
    print("Finished...")
