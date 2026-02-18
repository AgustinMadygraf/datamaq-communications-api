import threading
import time

from src.use_cases.ports import RateLimiterGateway


class InMemoryRateLimiterGateway(RateLimiterGateway):
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._events_by_key: dict[str, list[float]] = {}

    def hit(self, key: str, window_seconds: int, max_requests: int) -> bool:
        now = time.time()
        threshold = now - max(window_seconds, 1)

        with self._lock:
            events = self._events_by_key.get(key, [])
            events = [event for event in events if event >= threshold]
            if len(events) >= max(max_requests, 1):
                self._events_by_key[key] = events
                return False

            events.append(now)
            self._events_by_key[key] = events
            return True
