# -*- coding: utf-8 -*-
"""Dump every code reference to a global VA and disassemble around it."""
import struct
import sys
import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

EXE = sys.argv[1]
TARGET = int(sys.argv[2], 16)
PAD_BEFORE = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0x40
PAD_AFTER = int(sys.argv[4], 0) if len(sys.argv) > 4 else 0x60

pe = pefile.PE(EXE, fast_load=True)
IB = pe.OPTIONAL_HEADER.ImageBase
data = open(EXE, "rb").read()
md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = True

for s in pe.sections:
    name = s.Name.rstrip(b"\x00").decode(errors="replace")
    start = IB + s.VirtualAddress
    blob = data[s.PointerToRawData:s.PointerToRawData + s.Misc_VirtualSize]
    pat = struct.pack("<I", TARGET)
    i = blob.find(pat)
    while i >= 0:
        va = start + i
        lo = max(start, va - PAD_BEFORE)
        hi = min(start + len(blob), va + PAD_AFTER)
        print("\n#### %s  section=%s  ref@%08X" % (EXE, name, va))
        for ins in md.disasm(blob[lo - start:hi - start], lo):
            mark = " <== REF" if ins.address == va else ""
            print("%08X  %-9s %-34s%s" % (ins.address, ins.mnemonic, ins.op_str, mark))
        i = blob.find(pat, i + 1)
