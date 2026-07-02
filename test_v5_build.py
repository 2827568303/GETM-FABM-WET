#!/usr/bin/env python3
"""Test bot_pel_conv patch with v5 build."""
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

def run_simulation(sim_name, days=2, getm_bin="install_gcc9_v5"):
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, f"v5_{sim_name}.log")
    
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
    wsl_getm_bin = f"/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/{getm_bin}/bin/getm_cartesian"
    
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
    print("Test v5 build (with bot_pel_conv patch)")
    print("=" * 60)
    
    with open(BASE_FABM, 'r') as f:
        base_config = yaml.safe_load(f)
    
    all_instances = base_config['instances']
    
    # Test 1: abiotic + POM + DOM + humus + bot_pel_interface
    print("\n--- Test 1: Core modules (abiotic + POM + DOM + humus + bot_pel_interface) ---")
    modules = ['abiotic_water', 'abiotic_sediment', 'bot_pel_interface', 'POM', 'DOM', 'humus']
    config = {'instances': {}}
    for m in modules:
        if m in all_instances:
            config['instances'][m] = all_instances[m]
    
    path = os.path.join(WORK_DIR, "fabm_v5_test1.yaml")
    with open(path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    copy_config_to_case(path)
    success, fatal, unfulfilled = run_simulation("test1_core", days=2)
    print(f"  Success: {success}")
    if fatal: print(f"  Fatal: {fatal}")
    if unfulfilled: print(f"  Unfulfilled: {unfulfilled}")
    
    if not success:
        print("\n  Test 1 failed. Stopping.")
        return 1
    
    # Test 2: add sediment_exchange + burial
    print("\n--- Test 2: + sediment_exchange + burial ---")
    modules += ['sediment_exchange', 'burial']
    config = {'instances': {}}
    for m in modules:
        if m in all_instances:
            config['instances'][m] = all_instances[m]
    
    path = os.path.join(WORK_DIR, "fabm_v5_test2.yaml")
    with open(path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    copy_config_to_case(path)
    success, fatal, unfulfilled = run_simulation("test2_sediment", days=2)
    print(f"  Success: {success}")
    if fatal: print(f"  Fatal: {fatal}")
    if unfulfilled: print(f"  Unfulfilled: {unfulfilled}")
    
    if not success:
        print("\n  Test 2 failed. Stopping.")
        return 1
    
    # Test 3: add phytoplankton + zooplankton + zoobenthos + macrophytes
    # Note: will likely fail due to missing PAR (no meteo forcing)
    print("\n--- Test 3: + full food web (expected to fail on PAR) ---")
    food_web_modules = ['cyanobacteria', 'diatoms', 'greens', 'cladocerans', 'copepods', 'zoobenthos', 'macrophytes']
    modules += food_web_modules
    config = {'instances': {}}
    for m in modules:
        if m in all_instances:
            config['instances'][m] = all_instances[m]
    
    # Add _PV couplings
    pv_couplings = {
        'POM_DW_pool_sediment_PV': 'POM/sDS_PV',
        'POM_N_pool_sediment_PV': 'POM/sNS_PV',
        'POM_P_pool_sediment_PV': 'POM/sPS_PV',
        'POM_C_pool_sediment_PV': 'POM/sCS_PV',
        'DOM_DW_pool_sediment_PV': 'DOM/sDS_PV',
        'DOM_N_pool_sediment_PV': 'DOM/sNS_PV',
        'DOM_P_pool_sediment_PV': 'DOM/sPS_PV',
        'DOM_C_pool_sediment_PV': 'DOM/sCS_PV',
    }
    humus_pv = {
        'humus_DW_in_deep_sediment_PV': 'humus/sDS_PV',
        'humus_N_in_deep_sediment_PV': 'humus/sNS_PV',
        'humus_P_in_deep_sediment_PV': 'humus/sPS_PV',
        'humus_C_in_deep_sediment_PV': 'humus/sCS_PV',
    }
    
    for name in food_web_modules + ['burial']:
        if name in config['instances']:
            inst = config['instances'][name]
            coupling = inst.setdefault('coupling', {})
            if name == 'burial':
                for var, target in humus_pv.items():
                    coupling[var] = target
            for var, target in pv_couplings.items():
                coupling[var] = target
    
    path = os.path.join(WORK_DIR, "fabm_v5_test3.yaml")
    with open(path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    copy_config_to_case(path)
    success, fatal, unfulfilled = run_simulation("test3_foodweb", days=2)
    print(f"  Success: {success}")
    if fatal: print(f"  Fatal: {fatal}")
    if unfulfilled: print(f"  Unfulfilled: {unfulfilled}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
