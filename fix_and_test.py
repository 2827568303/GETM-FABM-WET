#!/usr/bin/env python3
"""Fix all missing _PV couplings in fabm config."""
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
    """Fix all known issues in fabm config."""
    instances = config['instances']
    
    # List of modules that need POM_PV and DOM_PV couplings
    # Based on wet/src code: phytoplankton, zoobenthos, macrophytes all need these
    
    pv_couplings = [
        ('POM_DW_pool_sediment_PV', 'POM/sDS_PV'),
        ('POM_N_pool_sediment_PV', 'POM/sNS_PV'),
        ('POM_P_pool_sediment_PV', 'POM/sPS_PV'),
        ('POM_C_pool_sediment_PV', 'POM/sCS_PV'),
        ('DOM_DW_pool_sediment_PV', 'DOM/sDS_PV'),
        ('DOM_N_pool_sediment_PV', 'DOM/sNS_PV'),
        ('DOM_P_pool_sediment_PV', 'DOM/sPS_PV'),
        ('DOM_C_pool_sediment_PV', 'DOM/sCS_PV'),
    ]
    
    modules_to_fix = []
    
    # Check each module for _PV dependencies
    for name, inst in instances.items():
        model = inst.get('model', '')
        if model in ['wet/phytoplankton', 'wet/zoobenthos', 'wet/macrophytes']:
            modules_to_fix.append(name)
    
    print(f"Modules needing _PV couplings: {', '.join(modules_to_fix)}")
    
    for name in modules_to_fix:
        inst = instances[name]
        coupling = inst.setdefault('coupling', {})
        added = 0
        for var, target in pv_couplings:
            if var not in coupling:
                coupling[var] = target
                added += 1
        if added > 0:
            print(f"  Added {added} _PV couplings to {name}")
    
    # Remove fish modules for now
    fish_modules = [k for k in instances.keys() if 'Fish' in k or 'fish' in k]
    for fm in fish_modules:
        del instances[fm]
        print(f"  Removed fish module: {fm}")
    
    return config

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
        print(f"  Variables: {len(ds.variables)}")
        ds.close()
    except:
        pass
    
    return True

def main():
    print("=" * 60)
    print("Fixing and Testing Full Food Web")
    print("=" * 60)
    
    with open(BASE_FABM, 'r') as f:
        config = yaml.safe_load(f)
    
    print(f"\nBase instances: {len(config['instances'])}")
    
    print("\nFixing config...")
    config = fix_config(config)
    print(f"Fixed instances: {len(config['instances'])}")
    
    # Save
    temp_path = os.path.join(WORK_DIR, "fabm_fixed2.yaml")
    with open(temp_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    # Copy to case dir
    subprocess.run(
        ["wsl", "-e", "bash", "-c", 
         f"cp /mnt/c/Users/dinod/Desktop/GETM-FABM-WET/fabm_fixed2.yaml /mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/luomahu_case/fabm.yaml && echo OK"],
        capture_output=True
    )
    
    print("\nRunning 10-day simulation...")
    success = run_simulation("full_foodweb_fixed2", days=10)
    
    if success:
        print("\n" + "=" * 60)
        print("SUCCESS! Full food web (no fish) works!")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("FAILED - check logs for details")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
