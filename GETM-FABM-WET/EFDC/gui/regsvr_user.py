# -*- coding: utf-8 -*-
"""Register an OCX per-user: run regsvr32 under frida with HKCR->HKCU redirection.

python -X utf8 gui/regsvr_user.py <path-to-ocx-or-dll>
"""
import os, sys, time
import frida

HERE = os.path.dirname(os.path.abspath(__file__))
target = os.path.abspath(sys.argv[1])
js = open(os.path.join(HERE, "regredir.js"), encoding="utf-8").read()

regsvr = r"C:\Windows\SysWOW64\regsvr32.exe"
pid = frida.spawn([regsvr, "/s", target])
sess = frida.attach(pid)
sc = sess.create_script(js)
log = []


def on_msg(m, d):
    p = m.get("payload")
    if isinstance(p, dict) and "reg" in p:
        log.append(p["reg"])
        return
    if isinstance(p, dict) and "note" in p:
        print("  note:", p["note"], flush=True)
        return
    if m.get("type") == "error":
        print("  js error:", m.get("description"), flush=True)


sc.on("message", on_msg)
sc.load()
frida.resume(pid)
t0 = time.time()
while time.time() - t0 < 25:
    time.sleep(0.2)
    try:
        os.kill(pid, 0)
    except Exception:
        break
print("registered keys written: %d" % len(log))
for k in log[:12]:
    print("   ", k)
