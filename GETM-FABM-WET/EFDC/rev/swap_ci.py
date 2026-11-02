import os
base = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC"
cand = [d for d in os.listdir(base) if d.startswith("EFDC ") and "8.4" in d]
p = os.path.join(base, cand[0], "EFDC_Explorer8.4.exe")
d = bytearray(open(p, "rb").read())
o = 0x156AD58 - 0x400000
print("current push:", d[o:o+5].hex())
assert d[o:o+5] == bytes.fromhex("6804524d00"), d[o:o+5].hex()
d[o:o+5] = b"\x68" + (0x4A6468).to_bytes(4, "little")
open(p, "wb").write(bytes(d))
print("patched push -> 0x4A6468:", d[o:o+5].hex())
