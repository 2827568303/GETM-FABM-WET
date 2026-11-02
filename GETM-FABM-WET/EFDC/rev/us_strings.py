import struct

P = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_LIC.exe"
d = open(P, 'rb').read()

pe_off = struct.unpack_from('<I', d, 0x3C)[0]
assert d[pe_off:pe_off + 4] == b'PE\0\0'
coff = pe_off + 4
num_sections = struct.unpack_from('<H', d, coff + 2)[0]
opt_size = struct.unpack_from('<H', d, coff + 16)[0]
opt = coff + 20
magic = struct.unpack_from('<H', d, opt)[0]
is_pe32plus = magic == 0x20b
dd_off = opt + (0x70 if is_pe32plus else 0x60)
cli_rva, cli_size = struct.unpack_from('<II', d, dd_off + 14 * 8)
print('CLI dir rva', hex(cli_rva), 'size', cli_size)

sections = []
sec_off = opt + opt_size
for i in range(num_sections):
    o = sec_off + i * 40
    name = d[o:o + 8].rstrip(b'\x00').decode('latin1')
    vsize, vaddr, rsize, raddr = struct.unpack_from('<IIII', d, o + 8)
    sections.append((name, vaddr, vsize, raddr, rsize))


def rva2off(rva):
    for name, vaddr, vsize, raddr, rsize in sections:
        if vaddr <= rva < vaddr + max(vsize, rsize):
            return raddr + (rva - vaddr)
    return None


cli = rva2off(cli_rva)
md_rva, md_size = struct.unpack_from('<II', d, cli + 8)
md = rva2off(md_rva)
print('metadata at', hex(md))
sig = struct.unpack_from('<I', d, md)[0]
ver_len = struct.unpack_from('<I', d, md + 12)[0]
p = md + 16 + ver_len
p += 2  # flags
nstreams = struct.unpack_from('<H', d, p)[0]
p += 2
streams = {}
for i in range(nstreams):
    off, size = struct.unpack_from('<II', d, p)
    p += 8
    e = d.index(b'\x00', p)
    name = d[p:e].decode('latin1')
    p = e + 1
    while (p - md) % 4:
        p += 1
    streams[name] = (md + off, size)
print('streams:', {k: (hex(v[0]), v[1]) for k, v in streams.items()})

if '#US' in streams:
    base, size = streams['#US']
    i = 1
    out = []
    while i < size:
        b = d[base + i]
        if b & 0x80 == 0:
            ln = b; i += 1
        elif b & 0xC0 == 0x80:
            ln = ((b & 0x3F) << 8) | d[base + i + 1]; i += 2
        else:
            ln = ((b & 0x1F) << 24) | (d[base + i + 1] << 16) | (d[base + i + 2] << 8) | d[base + i + 3]; i += 4
        if ln == 0:
            continue
        raw = d[base + i:i + ln]
        i += ln
        try:
            s = raw.decode('utf-16le', 'ignore')
        except Exception:
            s = repr(raw)
        s = s.rstrip('\x00')
        if s:
            out.append(s)
    print('user strings:', len(out))
    for s in out:
        print('   ', repr(s))
