"""Record diagnostics for the intermittent integrity acceptance failure."""
import json
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / '3DWET/app'))
import calibration

original = calibration.validate_current_run_outputs
records = []

def observed(case, opener, **kwargs):
    report = original(case, opener, **kwargs)
    files = [{"name": p.name, "mtime_ns": p.stat().st_mtime_ns,
              "mtime": p.stat().st_mtime} for p in Path(case).glob('*.nc')]
    records.append(dict(started_at=kwargs.get('started_at'), files=files, health=report))
    return report

calibration.validate_current_run_outputs = observed
target = 'tests/test_calibration_integrity.py::test_legitimate_stop_between_output_intervals_is_valid'
code = 0
full = '--full' in sys.argv
attempts = 1 if full else (int(sys.argv[sys.argv.index('--attempts')+1]) if '--attempts' in sys.argv else 40)
for attempt in range(attempts):
    print(f'Attempt {attempt + 1}/{attempts}', flush=True)
    current = pytest.main(['-q', '--tb=long', '--showlocals'] +
                          (['3DWET/tests', 'tests'] if full else [target]))
    if current:
        code = current
        break
(Path(__file__).parent / ('integrity-full.json' if full else 'integrity-reproduction.json')).write_text(
    json.dumps(records, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
raise SystemExit(code)
