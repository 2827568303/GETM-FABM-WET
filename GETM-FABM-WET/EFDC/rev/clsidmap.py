import re, subprocess, json, os

LOG = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\diag2_out.txt"
txt = open(LOG, encoding="utf-8", errors="replace").read()
hexes = re.findall(r"CoCreate ([0-9a-f]{32}) ", txt)
guids = set()
for h in hexes:
    # raw order: data1(4) data2(2) data3(2) data4(8) little-endian for first 3
    b = bytes.fromhex(h)
    d1 = b[0:4][::-1].hex().upper()
    d2 = b[4:6][::-1].hex().upper()
    d3 = b[6:8][::-1].hex().upper()
    d4 = b[8:16].hex().upper()
    guids.add("{%s-%s-%s-%s-%s}" % (d1, d2, d3, d4[0:4], d4[4:]))
print("distinct CLSIDs:", len(guids))


def reg(path):
    try:
        out = subprocess.run(["reg", "query", path, "/ve"], capture_output=True, text=True, encoding="mbcs")
        for line in out.stdout.splitlines():
            if "REG_SZ" in line:
                return line.split("REG_SZ", 1)[1].strip()
    except Exception:
        pass
    return None


rows = []
for g in sorted(guids):
    name = None
    for root in (r"HKCU\Software\Classes\CLSID", r"HKLM\SOFTWARE\Classes\CLSID", r"HKLM\SOFTWARE\Classes\WOW6432Node\CLSID"):
        name = reg(root + "\\" + g)
        if name:
            break
    rows.append((g, name or "?"))
for g, n in rows:
    print(g, n)
