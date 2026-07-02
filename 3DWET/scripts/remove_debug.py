#!/usr/bin/env python3
"""Remove DEBUG write statements from fabm.F90 for production builds."""
import os
import sys

# Default path relative to project root
default_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "src", "fabm", "src", "fabm.F90"
)

filepath = sys.argv[1] if len(sys.argv) > 1 else default_path

if not os.path.exists(filepath):
    print(f"Warning: {filepath} not found, skipping.")
    sys.exit(0)

with open(filepath, "r") as f:
    lines = f.readlines()

count = 0
new_lines = []
for line in lines:
    if "write(0,*)" in line and "DEBUG" in line:
        new_lines.append("!" + line)
        count += 1
    else:
        new_lines.append(line)

with open(filepath, "w") as f:
    f.writelines(new_lines)

print(f"Removed {count} DEBUG lines from {filepath}")
