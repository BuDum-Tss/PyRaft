import argparse
import json
from typing import Dict


def main(self_address: str, node_addresses: Dict[str, str]):
    pass


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
    print("Finished..,")
