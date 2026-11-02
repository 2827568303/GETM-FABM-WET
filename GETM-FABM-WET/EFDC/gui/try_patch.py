# -*- coding: utf-8 -*-
"""Byte-patch experiments on a copy of the app folder; report GUI outcome.

python -X utf8 gui/try_patch.py <src-exe> <out-dir> <hexoff>:<hexbytes> [more...]
"""
import os
import shutil
import subprocess
import sys

src, outdir = sys.argv[1], sys.argv[2]
patches = []
for spec in sys.argv[3:]:
    off, data = spec.split(":")
    patches.append((int(off, 16), bytes.fromhex(data)))

srcdir = os.path.dirname(os.path.abspath(src))
outdir = os.path.abspath(outdir)
if os.path.abspath(srcdir) != outdir:
    if os.path.isdir(outdir):
        shutil.rmtree(outdir)
    shutil.copytree(srcdir, outdir)
out = os.path.join(outdir, os.path.basename(src))

with open(out, "r+b") as f:
    for off, data in patches:
        f.seek(off)
        old = f.read(len(data))
        f.seek(off)
        f.write(data)
        print("patch 0x%x: %s -> %s" % (off, old.hex(), data.hex()))

WATCH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "watch2.py")
p = subprocess.Popen([sys.executable, "-X", "utf8", WATCH, out, "13", "trypatch"],
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
out_text = p.communicate()[0]
print("---")
print("main window (EFDC_Explorer7.3) : %s" % ("EFDC_Explorer7.3" in out_text))
print("activation wizard              : %s" % ("Activation Wizard" in out_text))
print("message box                    : %s" % ("#32770" in out_text))
print("exited early                   : %s" % ("EXITED" in out_text))
for line in out_text.splitlines():
    if any(k in line for k in ("EFDC_Explorer7.3", "Activation Wizard", "EXITED", "#32770")):
        print("   ", line)
