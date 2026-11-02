import sys, pefile
PRISTINE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\_backup_EFDC84_orig\EFDC_Explorer8.4.exe"
pe = pefile.PE(PRISTINE, fast_load=True)
IB = pe.OPTIONAL_HEADER.ImageBase
data = open(PRISTINE, 'rb').read()
secs = [(s.Name.rstrip(b'\x00').decode(), IB + s.VirtualAddress, s.Misc_VirtualSize, s.PointerToRawData, s.SizeOfRawData) for s in pe.sections]
def va2off(va):
    for (n, base, vsize, rawptr, rawsize) in secs:
        if base <= va < base + max(vsize, rawsize):
            return rawptr + (va - base)
def rd(va, n=200):
    o = va2off(va)
    if o is None: return None
    return data[o:o+n]
for a in sys.argv[1:]:
    va = int(a, 16)
    b = rd(va)
    s = b.split(b'\x00')[0]
    print('0x%X: %r' % (va, s[:160]))
