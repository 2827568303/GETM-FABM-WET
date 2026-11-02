# -*- coding: utf-8 -*-
"""Point EFDC Explorer's file dialog (InitDir) and last project (Proj1) at a model folder.

python -X utf8 set_lastmodel.py "<model dir>"
"""
import os
import sys

PUBLIC = os.environ.get("PUBLIC") or r"C:\Users\Public"
INI = os.path.join(PUBLIC, "DSI", "EEMS8.4", "EFDC_Explorer.ini")

model = sys.argv[1]
model = os.path.abspath(model)

text = ""
if os.path.isfile(INI):
    text = open(INI, "rb").read().decode("mbcs", errors="replace")

out, done = [], set()
for ln in text.splitlines():
    if ln.startswith("InitDir="):
        out.append("InitDir=" + model)
        done.add("init")
        continue
    if ln.startswith("Proj1="):
        out.append("Proj1=" + model + "\\")
        done.add("proj")
        continue
    out.append(ln)
if "init" not in done:
    out.append("InitDir=" + model)
if "proj" not in done:
    out.append("Proj1=" + model + "\\")

data = "\r\n".join(out).rstrip() + "\r\n"
open(INI, "wb").write(data.encode("mbcs", errors="replace"))
print("InitDir=%s" % model)
print("Proj1=%s\\" % model)
