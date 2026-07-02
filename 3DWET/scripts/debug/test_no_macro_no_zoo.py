#!/usr/bin/env python3
"""Test: no macrophytes, no zooplankton."""
import yaml
import os
import subprocess
import sys

WORK_DIR = r"C:\Users\dinod\Desktop\GETM-FABM-WET"
BASE_YAML = r"C:\Users\dinod\Desktop\GETM-FABM-WET\fabm_pvfix_25.yaml"
OUTPUT = r"C:\Users\dinod\Desktop\GETM-FABM-WET\fabm_test_no_macro_no_zoo.yaml"
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

# Remove macrophytes
print("Removing macrophytes...")
remove_module(config, 'macrophytes')
config['instances']['burial']['parameters']['nMACRO'] = 0

# Remove zooplankton
print("Removing zooplankton...")
remove_module(config, 'cladocerans')
remove_module(config, 'copepods')
config['instances']['burial']['parameters']['nPHYT'] = 3  # still 3 phyto

# Remove fish
for fm in ['JuFish', 'AdFish', 'PiscFish']:
    remove_module(config, fm)

print(f"\nModules: {list(config['instances'].keys())}")

with open(OUTPUT, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)

# Run test
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
