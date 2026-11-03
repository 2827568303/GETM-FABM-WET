import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET' / 'app'))
from result_slice_cache import clear, lookup, store


def test_slice_cache_returns_the_latest_frame_for_the_same_file():
    clear()
    key = ('/tmp/lake.nc', 10, 20, 'temp', 0, 1, False, False)
    assert lookup(key) is None
    store(key, {'mean': 1.0})
    assert lookup(key)['mean'] == 1.0
    store(key, {'mean': 2.0})
    assert lookup(key)['mean'] == 2.0


def test_slice_cache_drops_the_oldest_entry_past_the_limit():
    clear()
    for index in range(9):
        store(('file', index), index)
    assert lookup(('file', 0)) is None
    assert lookup(('file', 8)) == 8
