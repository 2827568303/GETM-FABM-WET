"""Remove fish modules (JuFish, AdFish, PiscFish) from fabm.yaml.

This is the known workaround for the time_step dangling pointer segfault
(see DEBUG_HISTORY_REPORT.md section 4.4). The GETM binary does not properly
link the time_step FABM variable, which fish modules depend on.
"""
import re

fpath = 'fabm.yaml'
with open(fpath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and remove the three fish instance blocks
# Each block starts with "  JuFish:", "  AdFish:", or "  PiscFish:" at 2-space indent
# and ends before the next top-level instance or EOF
fish_names = ['JuFish', 'AdFish', 'PiscFish']
lines = content.split('\n')
output_lines = []
skip = False
for line in lines:
    stripped = line.lstrip()
    indent = len(line) - len(stripped)
    # Check if this line starts a fish instance block
    if indent == 2 and stripped.rstrip(':') in fish_names:
        skip = True
        continue
    # Check if this line starts a new top-level instance (2-space indent, ends with :)
    # or a new top-level key (0-indent)
    if skip:
        if indent == 2 and stripped.endswith(':') and not stripped.startswith('#'):
            # New instance block starts
            skip = False
            output_lines.append(line)
        elif indent == 0 and not stripped.startswith('#') and stripped:
            # Top-level key
            skip = False
            output_lines.append(line)
        else:
            # Still inside fish block, skip
            continue
    else:
        output_lines.append(line)

# Remove trailing empty lines
while output_lines and not output_lines[-1].strip():
    output_lines.pop()
output_lines.append('')  # single trailing newline

new_content = '\n'.join(output_lines)
with open(fpath, 'w', encoding='utf-8') as f:
    f.write(new_content)

# Verify
with open(fpath, 'r', encoding='utf-8') as f:
    check = f.read()
for name in fish_names:
    if name in check:
        print(f'WARNING: {name} still present in fabm.yaml!')
    else:
        print(f'OK: {name} removed')

print(f'Original lines: {len(lines)}, New lines: {len(output_lines)}')
