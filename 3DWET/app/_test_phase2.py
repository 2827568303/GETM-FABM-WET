"""Phase 2 verification — exercise new visualization endpoints via Flask test client."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from server import app, active_case_path, CASE_DIR, Path

# Load Theoretical lake case as if user clicked "load"
client = app.test_client()
r = client.post('/api/case/load', json={'case_name': 'Theoretical lake'})
load_resp = r.get_json()
print(f"[1] /api/case/load -> success={load_resp.get('success')} has_results={load_resp.get('has_results')}")
print(f"    output_warning={load_resp.get('output_warning')[:50] if load_resp.get('output_warning') else None}...")

# Test state_vars_surface
r = client.get('/api/results/state_vars_surface')
sv = r.get_json()
if sv.get('error'):
    print(f"[2] /api/results/state_vars_surface -> error: {sv['error']}")
else:
    print(f"[2] /api/results/state_vars_surface -> vars: {list(sv.keys())}")
    for vname, info in list(sv.items())[:2]:
        shape = info.get('shape', [])
        print(f"    {vname}: shape={shape} min={info.get('min')} max={info.get('max')} mean={info.get('mean')} units={info.get('units')!r}")

# Test 3d_surface
r = client.get('/api/results/3d_surface?var=temp&time=0')
ts = r.get_json()
if ts.get('error'):
    print(f"[3] /api/results/3d_surface?var=temp -> error: {ts['error']}")
else:
    print(f"[3] /api/results/3d_surface?var=temp -> shape={ts.get('shape')} min={ts.get('min')} max={ts.get('max')} long_name={ts.get('long_name')!r}")

# Test timeseries_polygon (pick a small polygon from the grid)
r = client.post('/api/results/timeseries_polygon', json={'var': 'temp', 'polygon': [[5,5],[15,5],[15,15],[5,15]]})
poly = r.get_json()
if poly.get('error'):
    print(f"[4] /api/results/timeseries_polygon -> error: {poly['error']}")
else:
    n = len(poly.get('values', []))
    print(f"[4] /api/results/timeseries_polygon -> n_cells={poly.get('n_cells')} series_len={n} units={poly.get('units')!r}")
    if n > 0:
        print(f"    first value={poly['values'][0]}  last value={poly['values'][-1]}")

print("\nAll Phase 2 endpoint smoke checks complete.")
