import threading


class OverflowValue:
    """"Можно изменить значение только один раз"""

    def __init__(self, default=None, capacity=1, on_overflow=lambda: None):
        self.counter = 0
        self.capacity = capacity
        self.on_overflow = on_overflow
        self._value = default
        self._lock = threading.Lock()

    def get(self):
        with self._lock:
            return self._value

    def set(self, value) -> bool:
        result = False
        if self.counter < self.capacity:
            with self._lock:
                self._value = value
                self.counter += 1
                result = True
        if self.counter == self.capacity:
            self.on_overflow()
            return result
