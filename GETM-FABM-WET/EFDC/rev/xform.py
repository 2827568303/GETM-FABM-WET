import struct, sys, pefile
PRISTINE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\_backup_EFDC84_orig\EFDC_Explorer8.4.exe"
pe = pefile.PE(PRISTINE, fast_load=True)
IB = pe.OPTIONAL_HEADER.ImageBase
data = open(PRISTINE, 'rb').read()
secs = []
for s in pe.sections:
    secs.append((s.Name.rstrip(b'\x00').decode(), IB + s.VirtualAddress,
                 s.Misc_VirtualSize, s.PointerToRawData, s.SizeOfRawData))

def off2va(o):
    for (n, base, vsize, rawptr, rawsize) in secs:
        if rawptr <= o < rawptr + rawsize:
            return base + (o - rawptr)

def refs_of(va, limit=10):
    needle = struct.pack('<I', va)
    out = []
    j = 0
    while True:
        k = data.find(needle, j)
        if k < 0:
            break
        j = k + 1
        out.append(k)
        if len(out) >= limit:
            break
    return out

names = sys.argv[1:] or ['frmEFDC_Explorer', 'frmEFDC_Explorer_TitleForm', 'frmActivation']
for nm in names:
    pat = nm.encode() + b'\x00'
    i = data.find(pat)
    if i < 0:
        print(nm, 'NOT FOUND')
        continue
    va = off2va(i)
    print('=== %s : file 0x%X va 0x%X ===' % (nm, i, va))
    rs = refs_of(va, 8)
    lbl = []
    for x in rs:
        v = off2va(x)
        lbl.append('%s(va %s)' % (hex(x), hex(v) if v else '?'))
    print('  refs: ' + ' '.join(lbl))
    for h in rs[:5]:
        print('   ctx: %s' % data[h - 0x18:h + 0x14].hex())
