import pefile, struct, os, sys
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

SRC = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\vb6rt\sys\MSCOMCTL.OCX"
DST = r"C:\EFDC84_LIC\vb6\MSCOMCTL.OCX"

d = bytearray(open(SRC, 'rb').read())
pe = pefile.PE(data=bytes(d))
base = pe.OPTIONAL_HEADER.ImageBase
text = [s for s in pe.sections if s.Name.rstrip(b'\x00') == b'.text'][0]


def rva2off(rva):
    for s in pe.sections:
        if s.VirtualAddress <= rva < s.VirtualAddress + s.SizeOfRawData:
            return s.PointerToRawData + (rva - s.VirtualAddress)
    return None


# --- license patches ---
o = rva2off(0x81324)
assert d[o:o + 5] == bytes.fromhex('a150e06227'), d[o:o + 5].hex()
d[o:o + 5] = bytes.fromhex('b801000000')
o = rva2off(0x45400)
assert d[o:o + 6] == bytes.fromhex('0f844cd50000'), d[o:o + 6].hex()
d[o:o + 6] = bytes.fromhex('e94cd5000090')
print('license checks patched')

# --- picture-load fallback inside the OCX ---
iat = None
for e in pe.DIRECTORY_ENTRY_IMPORT:
    for imp in e.imports:
        n = (imp.name or b'').decode(errors='ignore')
        if n == 'OleLoadPicture':
            iat = imp.address
print('OleLoadPicture IAT', hex(iat) if iat else None)

if iat:
    # cave: zero run inside .text
    need = 48
    run = 0; rs = 0; cand = None
    tstart = text.PointerToRawData
    tend = tstart + min(text.Misc_VirtualSize, text.SizeOfRawData)
    for i in range(tstart, tend):
        if d[i] == 0:
            if run == 0: rs = i
            run += 1
            if run >= need:
                cand = rs; break
        else:
            run = 0
    if cand is None:
        for i in range(tstart, tend):
            if d[i] == 0:
                if run == 0: rs = i
                run += 1
                if run >= 16:
                    cand = rs; break
            else:
                run = 0
    cave_rva = text.VirtualAddress + (cand - tstart)
    stub = bytes.fromhex('8b442414' '832000' '31c0' 'c21400')
    d[cand:cand + len(stub)] = stub
    print('cave rva', hex(cave_rva), 'stub', stub.hex())
    pat = bytes([0xFF, 0x15]) + struct.pack('<I', iat)
    sites = []
    i = d.find(pat)
    while i >= 0:
        sites.append(i); i = d.find(pat, i + 1)
    print('sites', [hex(base + (s - text.PointerToRawData) + text.VirtualAddress) for s in sites])
    for s in sites:
        call_rva = text.VirtualAddress + (s - tstart)
        rel = (base + cave_rva) - (base + call_rva + 5)
        d[s:s + 5] = b'\xe9' + struct.pack('<i', rel)
        d[s + 5] = 0x90

open(DST, 'wb').write(bytes(d))
print('wrote', DST, os.path.getsize(DST))
