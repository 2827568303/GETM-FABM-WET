import os, shutil, time, sys
BASE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC"
EXE = os.path.join(BASE, "EFDC 商业版8.4", "EFDC_Explorer8.4.exe")
BK  = os.path.join(BASE, "_backup_EFDC84_orig")
os.makedirs(BK, exist_ok=True)
stamp = time.strftime("%Y%m%d_%H%M%S")
b = bytearray(open(EXE,'rb').read())
P = {0x81CA1F: bytes([0x90]*5),          # skip FNO check call
     0x81F784: bytes([0xEB,0x6A]),       # skip feature mapping check
     0x81F80D: bytes([0xEB,0x67]),       # skip hostID check
     0x822FF6: bytes([0x90,0x90]),       # skip Missing .lic file
     0x156AD74: bytes([0x31,0xC0,0x66,0x89,0x45,0xC4])}  # skip form method 0x250
shutil.copy2(EXE, os.path.join(BK, f"EFDC_Explorer8.4.orig_{stamp}.exe"))
for va, nb in P.items():
    off = va - 0x400000
    cur = bytes(b[off:off+len(nb)])
    print(f"{va:#x}: {cur.hex(' ')} -> {nb.hex(' ')}")
    b[off:off+len(nb)] = nb
open(EXE,'wb').write(b)
print("patched OK, backup:", stamp)
