#!/usr/bin/env python3
"""Fix fabm.yaml - add missing DOM_PV coupling for macrophytes."""
import yaml
import os
import subprocess

BASE_FABM = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\wet\testcases\fabm-wet.yaml"
CASE_DIR = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\luomahu_case"
WORK_DIR = r"C:\Users\dinod\Desktop\GETM-FABM-WET"

# Load base config
with open(BASE_FABM, 'r') as f:
    config = yaml.safe_load(f)

instances = config['instances']

# Fix macrophytes coupling - add missing DOM_PV couplings
macro = instances['macrophytes']
coupling = macro['coupling']

# Add missing DOM_PV couplings
coupling['DOM_DW_pool_sediment_PV'] = 'DOM/sDS_PV'
coupling['DOM_N_pool_sediment_PV'] = 'DOM/sNS_PV'
coupling['DOM_P_pool_sediment_PV'] = 'DOM/sPS_PV'
coupling['DOM_C_pool_sediment_PV'] = 'DOM/sCS_PV'

print("Added DOM_PV couplings to macrophytes:")
for k, v in coupling.items():
    if '_PV' in k:
        print(f"  {k}: {v}")

# Save to temp file
temp_path = os.path.join(WORK_DIR, "fabm_fixed.yaml")
with open(temp_path, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)

print(f"\nSaved to {temp_path}")

# Copy to case dir via WSL
result = subprocess.run(
    ["wsl", "-e", "bash", "-c", 
     f"cp /mnt/c/Users/dinod/Desktop/GETM-FABM-WET/fabm_fixed.yaml /mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/luomahu_case/fabm.yaml && echo 'Copied successfully'"],
    capture_output=True,
    text=True
)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
