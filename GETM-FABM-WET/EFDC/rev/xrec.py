import struct, pefile
P = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\_backup_EFDC84_orig\EFDC_Explorer8.4.exe"
pe = pefile.PE(P, fast_load=True)
IB = pe.OPTIONAL_HEADER.ImageBase
data = open(P, 'rb').read()
secs = [(s.Name.rstrip(b'\x00').decode(), IB + s.VirtualAddress, s.Misc_VirtualSize, s.PointerToRawData, s.SizeOfRawData) for s in pe.sections]

def va2off(va):
    for (n, base, vsize, rawptr, rawsize) in secs:
        if base <= va < base + max(vsize, rawsize):
            return rawptr + (va - base)

def rd(va, n=16):
    o = va2off(va)
    return data[o:o+n]

def str_at(va):
    b = rd(va, 200)
    if not b:
        return None
    try:
        s = b.decode('utf-16le', 'ignore').split('\x00')[0]
        if len(s) >= 2 and all(32 <= ord(c) < 127 for c in s):
            return 'U:' + s
    except Exception:
        pass
    s = b.split(b'\x00')[0].decode('latin1', 'ignore')
    if len(s) >= 2:
        return 'A:' + s
    return None

for va in [0x4D5204, 0x461D44, 0x4DF874, 0x4DED94, 0x4E334C, 0x4E1CEC, 0x507080, 0x507D08, 0x4F43F0]:
    b = rd(va, 24)
    dw = struct.unpack('<6I', b) if b and len(b) >= 24 else None
    print('VA 0x%06X: %s  %s' % (va, b.hex() if b else None,
                                 ' '.join('0x%X' % x for x in dw) if dw else ''))
    if dw:
        for i, x in enumerate(dw):
            s = str_at(x)
            if s:
                print('      [+0x%02X] -> %s' % (i * 4, s))
