# -*- coding: utf-8 -*-
"""P0 feature test: output subscription, run pre-flight check, geo/map endpoints,
ASCII (.dat/.csv) bathymetry import."""
import sys, io, json, time, subprocess, urllib.request, urllib.error

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = "http://localhost:8766"
APP_DIR = r"C:\Users\dinod\Desktop\GETM-FABM-WET\3DWET\app"
PYTHON = r"C:\ProgramData\anaconda3\python.exe"
lines = []


def log(s):
    lines.append(str(s))


_opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def req(path, payload=None, timeout=180):
    url = BASE + path
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        r = urllib.request.Request(url, data=data,
                                   headers={"Content-Type": "application/json"}, method="POST")
    else:
        r = urllib.request.Request(url, method="GET")
    try:
        with _opener.open(r, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")


def jget(path, tag):
    st, txt = req(path)
    try:
        obj = json.loads(txt)
    except Exception as e:
        log(f"[FAIL] {tag}: HTTP {st} bad json {e}: {txt[:200]}")
        return None
    log(f"[{tag}] HTTP {st} keys={sorted(obj.keys())[:12] if isinstance(obj, dict) else type(obj).__name__}")
    if isinstance(obj, dict) and obj.get("error"):
        log(f"    error: {obj['error']}")
    return obj


def run_tests():
    up = False
    for _ in range(80):
        try:
            req("/api/cases")
            up = True
            break
        except Exception:
            time.sleep(0.5)
    if not up:
        log("SERVER DID NOT START")
        return

    st, txt = req("/api/case/load", {"case_name": "Lake Dianchi"})
    log(f"[load Lake Dianchi] HTTP {st}")

    # 1 ── output subscription
    cfg = jget("/api/config/output", "config/output GET")
    if cfg:
        log(f"    sources={cfg.get('sources')} wildcard={cfg.get('has_wildcard')}")
        log(f"    modules={[m['name'] for m in cfg.get('modules', [])]}")
        log(f"    estimate={cfg.get('estimate')}")

    st, txt = req("/api/config/output", {"preset": "minimal"})
    obj = json.loads(txt) if txt else {}
    log(f"[preset=minimal] HTTP {st} sources={obj.get('sources')} est={obj.get('estimate', {}).get('gb')} GB")

    st, txt = req("/api/config/output", {"preset": "standard"})
    obj = json.loads(txt) if txt else {}
    log(f"[preset=standard] HTTP {st} sources={obj.get('sources')} est={obj.get('estimate', {}).get('gb')} GB")

    st, txt = req("/api/config/output", {"preset": "all"})
    obj = json.loads(txt) if txt else {}
    log(f"[preset=all] HTTP {st} sources={obj.get('sources')} est={obj.get('estimate', {}).get('gb')} GB")
    log(f"    warning={obj.get('warning')}")

    # leave the case on the sane 'standard' preset
    st, txt = req("/api/config/output", {"preset": "standard"})
    log(f"[restore standard] HTTP {st}")

    # 2 ── pre-flight check
    chk = jget("/api/run/check", "run/check")
    if chk:
        log(f"    ok={chk.get('ok')} blocking={chk.get('blocking')} n_warn={chk.get('n_warn')}")
        for c in chk.get("checks", []):
            log(f"      [{c['level']}] {c['title']}: {str(c.get('detail'))[:110]}")

    # 3 ── geo / map
    g = jget("/api/geo/grid", "geo/grid")
    if g and not g.get("error"):
        log(f"    grid={g.get('nx')}x{g.get('ny')} stride={g.get('stride')} "
            f"has_lonlat={g.get('has_lonlat')} bounds={g.get('bounds')} dx={g.get('dx')}")
    f = jget("/api/geo/field?var=temp&time=0&level=-1", "geo/field")
    if f and not f.get("error"):
        log(f"    var={f.get('var')} min={f.get('min')} max={f.get('max')}")

    # 4 ── ASCII / .dat imports
    xyz = "lon,lat,depth\n102.70,24.90,3.2\n102.71,24.91,4.5\n102.72,24.90,2.8\n" \
          "102.70,24.92,1.9\n102.69,24.89,5.1\n102.73,24.93,2.2\n"
    r = multipart("/api/preprocess/bathymetry/upload_xyz",
                  {"crs": "auto"}, ("file", "bathy.csv", xyz))
    log(f"[upload_xyz CSV] HTTP {r[0]} -> {json.dumps(r[1])[:260]}")

    dat = "x\ty\tz\n-243000\t2581000\t4.4\n-242500\t2581500\t3.1\n-242000\t2582000\t5.0\n" \
          "-241500\t2581000\t2.2\n-242000\t2580500\t6.1\n-243000\t2582000\t1.4\n"
    r = multipart("/api/preprocess/bathymetry/upload_xyz",
                  {"crs": "projected"}, ("file", "bathy.dat", dat))
    log(f"[upload_xyz TAB .dat] HTTP {r[0]} -> {json.dumps(r[1])[:260]}")

    try:
        hyp = open(r"D:\2024 QWET Workshop\Shahe_workshop\LAKEMODEL\Default\hypsograph.dat",
                   encoding="utf-8").read()
        r = multipart("/api/preprocess/hypsograph",
                      {"center_lon": "102.7", "center_lat": "24.8"},
                      ("file", "hypsograph.dat", hyp))
        log(f"[hypsograph.dat] HTTP {r[0]} -> {json.dumps(r[1])[:320]}")
    except Exception as e:
        log(f"[hypsograph.dat] SKIP: {e}")

    # 5 ── local vendor assets (must work without CDN)
    for p in ("/static/vendor/chart.umd.min.js", "/static/vendor/plotly-2.35.2.min.js",
              "/static/vendor/leaflet.js", "/static/vendor/leaflet.css"):
        try:
            with _opener.open(urllib.request.Request(BASE + p, method="GET"), timeout=30) as resp:
                log(f"[vendor {p}] HTTP {resp.status} bytes={len(resp.read())}")
        except Exception as e:
            log(f"[vendor {p}] FAIL {e}")
    try:
        with _opener.open(urllib.request.Request(BASE + "/", method="GET"), timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")
            log(f"[index.html] HTTP {resp.status} len={len(html)} "
                f"hard_cdn={('cdn.jsdelivr.net/npm/chart' in html) or ('cdn.plotly.com' in html)} "
                f"vendor={('/static/vendor/' in html)}")
    except Exception as e:
        log(f"[index.html] FAIL {e}")


def multipart(url_path, fields, file_field):
    boundary = "----p0testboundary"
    name, fname, content = file_field
    body = io.BytesIO()
    for k, v in fields.items():
        body.write(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    body.write((f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"; "
                f"filename=\"{fname}\"\r\nContent-Type: text/plain\r\n\r\n").encode())
    body.write(content.encode("utf-8"))
    body.write(f"\r\n--{boundary}--\r\n".encode())
    r = urllib.request.Request(BASE + url_path, data=body.getvalue(),
                               headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
                               method="POST")
    try:
        with _opener.open(r, timeout=120) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8", errors="replace"))
        except Exception:
            return e.code, {"error": "unparsable"}


def main():
    proc = subprocess.Popen([PYTHON, "server.py"], cwd=APP_DIR,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        run_tests()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except Exception:
            proc.kill()
    out = r"C:\Users\dinod\Desktop\GETM-FABM-WET\3DWET\_p0_result.txt"
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
