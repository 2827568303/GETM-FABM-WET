import os
base = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC"
cand = [d for d in os.listdir(base) if d.startswith("EFDC ") and "8.4" in d]
p = os.path.join(base, cand[0], "EFDC_Explorer8.4.exe")
d = bytearray(open(p, "rb").read())
o = 0x822FF6 - 0x400000
print("current:", d[o:o+2].hex())
assert d[o:o+2] == bytes.fromhex("7e28"), d[o:o+2].hex()
d[o:o+2] = bytes.fromhex("9090")
open(p, "wb").write(bytes(d))
print("patched: always take 'lic file present' path")
