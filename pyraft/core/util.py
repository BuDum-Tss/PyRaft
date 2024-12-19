import random


class Timings:
    HEARTBEAT_TIME = 0.1
    VOTE_TIMEOUT = 1
    HEARTBEAT_TIMEOUT = 0.05

    @staticmethod
    def election_timeout():
        return random.Random().randint(10, 70) / 100
