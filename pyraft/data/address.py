
def check(address: str):
    addr = address.split(":")
    if not addr[1].isdigit():
        raise ValueError("Invalid port")
    if addr[0].isalpha():
        return
    host = addr[0].split(".")
    if len(host) != 4:
        raise ValueError("Invalid address")
    for i in host:
        if not i.isdigit() or 256 < int(i) <= 0:
            raise ValueError("Invalid address")


class Address:
    node_id: str
    host: str
    port: int

    def __init__(self, node_id: str, host: str, port: int):
        self.node_id = node_id
        self.host = host
        self.port = port

    def __init__(self, node_id: str, address: str):
        check(address)
        address = address.split(":")
        self.node_id = node_id
        self.host = address[0]
        self.port = int(address[1])

    def __str__(self):
        return f"{self.host}:{self.port}"