#!/usr/bin/env python3
"""Test: only 3 phytoplankton groups + core (no zoobenthos, no macro, no zoo)."""
import yaml
import os
import subprocess
import sys

WORK_DIR = r"C:\Users\dinod\Desktop\GETM-FABM-WET"
BASE_YAML = r"C:\Users\dinod\Desktop\GETM-FABM-WET\fabm_pvfix_25.yaml"
OUTPUT = r"C:\Users\dinod\Desktop\GETM-FABM-WET\fabm_test_phyto3_only.yaml"
LOG_DIR = os.path.join(r"C:\Users\dinod\Desktop\GETM-FABM-PCLake", "run_logs")

def remove_module(config, module_name):
    instances = config['instances']
    if module_name in instances:
        del instances[module_name]
        print(f"Removed instance: {module_name}")
    
    for inst_name, inst in list(instances.items()):
        if 'coupling' not in inst:
            continue
        coupling = inst['coupling']
        to_remove = [k for k, v in list(coupling.items()) 
                     if isinstance(v, str) and v.startswith(module_name + '/')]
        for k in to_remove:
            del coupling[k]
            print(f"  Removed coupling {inst_name}/{k}")

with open(BASE_YAML, 'r') as f:
    config = yaml.safe_load(f)

# Remove everything except core + 3 phytoplankton
for mod in ['macrophytes', 'cladocerans', 'copepods', 'zoobenthos', 
            'JuFish', 'AdFish', 'PiscFish']:
    remove_module(config, mod)

# Update counts
config['instances']['burial']['parameters']['nMACRO'] = 0
config['instances']['burial']['parameters']['nBENT'] = 0
config['instances']['burial']['parameters']['nPHYT'] = 3

print(f"\nModules: {list(config['instances'].keys())}")

with open(OUTPUT, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)

wsl_path = OUTPUT.replace('C:', '/mnt/c').replace('\\', '/')
subprocess.run(["wsl", "-e", "cp", wsl_path, 
                "/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/luomahu_case/fabm.yaml"],
               capture_output=True)

os.makedirs(LOG_DIR, exist_ok=True)
result = subprocess.run(
    ["wsl", "-e", "bash", "-c", 
     f"cd /mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/luomahu_case && "
     f"/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/install_gcc9_v5/bin/getm_cartesian 2>&1 | tail -30"],
    capture_output=True, text=True, timeout=600
)
print("\n" + "="*60)
print(result.stdout)
print(result.stderr)
