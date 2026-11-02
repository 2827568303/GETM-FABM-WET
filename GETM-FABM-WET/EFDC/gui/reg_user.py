# -*- coding: utf-8 -*-
"""Register an OCX per-user by overriding HKCR inside regsvr32.

python -X utf8 gui/reg_user.py <path-to-ocx>
"""
import os, sys, time
import frida

HERE = os.path.dirname(os.path.abspath(__file__))
target = os.path.abspath(sys.argv[1])
js = open(os.path.join(HERE, "regoverride.js"), encoding="utf-8").read()

pid = frida.spawn([r"C:\Windows\SysWOW64\regsvr32.exe", "/s", target])
sess = frida.attach(pid)
sc = sess.create_script(js)


def on_msg(m, d):
    p = m.get("payload")
    if p is not None:
        print("  js:", p, flush=True)
    else:
        print("  js-err:", m.get("description"), flush=True)


sc.on("message", on_msg)
sc.load()
frida.resume(pid)
t0 = time.time()
while time.time() - t0 < 20:
    time.sleep(0.2)
    try:
        frida.attach(pid).detach()
    except Exception:
        print("regsvr32 exited after %.2fs" % (time.time() - t0), flush=True)
        break
