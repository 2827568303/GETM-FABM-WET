import struct, pefile

PRISTINE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\_backup_EFDC84_orig\EFDC_Explorer8.4.orig_20261030_135832.exe"
pe = pefile.PE(PRISTINE)
IB = pe.OPTIONAL_HEADER.ImageBase
SECS = [(s.Name.rstrip(b"\x00").decode(), IB + s.VirtualAddress, s.Misc_VirtualSize,
         s.PointerToRawData, s.SizeOfRawData) for s in pe.sections]
DATA = open(PRISTINE, "rb").read()

iat = {}
for entry in pe.DIRECTORY_ENTRY_IMPORT:
    dll = entry.dll.decode()
    for imp in entry.imports:
        if imp.address:
            iat[imp.address] = "%s!%s" % (dll, (imp.name or b"").decode("latin1") or ("ord%d" % imp.ordinal))


def va2off(va):
    for (n, base, vsize, rawptr, rawsize) in SECS:
        if base <= va < base + max(vsize, rawsize):
            o = rawptr + (va - base)
            if 0 <= o < len(DATA):
                return o
    return None


def resolve_thunk(va):
    o = va2off(va)
    if o is None:
        return None
    b = DATA[o:o + 6]
    if len(b) == 6 and b[0] == 0xFF and b[1] == 0x25:
        slot = struct.unpack("<I", b[2:6])[0]
        return iat.get(slot) or ("slot 0x%X (unresolved)" % slot)
    return None


if __name__ == "__main__":
    import sys
    for a in sys.argv[1:]:
        va = int(a, 16)
        print("%08X -> %s" % (va, resolve_thunk(va)))
