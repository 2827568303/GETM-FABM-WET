import struct, pefile

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
            if o < len(DATA):
                return o
    return None


def rd(va, n):
    o = va2off(va)
    return None if o is None else DATA[o:o + n]


def dw(va):
    b = rd(va, 4)
    return None if not b or len(b) < 4 else struct.unpack("<I", b)[0]


def in_image(x):
    return x is not None and IB <= x < IB + 0x1600000


print("sections:")
for s in SECS:
    print("  %-8s base=%08X vsize=%08X raw=%08X rawsize=%08X" % (s[0], s[1], s[2], s[3], s[4]))

EP = IB + pe.OPTIONAL_HEADER.AddressOfEntryPoint
print("entrypoint VA", hex(EP), "bytes", rd(EP, 16).hex())

# entry: push VBHeader; call ThunRTMain
b = rd(EP, 16)
if b[0] == 0x68:
    VBH = struct.unpack("<I", b[1:5])[0]
    print("VBHeader =", hex(VBH))
else:
    VBH = None

def dump_hdr(vbh, count=28):
    print("--- VBHeader dwords @", hex(vbh))
    for i in range(count):
        v = dw(vbh + i * 4)
        tag = ""
        if in_image(v):
            s = rd(v, 40)
            if s:
                try:
                    t = s.decode("latin1").split("\x00")[0]
                    if t.isprintable() and len(t) > 2:
                        tag = "str:" + repr(t)
                except Exception:
                    pass
        print("  +0x%02X = %08X  %s" % (i * 4, v, tag))

if VBH:
    dump_hdr(VBH)
