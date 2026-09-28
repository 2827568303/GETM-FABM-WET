"""Phase 3 endpoint smoke tests using Flask test client.

Run: python _test_phase3.py
"""
import sys
import io
import json
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from server import app, DATA_DIR

client = app.test_client()

def ok_or(label, resp, expected_status=200):
    status = resp.status_code
    body = resp.get_data(as_text=True)
    ok = status == expected_status
    print(f"{'PASS' if ok else 'FAIL'} {label}: HTTP {status}")
    if not ok:
        print(f"     body: {body[:300]}")
    return resp

print("=== Phase 3 smoke tests ===\n")

# --- p3-1: upload endpoint ---
# 1a. Load Theoretical lake case so active_case_path is set
resp = client.post('/api/case/load', json={'case_name': 'Theoretical lake'})
ok_or('load case', resp)

# 1b. Add a calibration point to attach data to
resp = client.post('/api/calibration/points', json={
    'name': 'TestPt', 'i': 12, 'j': 10, 'variables': ['temp']
})
ok_or('add calib point', resp)
pid = resp.get_json()['point']['id']
print(f"     point_id = {pid}")

# 1c. Upload a sample CSV
csv_content = "time,value\n2020-01-01 12:00:00,15.5\n2020-01-02 12:00:00,16.0\n2020-01-03 12:00:00,16.5\n"
resp = client.post('/api/calibration/upload', data={
    'file': (io.BytesIO(csv_content.encode('utf-8')), 'sample.csv'),
    'point_id': pid,
    'variable': 'temp',
}, content_type='multipart/form-data')
ok_or('upload CSV', resp)
data = resp.get_json()
if data.get('success'):
    print(f"     stored={data['stored']} total_rows={data['total_rows']}")

# 1d. Upload an XLSX with variable column (multi-variable)
try:
    from openpyxl import Workbook
    wb = Workbook(); ws = wb.active
    ws.append(['time', 'value', 'variable'])
    ws.append(['2020-01-01', 10.0, 'temp'])
    ws.append(['2020-01-02', 11.0, 'temp'])
    ws.append(['2020-01-01', 5.0, 'abiotic_water_sO2W'])
    ws.append(['2020-01-02', 5.5, 'abiotic_water_sO2W'])
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tf:
        wb.save(tf.name); tf.flush()
        with open(tf.name, 'rb') as fh:
            resp = client.post('/api/calibration/upload', data={
                'file': (fh, 'multi.xlsx'),
                'point_id': pid,
                'variable': 'temp',
            }, content_type='multipart/form-data')
        ok_or('upload XLSX multi-variable', resp)
        data = resp.get_json()
        if data.get('success'):
            print(f"     stored={data['stored']} total_rows={data['total_rows']}")
    Path(tf.name).unlink(missing_ok=True)
except ImportError:
    print("SKIP XLSX test (openpyxl not installed)")

# 1e. Verify data was stored
resp = client.get(f'/api/calibration/data?point_id={pid}&variable=temp')
ok_or('fetch stored data', resp)
values = resp.get_json()
print(f"     temp records: {len(values)}")

# --- p3-2: comparison endpoint with scatter_pairs ---
resp = client.get(f'/api/calibration/comparison?point_id={pid}&variable=temp')
ok_or('comparison endpoint', resp)
data = resp.get_json()
print(f"     observed={len(data.get('observed', []))} simulated_len={len(data.get('simulated', {}).get('values', []))}")
print(f"     scatter_pairs={len(data.get('scatter_pairs', []))}")
print(f"     axis_range={data.get('axis_range')}")

# --- p3-4: auto/start + status ---
# Try invalid params first
resp = client.post('/api/calibration/auto/start', json={
    'method': 'parsac', 'iterations': 5, 'objective': 'rmse', 'params': []
})
ok_or('start with empty params (should 400)', resp, expected_status=400)

# Valid request (will start a job that may fail since model output may be empty)
resp = client.post('/api/calibration/auto/start', json={
    'method': 'parsac', 'iterations': 3, 'objective': 'rmse',
    'params': [
        {'module': 'POM', 'param': 'kDMinW', 'min': 0.005, 'max': 0.1},
    ],
})
ok_or('start valid auto-calib', resp)
job_data = resp.get_json()
if job_data.get('success'):
    job_id = job_data['job_id']
    print(f"     job_id = {job_id}")
    # Status endpoint
    resp = client.get(f'/api/calibration/auto/status?job_id={job_id}')
    ok_or('status query', resp)
    status_data = resp.get_json()
    print(f"     status = {status_data.get('status')} progress={status_data.get('progress')}")

    # Stop endpoint
    resp = client.post('/api/calibration/auto/stop', json={'job_id': job_id})
    ok_or('stop job', resp)

    # Status of non-existent job
    resp = client.get('/api/calibration/auto/status?job_id=nonexistent')
    ok_or('status of missing job (404)', resp, expected_status=404)
else:
    print("     auto/start did not return success")

# --- cleanup test point ---
resp = client.delete(f'/api/calibration/points?id={pid}')
ok_or('delete test point', resp)

print("\n=== Phase 3 smoke tests complete ===")
