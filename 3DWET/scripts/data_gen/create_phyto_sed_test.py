#!/usr/bin/env python3
"""Add sediment_exchange and burial modules, test with phytoplankton."""
import yaml

BASE = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\wet\testcases\fabm-wet.yaml"
OUTPUT = r"C:\Users\dinod\Desktop\GETM-FABM-WET\fabm_test_phytoplankton_sed.yaml"

with open(BASE, 'r') as f:
    config = yaml.safe_load(f)

instances = config['instances']

# Keep core + sediment + phytoplankton
keep_modules = [
    'abiotic_water', 'abiotic_sediment', 'bot_pel_interface',
    'burial', 'sediment_exchange',
    'POM', 'DOM', 'humus',
    'diatoms'
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

# Add POM_PV and humus_PV coupling for burial
if 'burial' in instances:
    coupling = instances['burial'].setdefault('coupling', {})
    coupling['POM_DW_pool_sediment_PV'] = 'POM/sDS_PV'
    coupling['POM_N_pool_sediment_PV'] = 'POM/sNS_PV'
    coupling['POM_P_pool_sediment_PV'] = 'POM/sPS_PV'
    coupling['POM_C_pool_sediment_PV'] = 'POM/sCS_PV'
    coupling['humus_DW_in_deep_sediment_PV'] = 'humus/sDS_PV'
    coupling['humus_N_in_deep_sediment_PV'] = 'humus/sNS_PV'
    coupling['humus_P_in_deep_sediment_PV'] = 'humus/sPS_PV'
    coupling['humus_C_in_deep_sediment_PV'] = 'humus/sCS_PV'

print(f"Modules: {list(instances.keys())}")

with open(OUTPUT, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)

print(f"Saved to {OUTPUT}")
