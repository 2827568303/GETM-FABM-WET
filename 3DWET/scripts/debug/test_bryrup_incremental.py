#!/usr/bin/env python3
"""Test Lake Bryrup config with fish_pclake model, and without fish first."""
import yaml
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
import re

WORK_DIR = r"C:\Users\dinod\Desktop\GETM-FABM-WET"
CASE_DIR = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\luomahu_case"
BRYRUP_FABM = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\wet\testcases\lake_bryrup_denmark\fabm.yaml"
LOG_DIR = os.path.join(r"C:\Users\dinod\Desktop\GETM-FABM-PCLake", "run_logs")

def run_simulation(sim_name, days=3):
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, f"{sim_name}.log")
    
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
    
    if result.returncode != 0:
        print(f"  FAILED ({elapsed:.1f}s)")
        for line in (result.stdout + result.stderr).split('\n'):
            if 'FATAL' in line.upper() or 'ERROR' in line.upper():
                print(f"  {line.strip()}")
        return False
    
    print(f"  OK ({elapsed:.1f}s)")
    try:
        import netCDF4 as nc
        ds = nc.Dataset(os.path.join(CASE_DIR, "LUOMAHU_WET.3d.nc"), 'r')
        print(f"  Variables: {len(ds.variables)}")
        ds.close()
    except:
        pass
    return True

def copy_config_to_case(yaml_path):
    """Copy a yaml config to case dir via WSL."""
    wsl_path = yaml_path.replace('C:', '/mnt/c').replace('\\', '/')
    result = subprocess.run(
        ["wsl", "-e", "bash", "-c", 
         f"cp {wsl_path} /mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/luomahu_case/fabm.yaml && echo OK"],
        capture_output=True, text=True
    )
    return result.returncode == 0

def main():
    print("=" * 60)
    print("Strategy: Build up from working base")
    print("=" * 60)
    
    with open(BRYRUP_FABM, 'r') as f:
        config = yaml.safe_load(f)
    
    instances = config['instances']
    print(f"\nTotal instances in bryrup config: {len(instances)}")
    
    # Step 1: Remove fish modules first, test base food web
    print("\n--- Step 1: Test without fish ---")
    config_no_fish = {'instances': {}}
    for name, inst in instances.items():
        model = inst.get('model', '')
        if 'fish' not in model.lower():
            config_no_fish['instances'][name] = inst
    
    no_fish_path = os.path.join(WORK_DIR, "fabm_bryrup_nofish.yaml")
    with open(no_fish_path, 'w') as f:
        yaml.dump(config_no_fish, f, default_flow_style=False, sort_keys=False)
    
    copy_config_to_case(no_fish_path)
    success = run_simulation("bryrup_nofish", days=5)
    
    if success:
        print("\n  Base food web works! Now adding fish...")
        
        # Step 2: Try changing fish model from wet/fish to wet/fish_pclake
        print("\n--- Step 2: Test with fish_pclake model ---")
        config_with_fish_pclake = {'instances': {}}
        for name, inst in instances.items():
            model = inst.get('model', '')
            if model == 'wet/fish':
                inst_new = dict(inst)
                inst_new['model'] = 'wet/fish_pclake'
                config_with_fish_pclake['instances'][name] = inst_new
            else:
                config_with_fish_pclake['instances'][name] = inst
        
        fish_pclake_path = os.path.join(WORK_DIR, "fabm_bryrup_fishpclake.yaml")
        with open(fish_pclake_path, 'w') as f:
            yaml.dump(config_with_fish_pclake, f, default_flow_style=False, sort_keys=False)
        
        copy_config_to_case(fish_pclake_path)
        success2 = run_simulation("bryrup_fishpclake", days=5)
        
        if success2:
            print("\n  Full food web with fish works!")
            return 0
        else:
            print("\n  Fish still failing, but base food web works.")
            return 0
    else:
        print("\n  Base food web (no fish) also failed. Need to debug more.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
