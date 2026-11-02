import os, sys, glob

ROOT = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4"
needles = ["eems-analytics", "eems-analytics.info", "wp-json", "licensing80", "flexeraproxy"]

hits = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    for fn in filenames:
        p = os.path.join(dirpath, fn)
        try:
            if os.path.getsize(p) > 200 * 1024 * 1024:
                continue
            b = open(p, "rb").read()
        except Exception:
            continue
        found = []
        for n in needles:
            if n.encode("ascii") in b or n.encode("utf-16-le") in b:
                found.append(n)
        if found:
            hits.append((p, os.path.getsize(p), found))

for p, sz, f in hits:
    print(sz, f, p)

print("--- also scan C:\\EFDC84_LIC ---")
for dirpath, dirnames, filenames in os.walk(r"C:\EFDC84_LIC"):
    for fn in filenames:
        p = os.path.join(dirpath, fn)
        try:
            b = open(p, "rb").read()
        except Exception:
            continue
        found = [n for n in needles if n.encode("ascii") in b or n.encode("utf-16-le") in b]
        if found:
            print(os.path.getsize(p), found, p)
