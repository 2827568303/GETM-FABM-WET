# -*- coding: utf-8 -*-
"""Point the GUI at the bundled EFDC+ solver so "Run" works out of the box.

Writes EFDCPath0 in %PUBLIC%\\DSI\\EEMS8.4\\EFDC_Explorer.ini when it is empty
(or when the stored file no longer exists).

python -X utf8 seed_solver.py "<app dir>"
"""
import os
import sys

PUBLIC = os.environ.get("PUBLIC") or r"C:\Users\Public"
INI = os.path.join(PUBLIC, "DSI", "EEMS8.4", "EFDC_Explorer.ini")

APP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.environ.get("LOCALAPPDATA", ""), "EFDC84", "app")

CANDIDATES = [
    "EFDCPlus_084_OMP.exe",
    "EFDCPlus_084_OMP_180718.PERPETUAL.exe",
    "EFDCPlus_084_OMP_180718.exe",
]


def pick_solver():
    for name in CANDIDATES:
        p = os.path.join(APP, name)
        if os.path.isfile(p):
            return p
    return ""


def main():
    solver = pick_solver()
    if not solver:
        print("solver not found in %s" % APP)
        return 0
    os.makedirs(os.path.dirname(INI), exist_ok=True)
    text = ""
    if os.path.isfile(INI):
        try:
            text = open(INI, "rb").read().decode("latin-1")
        except Exception:
            text = ""

    lines = text.splitlines()
    cur = ""
    for ln in lines:
        if ln.startswith("EFDCPath0="):
            cur = ln.split("=", 1)[1].strip()
    if cur and os.path.isfile(cur):
        print("solver already set: %s" % cur)
        return 0

    out, done = [], False
    for ln in lines:
        if ln.startswith("EFDCPath0="):
            out.append("EFDCPath0=%s" % solver)
            done = True
        else:
            out.append(ln)
    if not done:
        out.append("EFDCPath0=%s" % solver)

    data = "\r\n".join(out).rstrip() + "\r\n"
    try:
        open(INI, "wb").write(data.encode("latin-1"))
        print("solver set: %s" % solver)
    except PermissionError:
        print("solver seed skipped: ini locked by a running EFDC")
    except Exception as e:
        print("solver seed skipped: %s" % e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
