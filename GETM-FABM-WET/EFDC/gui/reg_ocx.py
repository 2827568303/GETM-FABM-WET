# -*- coding: utf-8 -*-
"""Register any 32-bit ActiveX control per-user (HKCU), by reading its typelib.

python -X utf8 gui/reg_ocx.py <ocx1> [ocx2 ...]
"""
import os
import subprocess
import sys
import winreg

HERE = os.path.dirname(os.path.abspath(__file__))
PS32 = os.path.join(os.environ["WINDIR"], "SysWOW64", "WindowsPowerShell", "v1.0", "powershell.exe")
DUMP = os.path.join(HERE, "tlb_dump.ps1")

ROOTS = ["Software\\Classes\\", "Software\\Classes\\WOW6432Node\\"]


def sv(base, name, value):
    k = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, base, 0, winreg.KEY_WRITE)
    winreg.SetValueEx(k, name, 0, winreg.REG_SZ, value)
    winreg.CloseKey(k)


def dword(base, name, value):
    k = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, base, 0, winreg.KEY_WRITE)
    winreg.SetValueEx(k, name, 0, winreg.REG_DWORD, value)
    winreg.CloseKey(k)


def empty(base):
    k = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, base, 0, winreg.KEY_WRITE)
    winreg.CloseKey(k)


def dump(path):
    cp = subprocess.run([PS32, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", DUMP, "-Path", path],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = (cp.stdout or "") + (cp.stderr or "")
    lib = None
    classes = []
    for line in out.splitlines():
        p = line.strip().split("|")
        if len(p) >= 4 and p[0] == "LIB":
            lib = (p[1].strip("{}").upper(), p[2])
        elif len(p) >= 3 and p[0] == "TKIND_COCLASS":
            classes.append((p[2], p[1].strip("{}").upper()))
    return lib, classes


total = 0
for path in sys.argv[1:]:
    path = os.path.abspath(path)
    lib, classes = dump(path)
    if not lib or not classes:
        print("!! %s : typelib dump failed (lib=%s classes=%d)" % (path, lib, len(classes)))
        continue
    libguid, libver = lib
    libname = None
    for line in subprocess.run([PS32, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", DUMP, "-Path", path],
                               capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.splitlines():
        if line.startswith("LIB|"):
            libname = line.split("|")[3].strip()
    print("%s : lib %s v%s (%s), %d classes" % (os.path.basename(path), libguid, libver, libname, len(classes)))
    for root in ROOTS:
        tl = root + "TypeLib\\{%s}\\%s" % (libguid, libver)
        sv(tl + "\\0\\win32", "", path)
        sv(tl + "\\HELPDIR", "", os.path.dirname(path))
        dword(tl, "FLAGS", 2)
        for name, clsid in classes:
            progid = "%s.%s" % (libname, name)
            base = root + "CLSID\\{%s}" % clsid
            sv(base, "", progid)
            sv(base + "\\InprocServer32", "", path)
            sv(base + "\\InprocServer32", "ThreadingModel", "Apartment")
            sv(base + "\\TypeLib", "", "{%s}" % libguid)
            sv(base + "\\TypeLib", "Version", libver)
            sv(base + "\\Version", "", libver)
            sv(base + "\\ProgID", "", progid)
            empty(base + "\\Control")
            sv(root + progid + "\\CLSID", "", "{%s}" % clsid)
            total += 1
            print("   + %-14s %s  ->  %s" % (name, clsid, progid))
print("total class entries written: %d" % total)
