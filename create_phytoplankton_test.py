#!/usr/bin/env python3
"""Create a minimal phytoplankton-only config to debug temporal_mean issue."""
import yaml

BASE = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\wet\testcases\fabm-wet.yaml"
OUTPUT = r"C:\Users\dinod\Desktop\GETM-FABM-WET\fabm_test_phytoplankton_only.yaml"

with open(BASE, 'r') as f:
    config = yaml.safe_load(f)

instances = config['instances']

# Keep only core modules + one phytoplankton module
keep_modules = [
    'abiotic_water', 'abiotic_sediment', 'bot_pel_interface',
    'POM', 'DOM', 'humus',
    'diatoms'  # just one phytoplankton group
]
for name in list(instances.keys()):
    if name not in keep_modules:
        del instances[name]

# Disable Si tracking for diatoms
if 'diatoms' in instances:
    params = instances['diatoms'].setdefault('parameters', {})
    for key in list(params.keys()):
        if key.startswith('lSi') and key[3:].isdigit():
            params[key] = False

# Add DOM_PV coupling for diatoms
if 'diatoms' in instances:
    coupling = instances['diatoms'].setdefault('coupling', {})
    coupling['DOM_DW_pool_sediment_PV'] = 'DOM/sDS_PV'
    coupling['DOM_N_pool_sediment_PV'] = 'DOM/sNS_PV'
    coupling['DOM_P_pool_sediment_PV'] = 'DOM/sPS_PV'
    coupling['DOM_C_pool_sediment_PV'] = 'DOM/sCS_PV'

print(f"Modules: {list(instances.keys())}")

with open(OUTPUT, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)

print(f"Saved to {OUTPUT}")
