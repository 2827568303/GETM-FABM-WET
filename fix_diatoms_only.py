#!/usr/bin/env python3
"""Iteratively fix food web with 1 phytoplankton (diatoms only)."""
import yaml
import os
import subprocess
import re

WORK_DIR = r"C:\Users\dinod\Desktop\GETM-FABM-WET"
BASE_YAML = r"C:\Users\dinod\Desktop\GETM-FABM-WET\fabm_pvfix_25.yaml"

def run_sim():
    result = subprocess.run(
        ["wsl", "-e", "bash", "-c",
         f"cd /mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/luomahu_case && "
         f"/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/install_gcc9_v5/bin/getm_cartesian 2>&1"],
        capture_output=True, text=True, timeout=600
    )
    return result.stdout + result.stderr

def get_error(output):
    if 'SIGSEGV' in output or 'Segmentation fault' in output:
        return 'segfault'
    if 'TIMERS SUM' in output:
        return 'success'
    for line in output.split('\n'):
        if 'FATAL ERROR' in line:
            return line.strip()
    return 'unknown'

def fix_error(config, error):
    """Auto-fix various coupling errors."""
    instances = config['instances']

    # Case 1: Coupling target not found
    m = re.search(r'Coupling target "([^/]+)/([^"]+)" for "([^"]+)" was not found', error)
    if m:
        missing_mod = m.group(1)
        coupling_name = m.group(3)
        if missing_mod not in instances:
            for inst_name, inst in instances.items():
                if 'coupling' in inst and coupling_name in inst['coupling']:
                    del inst['coupling'][coupling_name]
                    print(f"  Removed {inst_name}/{coupling_name}")
                    return True
        return False

    # Case 2: Variable mentioned in coupling but not in model
    m = re.search(r'model ([^ ]+) does not contain variable "([^"]+)" mentioned in coupling', error)
    if m:
        model_name = m.group(1)
        var_name = m.group(2)
        # Remove the variable from the coupling section
        if '/' in model_name:
            inst_name = model_name.lstrip('/')
        else:
            inst_name = model_name
        if inst_name in instances and 'coupling' in instances[inst_name]:
            if var_name in instances[inst_name]['coupling']:
                del instances[inst_name]['coupling'][var_name]
                print(f"  Removed {inst_name}/{var_name}")
                return True
        return False

    return False

def main():
    with open(BASE_YAML, 'r') as f:
        config = yaml.safe_load(f)

    instances = config['instances']
    for mod in ['macrophytes', 'cladocerans', 'copepods', 'zoobenthos',
                'JuFish', 'AdFish', 'PiscFish', 'cyanobacteria', 'greens']:
        if mod in instances:
            del instances[mod]

    if 'burial' in instances and 'parameters' in instances['burial']:
        p = instances['burial']['parameters']
        p['nMACRO'] = 0
        p['nBENT'] = 0
        p['nPHYT'] = 1

    print(f"Modules: {list(instances.keys())}")

    yaml_path = os.path.join(WORK_DIR, "fabm_diatoms_only.yaml")
    with open(yaml_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    for i in range(1, 50):
        print(f"\nIteration {i}...")
        wsl_path = yaml_path.replace('C:', '/mnt/c').replace('\\', '/')
        subprocess.run(["wsl", "-e", "cp", wsl_path,
                       "/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/luomahu_case/fabm.yaml"],
                      capture_output=True)

        output = run_sim()
        error = get_error(output)

        if error == 'success':
            print("SUCCESS!")
            return 0
        elif error == 'segfault':
            print("SEGFAULT!")
            return 1
        else:
            print(f"Error: {error}")
            if not fix_error(config, error):
                print("Could not fix")
                return 1
            with open(yaml_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    print("Max iterations")
    return 1

if __name__ == "__main__":
    exit(main())
