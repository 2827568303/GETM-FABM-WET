# -*- coding: utf-8 -*-
"""Inventory every access to the license-restriction word at 0x16204A0.

Prints: section, write sites (mov [global], imm / reg), read+compare sites with the
following conditional jump, so a patch set can be derived.

python -X utf8 rev/licscan.py <exe>
"""
import struct
import sys

import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

EXE = sys.argv[1]
G = 0x16204A0
pe = pefile.PE(EXE, fast_load=True)
IB = pe.OPTIONAL_HEADER.ImageBase
data = open(EXE, "rb").read()
md = Cs(CS_ARCH_X86, CS_MODE_32)

secs = []
for s in pe.sections:
    secs.append((s.Name.rstrip(b"\x00").decode(), IB + s.VirtualAddress,
                 IB + s.VirtualAddress + s.Misc_VirtualSize,
                 s.PointerToRawData, s.Characteristics))

for name, lo, hi, praw, ch in secs:
    if lo <= G < hi:
        print("global 0x%X lives in %s (writable=%s) file_off=0x%X" %
              (G, name, bool(ch & 0x80000000), praw + (G - lo)))
        off = praw + (G - lo)
        print("current bytes:", data[off:off + 8].hex())
        break

pat = struct.pack("<I", G)
for name, lo, hi, praw, ch in secs:
    blob = data[praw:praw + (hi - lo)]
    i = blob.find(pat)
    while i >= 0:
        va = lo + i
        # disassemble from a little before to have the whole instruction
        start = max(lo, va - 12)
        insns = list(md.disasm(blob[start - lo: va - lo + 20], start))
        window = [x for x in insns if x.address <= va + 12]
        text = " | ".join("%s %s" % (x.mnemonic, x.op_str) for x in window[-3:])
        print("%s %08X  %s" % (name, va, text))
        i = blob.find(pat, i + 1)
