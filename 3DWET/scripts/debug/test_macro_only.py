#!/usr/bin/env python3
"""Test: only macrophytes (no phytoplankton) to see if segfault occurs."""
import yaml

BASE = r"C:\Users\dinod\Desktop\GETM-FABM-WET\fabm_pvfix_25.yaml"
OUTPUT = r"C:\Users\dinod\Desktop\GETM-FABM-WET\fabm_test_macro_only.yaml"

with open(BASE, 'r') as f:
    config = yaml.safe_load(f)

instances = config['instances']

# Keep only core + macrophytes (remove phytoplankton and zooplankton)
remove = ['cyanobacteria', 'diatoms', 'greens', 'cladocerans', 'copepods', 'zoobenthos']
for name in remove:
    if name in instances:
        del instances[name]

print(f"Modules: {list(instances.keys())}")

with open(OUTPUT, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)

print(f"Saved to {OUTPUT}")
