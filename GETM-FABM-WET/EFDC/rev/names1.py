import struct, pefile, re, sys

PRISTINE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\_backup_EFDC84_orig\EFDC_Explorer8.4.orig_20261030_135832.exe"
pe = pefile.PE(PRISTINE, fast_load=True)
IB = pe.OPTIONAL_HEADER.ImageBase
SECS = [(s.Name.rstrip(b"\x00").decode(), IB + s.VirtualAddress, s.Misc_VirtualSize,
         s.PointerToRawData, s.SizeOfRawData) for s in pe.sections]
DATA = open(PRISTINE, "rb").read()


def va2off(va):
    for (n, base, vsize, rawptr, rawsize) in SECS:
        if base <= va < base + max(vsize, rawsize):
            o = rawptr + (va - base)
            if 0 <= o < len(DATA):
                return o
    return None


def off2va(off):
    for (n, base, vsize, rawptr, rawsize) in SECS:
        if rawptr <= off < rawptr + rawsize:
            return base + (off - rawptr)
    return None


def rd(va, n):
    o = va2off(va)
    return None if o is None else DATA[o:o + n]


# --- find form-name strings ---
names = set()
for m in re.finditer(rb"frm[A-Za-z0-9_]{2,30}", DATA):
    s = m.group().decode()
    names.add(s)
print("distinct frm* strings:", len(names))
print(sorted(names)[:80])
