# -*- coding: utf-8 -*-
"""Spawn an exe under frida, load a JS probe, print its messages for N seconds.

python -X utf8 gui/frun.py <js> <exe> [seconds] [cwd]
"""
import os
import sys
import time

import frida

js_path, exe = sys.argv[1], sys.argv[2]
dur = float(sys.argv[3]) if len(sys.argv) > 3 else 15.0
cwd = sys.argv[4] if len(sys.argv) > 4 else os.path.dirname(exe)
src = open(js_path, "r", encoding="utf-8").read()

dev = frida.get_local_device()
pid = dev.spawn([exe], cwd=cwd)
print("[*] spawned pid=%d" % pid, flush=True)
sess = dev.attach(pid)


def on_msg(msg, data):
    if msg.get("type") == "send":
        print(msg["payload"], flush=True)
    else:
        print("[%s] %s" % (msg.get("type"), msg.get("description") or msg), flush=True)


script = sess.create_script(src)
script.on("message", on_msg)
script.load()
dev.resume(pid)
t0 = time.time()
while time.time() - t0 < dur:
    try:
        if not sess.is_detached:
            pass
    except Exception:
        break
    time.sleep(0.5)
print("[*] done, killing pid=%d" % pid, flush=True)
try:
    dev.kill(pid)
except Exception as e:
    print("kill: %s" % e)
