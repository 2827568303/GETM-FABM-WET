#!/usr/bin/env python3
"""Find all _PV dependencies in WET source code to understand what couplings are needed."""
import os
import re

WET_SRC = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\wet\src"

print("Searching for _PV state dependencies in WET modules...\n")

pv_pattern = re.compile(r"register_state_dependency.*'([^']*_PV[^']*)'")

for f in os.listdir(WET_SRC):
    if not f.endswith('.F90'):
        continue
    fpath = os.path.join(WET_SRC, f)
    with open(fpath, 'r', encoding='latin-1') as fh:
        content = fh.read()
    
    matches = pv_pattern.findall(content)
    if matches:
        module_name = f.replace('.F90', '')
        print(f"{module_name}:")
        for m in matches:
            print(f"  - {m}")
        print()
