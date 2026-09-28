# -*- coding: utf-8 -*-
"""End-to-end test v2: strict browser-like JSON parsing + concurrent-read stress
(the exact scenario that crashed netcdf.dll with 0xC0000005)."""
import sys, io, json, time, subprocess, threading, urllib.request, urllib.error, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = "http://localhost:8767"
APP_DIR = r"C:\Users\dinod\Desktop\GETM-FABM-WET\3DWET\app"
PYTHON = r"C:\ProgramData\anaconda3\python.exe"
lines = []

def log(s): lines.append(str(s))

def browser_parse(text):
    return json.loads(text, parse_constant=lambda c: (_ for _ in ()).throw(ValueError(f"non-JSON constant: {c}")))

_opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

def req(path, payload=None, timeout=120):
    url = BASE + path
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        r = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    else:
        r = urllib.request.Request(url, method="GET")
    try:
        with _opener.open(r, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")

def check_response(tag, status, text, expect_data=True):
    try:
        obj = browser_parse(text)
        ok = "OK"
    except Exception as e:
        obj = None
        ok = f"FAIL: {e}"
    has_nan = ("NaN" in text) or ("Infinity" in text)
    log(f"[{tag}] HTTP {status}  strict_parse={ok}  raw_NaN={has_nan}  len={len(text)}")
    if expect_data and obj and isinstance(obj, dict) and obj.get("error"):
        log(f"    endpoint error: {obj['error']}")
    return obj

def load_case(name):
    st, txt = req("/api/case/load", {"case_name": name})
    obj = check_response(f"load:{name}", st, txt)
    if isinstance(obj, dict):
        log(f"    has_results={obj.get('has_results')} output_ntimesteps={obj.get('output_ntimesteps')}")

def run_tests():
    up = False
    for i in range(60):
        try:
            req("/api/cases")
            up = True
            break
        except Exception:
            time.sleep(0.5)
    if not up:
        log("SERVER DID NOT START")
        return

    st, txt = req("/api/cases")
    cases = check_response("cases", st, txt)
    if isinstance(cases, list):
        log(f"    cases: {[c['name'] for c in cases]}")

    load_case("Lake Dianchi")
    st, txt = req("/api/results/2d?var=temp&time=0&level=5")
    d2 = check_response("2d:temp (Dianchi)", st, txt)
    if d2 and not d2.get("error"):
        n_null = sum(1 for row in d2["data"] for v in row if v is None)
        log(f"    rows={len(d2['data'])} nulls={n_null} min={d2.get('min')} max={d2.get('max')}")

    # ── CFL guard tests (deterministic: manipulate getm.inp directly) ──
    INP = r"C:\Users\dinod\Desktop\GETM-FABM-WET\3DWET\case\Lake Dianchi\getm.inp"
    orig_inp = open(INP, encoding="utf-8", errors="replace").read()
    try:
        open(INP, "w", encoding="utf-8").write(orig_inp.replace("timestep = 60", "timestep = 8640"))
        st, txt = req("/api/run/start", {})
        obj = check_response("run/start with dt=8640 inp (expect refuse)", st, txt)
        log(f"    refused={bool(obj and not obj.get('success'))} err={(obj or {}).get('error','')[:60]}")
    finally:
        open(INP, "w", encoding="utf-8").write(orig_inp)
    st, txt = req("/api/config/time", {"timestep": 8640})
    obj = check_response("config/time dt=8640 (expect reject)", st, txt)
    log(f"    rejected={bool(obj and not obj.get('success'))} err={(obj or {}).get('error','')[:60]}")
    st, txt = req("/api/config/time", {"timestep": 60})
    obj = check_response("config/time dt=60 (expect success)", st, txt)
    log(f"    saved={bool(obj and obj.get('success'))}")

    # ── concurrent-read stress: 8 parallel requests hitting output.nc ──
    # This exact pattern (browser parallel XHRs) killed the server via
    # netcdf.dll 0xC0000005 before the global NC lock existed.
    paths = [
        "/api/results/2d?var=temp&time=0&level=5",
        "/api/results/state_vars_surface",
        "/api/dashboard/summary",
        "/api/results/3d_surface?var=temp&time=0",
        "/api/results/profile?var=temp&time=0&i=40&j=20",
        "/api/results/variables",
        "/api/results/2d?var=temp&time=120&level=5",
        "/api/results/state_vars_surface",
    ]
    results = [None] * len(paths)
    def worker(idx, p):
        try:
            results[idx] = req(p, timeout=180)
        except Exception as e:
            results[idx] = ("EXC", str(e))
    threads = [threading.Thread(target=worker, args=(i, p)) for i, p in enumerate(paths)]
    t0 = time.time()
    for t in threads: t.start()
    for t in threads: t.join()
    log(f"concurrent stress: {len(paths)} parallel requests in {time.time()-t0:.1f}s")
    alive = True
    try:
        req("/api/cases")
    except Exception as e:
        alive = False
        log(f"SERVER DIED during concurrent stress: {e}")
    log(f"server alive after stress: {alive}")
    for i, (p, r) in enumerate(zip(paths, results)):
        if r is None:
            log(f"  #{i} {p} -> NO RESULT")
            continue
        st, txt = r
        if st == "EXC":
            log(f"  #{i} {p} -> EXC {txt[:120]}")
        else:
            ok = "OK" if browser_parse_ok(txt) else "PARSE-FAIL"
            log(f"  #{i} {p} -> HTTP {st} strict={ok} len={len(txt)}")

    st, txt = req("/api/results/3d_surface?var=temp&time=0")
    d3 = check_response("3d_surface (Dianchi)", st, txt)
    if d3 and not d3.get("error"):
        log(f"    shape={d3['shape']} min={d3['min']:.3f} max={d3['max']:.3f}")

    # numrecs=0 cases → clean 404
    for cname in ("Lake Luoma", "Theoretical lake"):
        load_case(cname)
        st, txt = req("/api/results/2d?var=temp&time=0&level=0")
        check_response(f"2d ({cname}, expect clean 404)", st, txt, expect_data=False)

    load_case("NativeTest")
    st, txt = req("/api/results/2d?var=temp&time=0&level=0")
    dn = check_response("2d (NativeTest all-NaN)", st, txt)
    if dn and not dn.get("error"):
        n_null = sum(1 for row in dn["data"] for v in row if v is None)
        log(f"    rows={len(dn['data'])} nulls={n_null} min={dn['min']} max={dn['max']}")

def browser_parse_ok(text):
    try:
        browser_parse(text)
        return True
    except Exception:
        return False

_env = os.environ.copy()
_env["WET_PORT"] = "8767"  # 不占用用户可能在用的 8766
server_proc = subprocess.Popen([PYTHON, "server.py"], cwd=APP_DIR, env=_env,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    run_tests()
finally:
    server_proc.terminate()
    try:
        server_proc.wait(timeout=10)
    except Exception:
        server_proc.kill()

open(r"C:\Users\dinod\Desktop\GETM-FABM-WET\3DWET\_e2e_result.txt", "w", encoding="utf-8").write("\n".join(lines))
print("E2E DONE")
