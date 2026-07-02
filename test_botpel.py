#!/usr/bin/env python3
"""Test: add bot_pel_interface module."""
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
    log_file = os.path.join(LOG_DIR, f"test2_{sim_name}.log")
    
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
    print("Test bot_pel_interface")
    print("=" * 60)
    
    with open(BASE_FABM, 'r') as f:
        base_config = yaml.safe_load(f)
    
    all_instances = base_config['instances']
    
    # Test with bot_pel_interface added
    print("\n--- Test: abiotic + POM + DOM + humus + bot_pel_interface ---")
    modules = ['abiotic_water', 'abiotic_sediment', 'bot_pel_interface', 'POM', 'DOM', 'humus']
    config = {'instances': {}}
    for m in modules:
        if m in all_instances:
            config['instances'][m] = all_instances[m]
    
    # Also check if we need sediment_exchange and burial
    path = os.path.join(WORK_DIR, "fabm_test_botpel.yaml")
    with open(path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    copy_config_to_case(path)
    success, fatal, unfulfilled = run_simulation("botpel", days=2)
    print(f"  Success: {success}")
    if fatal: print(f"  Fatal: {fatal}")
    if unfulfilled: print(f"  Unfulfilled: {unfulfilled}")
    
    if not success and 'UNFULFILLED' in str(fatal):
        print("\n  bot_pel_conv needs host support. Let's check if we can work around it...")

if __name__ == "__main__":
    sys.exit(main())
