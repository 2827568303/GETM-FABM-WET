#!/usr/bin/env python3
"""Test: remove macrophytes to see if segfault disappears."""
import yaml

BASE = r"C:\Users\dinod\Desktop\GETM-FABM-WET\fabm_pvfix_25.yaml"
OUTPUT = r"C:\Users\dinod\Desktop\GETM-FABM-WET\fabm_test_no_macro.yaml"

with open(BASE, 'r') as f:
    config = yaml.safe_load(f)

instances = config['instances']

# Remove macrophytes
if 'macrophytes' in instances:
    del instances['macrophytes']

print(f"Modules: {list(instances.keys())}")

with open(OUTPUT, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)

print(f"Saved to {OUTPUT}")
