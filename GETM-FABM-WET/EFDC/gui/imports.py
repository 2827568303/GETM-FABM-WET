# -*- coding: utf-8 -*-
"""Minimal PE import table dumper (32-bit, enough for VB6 exes)."""
import struct, sys


def rva2off(secs, rva):
    for (name, va, vs, off, rs) in secs:
        if va <= rva < va + max(vs, rs):
            return off + (rva - va)
    return None


def dump(path):
    d = open(path, 'rb').read()
    e = struct.unpack_from('<I', d, 0x3C)[0]
    fh = e + 4
    machine, nsec, tds, psym, nsym, optsz, chars = struct.unpack_from('<HHIIIHH', d, fh)
    opt = fh + 20
    ib = struct.unpack_from('<I', d, opt + 0x1C)[0]
    so = opt + optsz
    secs = []
    for i in range(nsec):
        name = d[so+i*40:so+i*40+8].rstrip(b'\0').decode('latin1')
        vsize, vaddr, rsize, raddr = struct.unpack_from('<IIII', d, so+i*40+8)
        secs.append((name, vaddr, vsize, raddr, rsize))
    # data dirs: import at offset 0x80 (8 bytes each), import = index 1
    imp_rva, imp_sz = struct.unpack_from('<II', d, opt + 0x80 + 1 * 8)
    print("%s  imports rva=0x%x size=0x%x" % (path, imp_rva, imp_sz))
    off = rva2off(secs, imp_rva)
    if off is None:
        print("  (no import table)")
        return
    i = 0
    while True:
        ent = off + i * 20
        ilt, ts, fc, nameRva, iat = struct.unpack_from('<IIIII', d, ent)
        if ilt == 0 and nameRva == 0 and iat == 0:
            break
        noff = rva2off(secs, nameRva)
        dll = d[noff:d.index(b'\0', noff)].decode('latin1')
        funcs = []
        t = rva2off(secs, ilt or iat)
        k = 0
        while t is not None:
            v = struct.unpack_from('<I', d, t + k * 4)[0]
            if v == 0:
                break
            if v & 0x80000000:
                funcs.append('#%d' % (v & 0xffff))
            else:
                fo = rva2off(secs, v)
                if fo is None:
                    break
                s = d[fo+2:d.index(b'\0', fo)]
                funcs.append(s.decode('latin1'))
            k += 1
        print("  %-22s %3d  %s" % (dll, len(funcs), ', '.join(funcs[:14]) + (' ...' if len(funcs) > 14 else '')))
        i += 1


for p in sys.argv[1:]:
    dump(p)
