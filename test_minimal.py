#!/usr/bin/env python3
"""Test minimal config and check if bot_pel_conv is really the issue."""
import yaml
import os
import subprocess
import sys
import re
from datetime import datetime, timedelta

WORK_DIR = r"C:\Users\dinod\Desktop\GETM-FABM-WET"
CASE_DIR = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\luomahu_case"
BASE_FABM = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\wet\testcases\fabm-wet.yaml"
LOG_DIR = os.path.join(r"C:\Users\dinod\Desktop\GETM-FABM-PCLake", "run_logs")

def copy_config_to_case(yaml_path):
    wsl_path = yaml_path.replace('C:', '/mnt/c').replace('\\', '/')
    result = subprocess.run(
        ["wsl", "-e", "bash", "-c", 
         f"cp {wsl_path} /mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/luomahu_case/fabm.yaml && echo OK"],
        capture_output=True, text=True
    )
    return result.returncode == 0

def run_simulation(sim_name, days=2):
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, f"minimal_{sim_name}.log")
    
    inp_file = os.path.join(CASE_DIR, "getm.inp")
    with open(inp_file, 'r') as f:
        content = f.read()
    
    start = datetime(2020, 1, 1)
    stop = start + timedelta(days=days)
    stop_str = stop.strftime('%Y-%m-%d %H:%M:%S')
    content_new = re.sub(r"stop\s*=\s*'[^']*'", f"stop = '{stop_str}'", content)
    with open(inp_file, 'w') as f:
        f.write(content_new)
    
    wsl_case_dir = "/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/luomahu_case"
    wsl_getm_bin = "/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/install_gcc9_v4/bin/getm_cartesian"
    
    result = subprocess.run(
        ["wsl", "-e", "bash", "-c", f"cd {wsl_case_dir} && {wsl_getm_bin}"],
        capture_output=True, text=True, timeout=3600
    )
    
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"=== {sim_name} ===\n\n=== STDOUT ===\n{result.stdout}\n=== STDERR ===\n{result.stderr}")
    
    output = result.stdout + result.stderr
    
    unfulfilled = []
    in_unfulfilled = False
    for line in output.split('\n'):
        if 'UNFULFILLED DEPENDENCY' in line:
            dep = line.split(':')[-1].strip()
            unfulfilled.append(dep)
    
    fatal_error = None
    for line in output.split('\n'):
        if 'FATAL ERROR' in line.upper():
            fatal_error = line.strip()
            break
    
    return result.returncode == 0, fatal_error, unfulfilled

def main():
    print("=" * 60)
    print("Minimal config test")
    print("=" * 60)
    
    with open(BASE_FABM, 'r') as f:
        base_config = yaml.safe_load(f)
    
    all_instances = base_config['instances']
    
    # Test 1: abiotic_water only
    print("\n--- Test 1: abiotic_water only ---")
    config1 = {'instances': {'abiotic_water': all_instances['abiotic_water']}}
    path1 = os.path.join(WORK_DIR, "fabm_test_abiotic.yaml")
    with open(path1, 'w') as f:
        yaml.dump(config1, f, default_flow_style=False, sort_keys=False)
    copy_config_to_case(path1)
    success, fatal, unfulfilled = run_simulation("abiotic_only", days=1)
    print(f"  Success: {success}")
    if fatal: print(f"  Fatal: {fatal}")
    if unfulfilled: print(f"  Unfulfilled: {unfulfilled}")
    
    # Test 2: abiotic_water + POM
    print("\n--- Test 2: abiotic_water + POM ---")
    config2 = {'instances': {
        'abiotic_water': all_instances['abiotic_water'],
        'POM': all_instances['POM'],
    }}
    path2 = os.path.join(WORK_DIR, "fabm_test_abiotic_pom.yaml")
    with open(path2, 'w') as f:
        yaml.dump(config2, f, default_flow_style=False, sort_keys=False)
    copy_config_to_case(path2)
    success, fatal, unfulfilled = run_simulation("abiotic_pom", days=1)
    print(f"  Success: {success}")
    if fatal: print(f"  Fatal: {fatal}")
    if unfulfilled: print(f"  Unfulfilled: {unfulfilled}")
    
    # Test 3: Check what happens with full abiotic modules
    print("\n--- Test 3: all abiotic + POM + DOM + humus ---")
    config3 = {'instances': {
        'abiotic_water': all_instances['abiotic_water'],
        'abiotic_sediment': all_instances['abiotic_sediment'],
        'POM': all_instances['POM'],
        'DOM': all_instances['DOM'],
        'humus': all_instances['humus'],
    }}
    path3 = os.path.join(WORK_DIR, "fabm_test_om_only.yaml")
    with open(path3, 'w') as f:
        yaml.dump(config3, f, default_flow_style=False, sort_keys=False)
    copy_config_to_case(path3)
    success, fatal, unfulfilled = run_simulation("om_only", days=1)
    print(f"  Success: {success}")
    if fatal: print(f"  Fatal: {fatal}")
    if unfulfilled: print(f"  Unfulfilled: {unfulfilled}")

if __name__ == "__main__":
    sys.exit(main())
