import os, shutil, sys

SRC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4"
DST = r"C:\EFDC84_RUN"
PRISTINE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\_backup_EFDC84_orig\EFDC_Explorer8.4.orig_20261030_135832.exe"
IMG = 0x400000

BASE_PATCHES = {
    0x81CA1F: bytes([0x90] * 5),
    0x81F784: bytes([0xEB, 0x6A]),
    0x81F80D: bytes([0xEB, 0x67]),
    0x822FF6: bytes([0x90, 0x90]),
}

os.makedirs(DST, exist_ok=True)

copied = 0
for name in os.listdir(SRC):
    p = os.path.join(SRC, name)
    if os.path.isfile(p):
        if name.lower().endswith((".exe", ".dll", ".ocx", ".config", ".tlb", ".mdb", ".csv", ".xml", ".bat", ".ini", ".log", ".txt")):
            t = os.path.join(DST, name)
            if name.lower() == "efdc_explorer8.4.exe":
                continue
            try:
                shutil.copy2(p, t)
                copied += 1
            except Exception as e:
                print("skip", name, e)
        elif name.lower().endswith(".exe"):
            pass

# 子目录也带过去（Documents/Resources/SWAN/Utilities/DSILIC0/DSILIC1）
for name in ("Documents", "Resources", "SWAN", "Utilities", "DSILIC0", "DSILIC1"):
    p = os.path.join(SRC, name)
    if os.path.isdir(p):
        try:
            shutil.copytree(p, os.path.join(DST, name), dirs_exist_ok=True)
            copied += 1
        except Exception as e:
            print("skip dir", name, e)

print("copied files:", copied)

extra = {}
if len(sys.argv) > 1:
    target = int(sys.argv[1], 16)
    extra[0x156AD58] = bytes([0x68]) + target.to_bytes(4, "little")
    print("push patch -> %08X" % target)

a = bytearray(open(PRISTINE, "rb").read())
for va, b in BASE_PATCHES.items():
    a[va - IMG: va - IMG + len(b)] = b
for va, b in extra.items():
    a[va - IMG: va - IMG + len(b)] = b
open(os.path.join(DST, "EFDC_Explorer8.4.exe"), "wb").write(bytes(a))
print("exe written to", os.path.join(DST, "EFDC_Explorer8.4.exe"))
