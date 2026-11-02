"""Remember a few result slices so the next frame request can skip NetCDF.

The key includes the file size and modification time. A new run replaces the
cache entry instead of replaying the previous case.
"""
from __future__ import annotations

from collections import OrderedDict
import threading

_LOCK = threading.Lock()
_CACHE = OrderedDict()
_LIMIT = 8


def lookup(key):
    with _LOCK:
        value = _CACHE.get(key)
        if value is not None:
            _CACHE.move_to_end(key)
        return value


def store(key, value):
    with _LOCK:
        _CACHE[key] = value
        _CACHE.move_to_end(key)
        while len(_CACHE) > _LIMIT:
            _CACHE.popitem(last=False)
        return value


def clear():
    with _LOCK:
        _CACHE.clear()
