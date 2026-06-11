from collections import Counter
from threading import Lock


class MetricsStore:
    def __init__(self):
        self._lock = Lock()
        self.events = Counter()
        self.failures = Counter()

    def record_event(self, event_type: str, channel: str):
        with self._lock:
            self.events[event_type] += 1
            self.events[f'{event_type}:{channel}'] += 1

    def record_failure(self, reason: str):
        with self._lock:
            self.failures[reason] += 1

    def snapshot(self):
        with self._lock:
            return {
                'events': dict(self.events),
                'failures': dict(self.failures),
            }


metrics_store = MetricsStore()
