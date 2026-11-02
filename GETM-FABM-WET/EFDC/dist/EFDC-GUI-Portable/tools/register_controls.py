# -*- coding: utf-8 -*-
"""Register every ActiveX control in a folder for the CURRENT USER (no admin needed).

Usage:  python register_controls.py [folder-with-ocx]
Works on any 64-bit Windows that has the 32-bit PowerShell
(%WINDIR%\\SysWOW64\\WindowsPowerShell\\v1.0\\powershell.exe).
"""
import glob
import os
import subprocess
import sys
import winreg

HERE = os.path.dirname(os.path.abspath(__file__))
PS32 = os.path.join(os.environ.get("WINDIR", r"C:\Windows"),
                    "SysWOW64", "WindowsPowerShell", "v1.0", "powershell.exe")
DUMP = os.path.join(HERE, "tlb_dump.ps1")
FOLDER = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(HERE, "..", "vb6")

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


TMP = os.path.join(HERE, "tmp")
os.makedirs(TMP, exist_ok=True)
ENV = os.environ.copy()
ENV["TEMP"] = TMP
ENV["TMP"] = TMP


def dump(path):
    cp = subprocess.run([PS32, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", DUMP, "-Path", path],
                        capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
    out = (cp.stdout or "") + (cp.stderr or "")
    lib = None
    libname = None
    classes = []
    for line in out.splitlines():
        p = line.strip().split("|")
        if len(p) >= 4 and p[0] == "LIB":
            lib = (p[1].strip("{}").upper(), p[2])
            libname = p[3].strip()
        elif len(p) >= 3 and p[0] == "TKIND_COCLASS":
            classes.append((p[2], p[1].strip("{}").upper()))
    return lib, libname, classes


if not os.path.isfile(PS32):
    print("!! 32-bit PowerShell not found: %s" % PS32)
    sys.exit(1)

files = sorted(set(glob.glob(os.path.join(FOLDER, "*.ocx")) + glob.glob(os.path.join(FOLDER, "*.OCX"))))
print("folder: %s" % FOLDER)
print("controls: %d" % len(files))

total = 0
failed = []
for path in files:
    lib, libname, classes = dump(path)
    if not lib or not classes:
        failed.append(os.path.basename(path))
        continue
    libguid, libver = lib
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
    print("  ok %-16s %2d classes (%s)" % (os.path.basename(path), len(classes), libname))

print("class entries written: %d" % total)
if failed:
    print("skipped (no readable typelib): %s" % ", ".join(failed))
