#!/usr/bin/env python3
"""Test with lake_bryrup config as base."""
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
    """Run a simulation and capture output."""
    os.makedirs(LOG_DIR, exist_ok=True)
    
    log_file = os.path.join(LOG_DIR, f"{sim_name}.log")
    
    # Update getm.inp
    inp_file = os.path.join(CASE_DIR, "getm.inp")
    with open(inp_file, 'r') as f:
        content = f.read()
    
    start = datetime(2020, 1, 1)
    stop = start + timedelta(days=days)
    stop_str = stop.strftime('%Y-%m-%d %H:%M:%S')
    
    content_new = re.sub(r"stop\s*=\s*'[^']*'", f"stop = '{stop_str}'", content)
    with open(inp_file, 'w') as f:
        f.write(content_new)
    
    # Run GETM
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
        errors = []
        for line in (result.stdout + result.stderr).split('\n'):
            if 'FATAL' in line.upper() or 'ERROR' in line.upper():
                errors.append(line.strip())
        for e in errors[:5]:
            print(f"  {e}")
        return False
    
    print(f"  OK ({elapsed:.1f}s)")
    
    try:
        import netCDF4 as nc
        ds = nc.Dataset(os.path.join(CASE_DIR, "LUOMAHU_WET.3d.nc"), 'r')
        n_vars = len(ds.variables)
        print(f"  Variables: {n_vars}")
        ds.close()
    except:
        pass
    
    return True

def main():
    print("=" * 60)
    print("Testing with Lake Bryrup config")
    print("=" * 60)
    
    # Copy bryrup config
    result = subprocess.run(
        ["wsl", "-e", "bash", "-c", 
         f"cp /mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/wet/testcases/lake_bryrup_denmark/fabm.yaml /mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/luomahu_case/fabm.yaml && echo OK"],
        capture_output=True, text=True
    )
    print("Copied lake_bryrup_denmark fabm.yaml")
    
    # Load and show instances
    with open(BRYRUP_FABM, 'r') as f:
        config = yaml.safe_load(f)
    
    instances = config.get('instances', config)
    print(f"Instances: {len(instances)}")
    for name, inst in instances.items():
        model = inst.get('model', 'unknown')
        print(f"  {name}: {model}")
    
    # Run test
    print("\nRunning 3-day test...")
    success = run_simulation("bryrup_config_test", days=3)
    
    if success:
        print("\nSUCCESS!")
    else:
        print("\nFAILED")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
