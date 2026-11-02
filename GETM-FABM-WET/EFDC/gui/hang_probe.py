# -*- coding: utf-8 -*-
"""Attach with frida (read-only stack dump) + track child processes.

python -X utf8 gui/hang_probe.py <exe> <seconds> [js]
"""
import ctypes, ctypes.wintypes as wt, json, os, subprocess, sys, time
import frida

HERE = os.path.dirname(os.path.abspath(__file__))
exe = sys.argv[1]
dur = float(sys.argv[2]) if len(sys.argv) > 2 else 12.0
jsf = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, "dump_stacks.js")

k32 = ctypes.WinDLL("kernel32", use_last_error=True)


class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [("dwSize", wt.DWORD), ("cntUsage", wt.DWORD), ("th32ProcessID", wt.DWORD),
                ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)), ("th32ModuleID", wt.DWORD),
                ("cntThreads", wt.DWORD), ("th32ParentProcessID", wt.DWORD),
                ("pcPriClassBase", ctypes.c_long), ("dwFlags", wt.DWORD),
                ("szExeFile", ctypes.c_wchar * 260)]


def children(pid):
    out = []
    snap = k32.CreateToolhelp32Snapshot(2, 0)
    if snap == -1:
        return out
    e = PROCESSENTRY32W(); e.dwSize = ctypes.sizeof(e)
    ok = k32.Process32FirstW(snap, ctypes.byref(e))
    while ok:
        if e.th32ParentProcessID == pid:
            out.append((e.th32ProcessID, e.szExeFile))
        ok = k32.Process32NextW(snap, ctypes.byref(e))
    k32.CloseHandle(snap)
    return out


pid = frida.spawn(exe, cwd=os.path.dirname(exe))
sess = frida.attach(pid)
sc = sess.create_script(open(jsf, encoding="utf-8").read())
state = {"spin": 0}


def on_msg(m, d):
    p = m.get("payload")
    if isinstance(p, dict):
        if "tag" in p and "threads" in p:
            print("\n=== %s : %d threads, %d modules ===" % (p["tag"], p["threads"], p["modules"]), flush=True)
        elif "scan" in p:
            if p.get("state") == "running" and not p.get("bt") and not p.get("scan"):
                return
            print("  tid=%d %-8s eip=%s (%s) %s" % (p["tid"], p.get("state"),
                  p.get("eip"), p.get("eip_where") or "?", p.get("name") or ""), flush=True)
            for i, a in enumerate(p.get("bt") or []):
                print("      bt[%d] %s" % (i, a), flush=True)
            if p.get("scan"):
                print("      stack-scan(%d): %s" % (len(p["scan"]), ", ".join(p["scan"][:30])), flush=True)
            if p.get("err"):
                print("      err %s" % p["err"], flush=True)
        else:
            print("[js] %s" % json.dumps(p, ensure_ascii=False), flush=True)
    else:
        print("[js-raw] %r %r" % (m, d), flush=True)


sc.on("message", on_msg)
sc.load()
frida.resume(pid)
print("pid=%d" % pid, flush=True)
t0 = time.time()
seen = set()
while time.time() - t0 < dur:
    for cp, name in children(pid):
        if cp not in seen:
            seen.add(cp)
            print("[%5.2f] CHILD pid=%d %s" % (time.time() - t0, cp, name), flush=True)
    time.sleep(0.3)
print("done", flush=True)
try:
    os.kill(pid, 9)
except Exception:
    pass
