"""Bounded, process-local cache for result-variable inventory responses."""
from collections import OrderedDict
from pathlib import Path
import threading


def _file_revision(path):
    if path is None:
        return None
    resolved = Path(path).resolve()
    try:
        stat = resolved.stat()
    except OSError:
        return (str(resolved), 'absent')
    return (str(resolved), int(stat.st_size), int(stat.st_mtime_ns), int(stat.st_ino))


def inventory_key(case_path, output_files):
    """Include case identity and each expected output, including absent files."""
    case = str(Path(case_path).resolve()) if case_path is not None else None
    names = ('2d', '3d', 'legacy3d')
    primary = tuple((name, _file_revision(output_files.get(name))) for name in names)
    companions = tuple(_file_revision(path) for path in output_files.get('3d_candidates', ()))
    return (case, primary, companions)


class ResultInventoryCache:
    """Small LRU of JSON-ready inventories; output metadata changes invalidate."""
    def __init__(self, max_entries=8):
        self.max_entries = max(1, int(max_entries))
        self._items = OrderedDict()
        self._lock = threading.RLock()
        self.hits = 0
        self.misses = 0

    def get(self, key):
        with self._lock:
            value = self._items.get(key)
            if value is None:
                self.misses += 1
                return None
            self.hits += 1
            self._items.move_to_end(key)
            return value

    def put(self, key, value):
        with self._lock:
            self._items[key] = value
            self._items.move_to_end(key)
            while len(self._items) > self.max_entries:
                self._items.popitem(last=False)

    def clear(self):
        with self._lock:
            self._items.clear()
            self.hits = self.misses = 0

    def info(self):
        with self._lock:
            return {'entries': len(self._items), 'max_entries': self.max_entries,
                    'hits': self.hits, 'misses': self.misses}
