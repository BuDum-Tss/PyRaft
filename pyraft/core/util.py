import random


class Timings:
    HEARTBEAT_TIME = 40 / 10
    BROADCAST_TIME = 40 / 10
    VOTE_TIMEOUT = 25 / 10

    @staticmethod
    def election_timeout():
        return random.Random().randint(25, 500) / 10
