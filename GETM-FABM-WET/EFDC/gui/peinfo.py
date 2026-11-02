# -*- coding: utf-8 -*-
import struct, sys

def info(p):
    d = open(p, 'rb').read()
    e = struct.unpack_from('<I', d, 0x3C)[0]
    assert d[e:e+4] == b'PE\0\0', 'not PE'
    fh = e + 4
    machine, nsec, tds, psym, nsym, optsz, chars = struct.unpack_from('<HHIIIHH', d, fh)
    opt = fh + 20
    magic = struct.unpack_from('<H', d, opt)[0]
    dllchar = struct.unpack_from('<H', d, opt + 0x46)[0]
    ep = struct.unpack_from('<I', d, opt + 0x10)[0]
    ib = struct.unpack_from('<I', d, opt + 0x1C)[0]
    print(p)
    print("  machine=%04x nsec=%d optsz=%d filechars=%04x magic=%04x DllChar=%04x NXCOMPAT=%s DYNAMICBASE=%s EP=RVA %x ImageBase=%x" % (
        machine, nsec, optsz, chars, magic, dllchar, bool(dllchar & 0x100), bool(dllchar & 0x40), ep, ib))
    print("  raw size=%d  (%.1f MB)" % (len(d), len(d)/1048576.0))
    so = opt + optsz
    for i in range(nsec):
        name = d[so+i*40:so+i*40+8].rstrip(b'\0').decode('latin1')
        vsize, vaddr, rsize, raddr, _, _, _, _, sc = struct.unpack_from('<IIIIIIHHI', d, so+i*40+8)
        print("    %-9s VA=%08x VS=%08x OFF=%08x RS=%08x ch=%08x" % (name, vaddr, vsize, raddr, rsize, sc))
    # where does RVA 0x3ac2b1 fall?
    for i in range(nsec):
        name = d[so+i*40:so+i*40+8].rstrip(b'\0').decode('latin1')
        vsize, vaddr, rsize, raddr, *_ = struct.unpack_from('<IIIIIIHHI', d, so+i*40+8)
        for rva in (0x3ac2b1, 0x2bd255, 0x42a8a3, 0x250056):
            if vaddr <= rva < vaddr + max(vsize, rsize):
                print("    RVA %08x -> %s (file off %08x)" % (rva, name, raddr + (rva - vaddr)))

for p in sys.argv[1:]:
    info(p)
