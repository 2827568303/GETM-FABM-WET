import os
base = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC"
cand = [d for d in os.listdir(base) if d.startswith("EFDC ") and "8.4" in d]
p = os.path.join(base, cand[0], "EFDC_Explorer8.4.exe")
d = bytearray(open(p, "rb").read())
o = 0x156AD74 - 0x400000
print("current:", d[o:o+6].hex())
assert d[o:o+6] == bytes.fromhex("ff9050020000"), d[o:o+6].hex()
d[o:o+6] = bytes.fromhex("31c0668945c4")
open(p, "wb").write(bytes(d))
print("patched: skip call [eax+0x250]")
