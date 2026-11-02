import os
base = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC"
cand = [d for d in os.listdir(base) if d.startswith("EFDC ") and "8.4" in d]
p = os.path.join(base, cand[0], "EFDC_Explorer8.4.exe")
print("path:", p)
print("exists:", os.path.exists(p))
d = bytearray(open(p, "rb").read())
o = 0x81F80D - 0x400000
print("current:", d[o:o+2].hex())
if d[o:o+2] == bytes.fromhex("7567"):
    d[o:o+2] = bytes.fromhex("eb67")
    open(p, "wb").write(bytes(d))
    print("patched ->", bytes(d[o:o+2]).hex())
else:
    print("already patched")
