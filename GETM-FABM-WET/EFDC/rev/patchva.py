# -*- coding: utf-8 -*-
"""Patch PE bytes by virtual address (VA) instead of file offset.

python -X utf8 rev/patchva.py <exe> <VA>=<hexbytes> [<VA>=<hexbytes> ...]
"""
import sys

import pefile

exe = sys.argv[1]
pe = pefile.PE(exe, fast_load=True)
ib = pe.OPTIONAL_HEADER.ImageBase
secs = [(ib + s.VirtualAddress, ib + s.VirtualAddress + s.Misc_VirtualSize,
         s.PointerToRawData, s.Name.rstrip(b"\x00").decode()) for s in pe.sections]


def va2off(va):
    for lo, hi, praw, name in secs:
        if lo <= va < hi:
            return praw + (va - lo), name
    raise SystemExit("VA %08X not inside a section" % va)


with open(exe, "r+b") as f:
    for spec in sys.argv[2:]:
        vhex, bhex = spec.split("=")
        va = int(vhex, 16)
        data = bytes.fromhex(bhex)
        off, name = va2off(va)
        f.seek(off)
        old = f.read(len(data))
        f.seek(off)
        f.write(data)
        print("VA %08X (%s off 0x%X): %s -> %s" % (va, name, off, old.hex(), data.hex()))
print("done")
