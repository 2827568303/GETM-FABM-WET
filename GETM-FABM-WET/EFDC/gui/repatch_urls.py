# -*- coding: utf-8 -*-
"""Point the DSI licensing assembly at the local fake server by same-length string patching.

DSILIC1.dll is a .NET assembly; its endpoint URLs are stored as UTF-16 literals.
We replace each URL with an equally long one so the metadata blob stays valid.
"""
import os
import shutil
import sys

DLL = sys.argv[1] if len(sys.argv) > 1 else r"C:\EFDC84_LIC\DSILIC1.dll"
BASE = "http://127.0.0.1:8080"

OLD = [
    "http://licensing80.ds-intl.biz/flexeraproxy.php",
    "http://licensing80.ds-intl.biz/GetTimeLocation.php",
    "http://licensing80.ds-intl.biz/",
    "licensing80.ds-intl.biz",
]

bak = DLL + ".strbak"
if not os.path.exists(bak):
    shutil.copy2(DLL, bak)
    print("backup -> %s" % bak)

data = bytearray(open(DLL, "rb").read())
count = 0
for old in OLD:
    new = BASE + old.split(".biz", 1)[1] if ".biz" in old else BASE
    # pad to the exact same character count
    if len(new) > len(old):
        continue
    new = new + " " * (len(old) - len(new))
    o = old.encode("utf-16-le")
    n = new.encode("utf-16-le")
    assert len(o) == len(n)
    start = 0
    hits = 0
    while True:
        i = data.find(o, start)
        if i < 0:
            break
        data[i:i + len(o)] = n
        start = i + len(n)
        hits += 1
    print("%-52s -> %-52s  x%d" % (old, new, hits))
    count += hits

open(DLL, "wb").write(data)
print("total replacements: %d" % count)
