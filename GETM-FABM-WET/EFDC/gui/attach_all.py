# -*- coding: utf-8 -*-
"""Attach to the app and to any child processes it spawns, run a JS probe on each.

python -X utf8 gui/attach_all.py <exe> <seconds> <js>
"""
import ctypes
import ctypes.wintypes as wt
import os
import subprocess
import sys
import time

import frida

HERE = os.path.dirname(os.path.abspath(__file__))
exe = sys.argv[1]
dur = float(sys.argv[2]) if len(sys.argv) > 2 else 12.0
jsfile = sys.argv[3] if len(sys.argv) > 3 else "clsid_log.js"
js = open(jsfile if os.path.isabs(jsfile) else os.path.join(HERE, os.path.basename(jsfile)), encoding="utf-8").read()

k32 = ctypes.WinDLL("kernel32", use_last_error=True)


class PE32W(ctypes.Structure):
    _fields_ = [("dwSize", wt.DWORD), ("cntUsage", wt.DWORD), ("th32ProcessID", wt.DWORD),
                ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)), ("th32ModuleID", wt.DWORD),
                ("cntThreads", wt.DWORD), ("th32ParentProcessID", wt.DWORD),
                ("pcPriClassBase", ctypes.c_long), ("dwFlags", wt.DWORD),
                ("szExeFile", ctypes.c_wchar * 260)]


def children(pid):
    out = []
    snap = k32.CreateToolhelp32Snapshot(2, 0)
    e = PE32W(); e.dwSize = ctypes.sizeof(e)
    ok = k32.Process32FirstW(snap, ctypes.byref(e))
    while ok:
        if e.th32ParentProcessID == pid:
            out.append((e.th32ProcessID, e.szExeFile))
        ok = k32.Process32NextW(snap, ctypes.byref(e))
    k32.CloseHandle(snap)
    return out


p = subprocess.Popen([exe], cwd=os.path.dirname(exe), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
attached = {}
t0 = time.time()


def attach(pid, label):
    if pid in attached:
        return
    try:
        sess = frida.attach(pid)
        sc = sess.create_script(js)

        def on_msg(m, d, label=label):
            payload = m.get("payload")
            if isinstance(payload, dict):
                payload["pid"] = label
                print(payload, flush=True)
            elif m.get("type") == "error":
                print("  err[%s]: %s" % (label, m.get("description")), flush=True)

        sc.on("message", on_msg)
        sc.load()
        attached[pid] = sess
        print("attached %s pid=%d" % (label, pid), flush=True)
    except Exception as e:
        print("attach fail %s: %s" % (label, e), flush=True)


time.sleep(0.4)
attach(p.pid, "parent")
while time.time() - t0 < dur:
    for cpid, name in children(p.pid):
        attach(cpid, "child:" + name)
    if p.poll() is not None:
        print("parent exited code=%s" % p.returncode, flush=True)
        break
    time.sleep(0.25)
print("done", flush=True)
for sess in attached.values():
    try:
        sess.detach()
    except Exception:
        pass
try:
    os.kill(p.pid, 9)
except Exception:
    pass

