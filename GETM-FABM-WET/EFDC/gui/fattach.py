# -*- coding: utf-8 -*-
"""Attach frida to an already running process and stream a script's messages.

python -X utf8 gui/fattach.py <js> <pid> [seconds]
"""
import sys
import time

import frida

js_path = sys.argv[1]
pid = int(sys.argv[2])
dur = float(sys.argv[3]) if len(sys.argv) > 3 else 20.0
src = open(js_path, "r", encoding="utf-8").read()

dev = frida.get_local_device()
sess = dev.attach(pid)
script = sess.create_script(src)
script.on("message", lambda m, d: print(m.get("payload") if m.get("type") == "send" else m, flush=True))
script.load()
print("[*] attached pid=%d" % pid, flush=True)
t0 = time.time()
while time.time() - t0 < dur:
    time.sleep(0.5)
try:
    sess.detach()
except Exception:
    pass
print("[*] detached", flush=True)
