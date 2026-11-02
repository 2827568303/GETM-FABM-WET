import pefile, struct, shutil, os, sys
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

SRC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\vb6cab2\mscomctl.ocx"
DST = r"C:\EFDC84_LIC\mscomctl.ocx"

d = bytearray(open(SRC, 'rb').read())
pe = pefile.PE(data=bytes(d))
base = pe.OPTIONAL_HEADER.ImageBase
text = [s for s in pe.sections if s.Name.rstrip(b'\x00') == b'.text'][0]
tstart, tsize = text.PointerToRawData, text.Misc_VirtualSize
print('text raw', hex(tstart), 'vsize', hex(tsize), 'flags', hex(text.Characteristics))

# find zero run >= 48 inside .text virtual area
need = 48
run = 0; rs = 0; cand = None
for i in range(tstart, tstart + tsize):
    if d[i] == 0:
        if run == 0:
            rs = i
        run += 1
        if run >= need:
            cand = rs
            break
    else:
        run = 0
if cand is None:
    for i in range(tstart, tstart + tsize):
        if d[i] == 0:
            if run == 0: rs = i
            run += 1
            if run >= 16:
                cand = rs; break
        else:
            run = 0
print('cave file offset', hex(cand), 'rva', hex(text.VirtualAddress + (cand - tstart)))
cave_rva = text.VirtualAddress + (cand - tstart)

# stub: return S_OK with NULL picture, stdcall ret 0x14
stub = bytes.fromhex('8b442414' '832000' '31c0' 'c21400')
print('stub', stub.hex(), len(stub))
d[cand:cand + len(stub)] = stub

# patch call sites: call dword ptr [0x27581520]
IAT = 0x27581520
pat = bytes([0xFF, 0x15]) + struct.pack('<I', IAT)
sites = []
i = d.find(pat)
while i >= 0:
    sites.append(i)
    i = d.find(pat, i + 1)
print('sites', [hex(base + (o - 0x1000)) for o in sites])
for o in sites:
    call_va = base + (o - 0x1000)
    rel = (base + cave_rva) - (call_va + 5)
    d[o:o + 5] = b'\xe9' + struct.pack('<i', rel)
    d[o + 5] = 0x90

open(DST, 'wb').write(bytes(d))
print('wrote', DST, os.path.getsize(DST))
