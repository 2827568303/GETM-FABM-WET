# -*- coding: utf-8 -*-
"""Locate code references to DEMO-limit strings and disassemble around them."""
import struct
import sys
import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

EXE = sys.argv[1] if len(sys.argv) > 1 else r"C:\EFDC84_APP\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
pe = pefile.PE(EXE, fast_load=True)
IB = pe.OPTIONAL_HEADER.ImageBase
text = None
for s in pe.sections:
    if b".text" in s.Name:
        text = s
        break
data = open(EXE, "rb").read()
tstart = IB + text.VirtualAddress
tbytes = data[text.PointerToRawData:text.PointerToRawData + text.Misc_VirtualSize]

TARGETS = {
    "demo_no_save": 0x51A308,
    "demo_func_limited": 0x5F0D48,
    "demo_threads2": 0x566FAC,
    "demo_particles10": 0x5F130C,
    "demo_version_status": 0x5023A4,
    "demo_limited_cap": 0x4EC76C,
    "demo_300cells": 0x4EC910,
    "demo_package": 0x4ECE74,
}
md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = True


def refs(va):
    pat = struct.pack("<I", va)
    out = []
    i = tbytes.find(pat)
    while i >= 0:
        out.append(tstart + i)
        i = tbytes.find(pat, i + 1)
    return out


def dump(va_from, va_to, mark=None):
    off = va_from - tstart
    blob = tbytes[off:off + (va_to - va_from)]
    print("--- %08X .. %08X ---" % (va_from, va_to))
    for ins in md.disasm(blob, va_from):
        tag = ""
        for m in ins.operands:
            if m.type == 3:  # imm
                if m.imm in TARGETS.values():
                    tag = "   <== %s" % [k for k, v in TARGETS.items() if v == m.imm][0]
        print("%08X  %-8s %-32s%s" % (ins.address, ins.mnemonic, ins.op_str, tag))


for name, va in TARGETS.items():
    rs = refs(va)
    print("\n########## %s @ %08X  refs=%s" % (name, va, ["%08X" % r for r in rs]))
    for r in rs:
        dump(max(tstart, r - 0x50), min(tstart + len(tbytes), r + 0x60))
