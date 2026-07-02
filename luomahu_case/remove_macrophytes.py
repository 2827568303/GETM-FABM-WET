#!/usr/bin/env python3
"""Remove macrophytes from fabm.yaml to fix coupling issues"""

import re

# Read the file
with open('fabm.yaml', 'r') as f:
    content = f.read()

# Find and remove the macrophytes instance block
# Pattern matches from "  macrophytes:" to the next "  <name>:" or end of file
macrophytes_pattern = r'  macrophytes:\n.*?(?=\n  [a-z_]+:|\n[^ ])'

# Remove macrophytes references from sediment_exchange coupling
content = re.sub(r'      POM_macrophyte_update1: macrophytes/tDBedPOMS\n', '', content)

# Remove macrophytes instance (keep the pattern lenient)
lines = content.split('\n')
new_lines = []
skip_macrophytes = False
in_macrophytes = False

for i, line in enumerate(lines):
    if line.strip() == 'macrophytes:':
        in_macrophytes = True
        skip_macrophytes = True
        continue
    if skip_macrophytes and line.startswith('  ') and not line.startswith('    '):
        # We've reached the next top-level instance
        skip_macrophytes = False
        in_macrophytes = False
    if not skip_macrophytes:
        new_lines.append(line)

# Also remove fish references to macrophytes (cRelVegPlan, cRelVegBent)
new_lines = [line for line in new_lines if 'cRelVegPlan' not in line and 'cRelVegBent' not in line]

content = '\n'.join(new_lines)

# Write back
with open('fabm.yaml', 'w') as f:
    f.write(content)

print("Macrophytes removed from fabm.yaml")
