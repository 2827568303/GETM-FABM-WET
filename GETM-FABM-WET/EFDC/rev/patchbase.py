import os, sys, shutil, time

BASE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC"
APP = os.path.join(BASE, "EFDC 商业版8.4", "EFDC_Explorer8.4.exe")
PRISTINE = os.path.join(BASE, "_backup_EFDC84_orig", "EFDC_Explorer8.4.orig_20261030_135832.exe")
IMG = 0x400000

# 当前生效的补丁集合（相对原始 exe）
BASE_PATCHES = {
    0x81CA1F: bytes([0x90] * 5),
    0x81F784: bytes([0xEB, 0x6A]),
    0x81F80D: bytes([0xEB, 0x67]),
    0x822FF6: bytes([0x90, 0x90]),
}


def apply(extra=None, restore_call=False):
    if not os.path.exists(PRISTINE):
        raise SystemExit("pristine missing")
    a = bytearray(open(PRISTINE, "rb").read())
    for va, b in BASE_PATCHES.items():
        off = va - IMG
        a[off:off + len(b)] = b
    if extra:
        for va, b in extra.items():
            off = va - IMG
            a[off:off + len(b)] = b
    open(APP, "wb").write(bytes(a))
    print("written", len(a))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "show"
    if mode == "show":
        a = open(APP, "rb").read()
        p = open(PRISTINE, "rb").read()
        runs = []
        i = 0
        n = min(len(a), len(p))
        while i < n:
            if a[i] != p[i]:
                j = i
                while j < n and a[j] != p[j]:
                    j += 1
                runs.append((IMG + i, p[i:j].hex(" "), a[i:j].hex(" ")))
                i = j
            else:
                i += 1
        print("sizes", len(p), len(a), "diffs", len(runs))
        for va, o, c in runs:
            print("  %08X  %s -> %s" % (va, o, c))
    elif mode == "test":
        target = int(sys.argv[2], 16)
        apply(extra={0x156AD58: bytes([0x68]) + target.to_bytes(4, "little")})
        print("patched push 0x156AD58 -> %08X (0x156AD74 restored to original call)" % target)
