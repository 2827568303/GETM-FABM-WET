# -*- coding: utf-8 -*-
"""Apply a regasm-generated .reg into HKCU\\Software\\Classes (per-user, no admin).

python -X utf8 gui/apply_reg.py <regfile> [--codebase <dll-path>]
"""
import os
import sys
import winreg

regfile = sys.argv[1]
codebase = None
if "--codebase" in sys.argv:
    codebase = os.path.abspath(sys.argv[sys.argv.index("--codebase") + 1])
    codebase_url = "file:///" + codebase.replace("\\", "/")

root_map = {
    "HKEY_CLASSES_ROOT": (winreg.HKEY_CURRENT_USER, "Software\\Classes\\"),
    "HKEY_LOCAL_MACHINE": (winreg.HKEY_CURRENT_USER, "Software\\Classes\\"),
    "HKEY_CURRENT_USER": (winreg.HKEY_CURRENT_USER, ""),
}

cur = None
count = 0
for raw in open(regfile, encoding="utf-8-sig", errors="replace"):
    line = raw.rstrip("\r\n")
    if not line or line.startswith(";"):
        continue
    if line.startswith("[") and line.endswith("]"):
        path = line[1:-1]
        hive, _, rest = path.partition("\\")
        base, prefix = root_map.get(hive.upper(), (winreg.HKEY_CURRENT_USER, "Software\\Classes\\"))
        full = prefix + rest
        cur = (base, full)
        winreg.CreateKeyEx(base, full, 0, winreg.KEY_WRITE).Close()
        count += 1
        continue
    if cur is None:
        continue
    if "=" not in line:
        continue
    name, _, value = line.partition("=")
    name = name.strip()
    value = value.strip().strip('"')
    name = "" if name == "@" else name.strip('"')
    k = winreg.CreateKeyEx(cur[0], cur[1], 0, winreg.KEY_WRITE)
    winreg.SetValueEx(k, name, 0, winreg.REG_SZ, value)
    k.Close()

if codebase:
    for clsid in ("{6399E2C8-63E4-4F31-823C-D256C17E7A13}", "{330D13A9-B2BE-4CCF-9B8A-DC2047FB3D33}"):
        for sub in ("", "\\0.0.0.0"):
            p = "Software\\Classes\\CLSID\\%s\\InprocServer32%s" % (clsid, sub)
            k = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, p, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(k, "CodeBase", 0, winreg.REG_SZ, codebase_url)
            k.Close()
    print("codebase -> %s" % codebase_url)
print("keys created/updated: %d" % count)
