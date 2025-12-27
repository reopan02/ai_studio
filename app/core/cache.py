from __future__ import annotations

import time
from dataclasses import dataclass
from threading import RLock
from typing import Generic, Optional, TypeVar

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class _Entry(Generic[V]):
    value: V
    expires_at: float


class TTLCache(Generic[K, V]):
    def __init__(self, *, ttl_seconds: float, max_items: int = 10_000):
        self._ttl = float(ttl_seconds)
        self._max = int(max_items)
        self._lock = RLock()
        self._data: dict[K, _Entry[V]] = {}

    def get(self, key: K) -> Optional[V]:
        now = time.monotonic()
        with self._lock:
            entry = self._data.get(key)
            if not entry:
                return None
            if entry.expires_at <= now:
                self._data.pop(key, None)
                return None
            return entry.value

    def set(self, key: K, value: V) -> None:
        now = time.monotonic()
        with self._lock:
            if len(self._data) >= self._max:
                self._evict_expired(now)
                if len(self._data) >= self._max:
                    self._data.pop(next(iter(self._data)), None)
            self._data[key] = _Entry(value=value, expires_at=now + self._ttl)

    def delete(self, key: K) -> None:
        with self._lock:
            self._data.pop(key, None)

    def _evict_expired(self, now: float) -> None:
        expired = [k for k, v in self._data.items() if v.expires_at <= now]
        for k in expired:
            self._data.pop(k, None)

