#!/usr/bin/env python3
"""Debug: start from working config and add modules incrementally."""
import yaml
import os
import subprocess
import sys
import time
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
    log_file = os.path.join(LOG_DIR, f"debug_{sim_name}.log")
    
    inp_file = os.path.join(CASE_DIR, "getm.inp")
    with open(inp_file, 'r') as f:
        content = f.read()
    
    start = datetime(2020, 1, 1)
    stop = start + timedelta(days=days)
    stop_str = stop.strftime('%Y-%m-%d %H:%M:%S')
    content_new = re.sub(r"stop\s*=\s*'[^']*'", f"stop = '{stop_str}'", content)
    with open(inp_file, 'w') as f:
        f.write(content_new)
    
    start_time = time.time()
    wsl_case_dir = "/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/luomahu_case"
    wsl_getm_bin = "/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/install_gcc9_v4/bin/getm_cartesian"
    
    result = subprocess.run(
        ["wsl", "-e", "bash", "-c", f"cd {wsl_case_dir} && {wsl_getm_bin}"],
        capture_output=True, text=True, timeout=3600
    )
    
    elapsed = time.time() - start_time
    
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"=== {sim_name} ===\n\n=== STDOUT ===\n{result.stdout}\n=== STDERR ===\n{result.stderr}")
    
    output = result.stdout + result.stderr
    
    unfulfilled = []
    fatal_error = None
    for line in output.split('\n'):
        if 'UNFULFILLED DEPENDENCY' in line:
            dep = line.split(':')[-1].strip()
            unfulfilled.append(dep)
        if 'FATAL ERROR' in line.upper():
            fatal_error = line.strip()
    
    return result.returncode == 0, fatal_error, unfulfilled, elapsed

def main():
    print("=" * 60)
    print("Incremental module addition test")
    print("=" * 60)
    
    with open(BASE_FABM, 'r') as f:
        base_config = yaml.safe_load(f)
    
    all_instances = base_config['instances']
    print(f"\nAll available instances: {list(all_instances.keys())}")
    
    # Start with core abiotic + POM + DOM (should work)
    test_modules = [
        ['abiotic_water', 'abiotic_sediment', 'POM', 'DOM'],
        ['abiotic_water', 'abiotic_sediment', 'POM', 'DOM', 'bot_pel_interface'],
        ['abiotic_water', 'abiotic_sediment', 'POM', 'DOM', 'bot_pel_interface', 'humus'],
        ['abiotic_water', 'abiotic_sediment', 'POM', 'DOM', 'bot_pel_interface', 'humus', 'sediment_exchange'],
        ['abiotic_water', 'abiotic_sediment', 'POM', 'DOM', 'bot_pel_interface', 'humus', 'sediment_exchange', 'burial'],
    ]
    
    for i, modules in enumerate(test_modules):
        test_name = f"test_{i+1}_{'_'.join(modules)}"
        print(f"\n--- Test {i+1}: {', '.join(modules)} ---")
        
        config = {'instances': {}}
        for m in modules:
            if m in all_instances:
                config['instances'][m] = all_instances[m]
        
        config_path = os.path.join(WORK_DIR, f"fabm_{test_name}.yaml")
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        copy_config_to_case(config_path)
        
        success, fatal_error, unfulfilled, elapsed = run_simulation(test_name, days=2)
        
        if success:
            print(f"  SUCCESS ({elapsed:.1f}s)")
        else:
            print(f"  FAILED ({elapsed:.1f}s)")
            if unfulfilled:
                print(f"  Unfulfilled deps: {unfulfilled}")
            if fatal_error:
                print(f"  Fatal: {fatal_error}")
            print("\n  Stopping at first failure.")
            break

if __name__ == "__main__":
    sys.exit(main())
