#!/usr/bin/env python3
"""Test: phyto3 + zoobenthos."""
import yaml

BASE = r"C:\Users\dinod\Desktop\GETM-FABM-WET\fabm_pvfix_25.yaml"
OUTPUT = r"C:\Users\dinod\Desktop\GETM-FABM-WET\fabm_test_phyto3_zoo.yaml"

with open(BASE, 'r') as f:
    config = yaml.safe_load(f)

instances = config['instances']

keep = ['abiotic_water', 'abiotic_sediment', 'bot_pel_interface',
        'burial', 'sediment_exchange',
        'POM', 'DOM', 'humus',
        'cyanobacteria', 'diatoms', 'greens',
        'zoobenthos']

for name in list(instances.keys()):
    if name not in keep:
        del instances[name]

print(f"Modules: {list(instances.keys())}")

with open(OUTPUT, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)

print(f"Saved to {OUTPUT}")
