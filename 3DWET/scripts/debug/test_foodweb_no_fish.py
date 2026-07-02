#!/usr/bin/env python3
"""Test food web without fish first."""
import yaml
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
import re

WORK_DIR = r"C:\Users\dinod\Desktop\GETM-FABM-WET"
CASE_DIR = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\luomahu_case"
BASE_FABM = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\wet\testcases\fabm-wet.yaml"
LOG_DIR = os.path.join(r"C:\Users\dinod\Desktop\GETM-FABM-PCLake", "run_logs")

def fix_config(config):
    """Fix known issues in fabm config."""
    instances = config['instances']
    
    # Fix 1: Add missing DOM_PV couplings to macrophytes
    if 'macrophytes' in instances:
        macro = instances['macrophytes']
        coupling = macro.setdefault('coupling', {})
        for var, target in [
            ('DOM_DW_pool_sediment_PV', 'DOM/sDS_PV'),
            ('DOM_N_pool_sediment_PV', 'DOM/sNS_PV'),
            ('DOM_P_pool_sediment_PV', 'DOM/sPS_PV'),
            ('DOM_C_pool_sediment_PV', 'DOM/sCS_PV'),
        ]:
            if var not in coupling:
                coupling[var] = target
    
    # Fix 2: Remove fish modules for now (they have parameter issues)
    fish_modules = [k for k in instances.keys() if 'Fish' in k or 'fish' in k]
    for fm in fish_modules:
        del instances[fm]
        print(f"  Removed fish module: {fm}")
    
    return config

def run_simulation(sim_name, days=3):
    """Run a simulation and capture output."""
    os.makedirs(LOG_DIR, exist_ok=True)
    
    log_file = os.path.join(LOG_DIR, f"{sim_name}.log")
    
    # Update getm.inp with simulation duration
    inp_file = os.path.join(CASE_DIR, "getm.inp")
    
    with open(inp_file, 'r') as f:
        content = f.read()
    
    start = datetime(2020, 1, 1)
    stop = start + timedelta(days=days)
    stop_str = stop.strftime('%Y-%m-%d %H:%M:%S')
    
    content_new = re.sub(
        r"stop\s*=\s*'[^']*'",
        f"stop = '{stop_str}'",
        content
    )
    
    with open(inp_file, 'w') as f:
        f.write(content_new)
    
    # Run GETM
    start_time = time.time()
    
    wsl_case_dir = "/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/luomahu_case"
    wsl_getm_bin = "/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/install_gcc9_v4/bin/getm_cartesian"
    
    cmd = f"cd {wsl_case_dir} && {wsl_getm_bin}"
    
    result = subprocess.run(
        ["wsl", "-e", "bash", "-c", cmd],
        capture_output=True,
        text=True,
        timeout=3600
    )
    
    elapsed = time.time() - start_time
    
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"=== {sim_name} ===\n\n")
        f.write("=== STDOUT ===\n")
        f.write(result.stdout)
        f.write("\n=== STDERR ===\n")
        f.write(result.stderr)
    
    if result.returncode != 0:
        print(f"  FAILED ({elapsed:.1f}s)")
        for line in (result.stdout + result.stderr).split('\n'):
            if 'FATAL' in line.upper() or 'ERROR' in line.upper():
                print(f"  {line.strip()}")
        return False
    
    print(f"  OK ({elapsed:.1f}s)")
    
    # Count variables
    try:
        import netCDF4 as nc
        ds = nc.Dataset(os.path.join(CASE_DIR, "LUOMAHU_WET.3d.nc"), 'r')
        n_vars = len(ds.variables)
        ds.close()
        print(f"  Variables: {n_vars}")
    except:
        pass
    
    return True

def main():
    print("=" * 60)
    print("Testing Full Food Web (without fish)")
    print("=" * 60)
    
    # Load base config
    with open(BASE_FABM, 'r') as f:
        config = yaml.safe_load(f)
    
    print(f"\nBase config has {len(config['instances'])} instances")
    print(f"Instances: {', '.join(config['instances'].keys())}")
    
    # Fix config
    print("\nFixing config...")
    config = fix_config(config)
    print(f"Fixed config has {len(config['instances'])} instances")
    print(f"Instances: {', '.join(config['instances'].keys())}")
    
    # Save temp config
    temp_path = os.path.join(WORK_DIR, "fabm_no_fish.yaml")
    with open(temp_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    # Copy to case dir
    subprocess.run(
        ["wsl", "-e", "bash", "-c", 
         f"cp /mnt/c/Users/dinod/Desktop/GETM-FABM-WET/fabm_no_fish.yaml /mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/luomahu_case/fabm.yaml && echo 'Copied'"],
        capture_output=True
    )
    
    # Run simulation
    print("\nRunning simulation...")
    success = run_simulation("full_foodweb_no_fish", days=10)
    
    if success:
        print("\n" + "=" * 60)
        print("Full food web (no fish) test PASSED!")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("Full food web test FAILED!")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
