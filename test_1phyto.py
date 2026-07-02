#!/usr/bin/env python3
"""Test: only diatoms (1 phytoplankton) + core."""
import yaml
import os
import subprocess

WORK_DIR = r"C:\Users\dinod\Desktop\GETM-FABM-WET"
BASE_YAML = r"C:\Users\dinod\Desktop\GETM-FABM-WET\fabm_pvfix_25.yaml"
OUTPUT = r"C:\Users\dinod\Desktop\GETM-FABM-WET\fabm_test_1phyto.yaml"
LOG_DIR = os.path.join(r"C:\Users\dinod\Desktop\GETM-FABM-PCLake", "run_logs")

with open(BASE_YAML, 'r') as f:
    config = yaml.safe_load(f)

instances = config['instances']

# Keep only core + diatoms (1 phytoplankton)
for mod in ['macrophytes', 'cladocerans', 'copepods', 'zoobenthos',
            'JuFish', 'AdFish', 'PiscFish', 'cyanobacteria', 'greens']:
    if mod in instances:
        del instances[mod]

# Update counts
if 'burial' in instances and 'parameters' in instances['burial']:
    p = instances['burial']['parameters']
    p['nMACRO'] = 0
    p['nBENT'] = 0
    p['nPHYT'] = 1  # Only 1 phytoplankton

print(f"Modules: {list(instances.keys())}")

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
