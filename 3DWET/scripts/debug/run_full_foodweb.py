#!/usr/bin/env python3
"""Run full food web simulation test."""
import subprocess
import os
import sys
import time
from datetime import datetime, timedelta

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
CASE_DIR = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\luomahu_case"
GETM_BIN = r"C:\Users\dinod\Desktop\GETM-FABM-WET\install_gcc9_v3\bin\getm_cartesian"
LOG_DIR = os.path.join(WORK_DIR, "run_logs")

def run_simulation(sim_name, days=30):
    """Run a simulation and capture output."""
    os.makedirs(LOG_DIR, exist_ok=True)
    
    log_file = os.path.join(LOG_DIR, f"{sim_name}.log")
    
    print(f"\n{'='*60}")
    print(f"Running simulation: {sim_name} ({days} days)")
    print(f"{'='*60}")
    
    # Update getm.inp with simulation duration
    inp_file = os.path.join(CASE_DIR, "getm.inp")
    
    with open(inp_file, 'r') as f:
        content = f.read()
    
    start = datetime(2020, 1, 1)
    stop = start + timedelta(days=days)
    stop_str = stop.strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"Start: 2020-01-01 00:00:00")
    print(f"Stop:  {stop_str}")
    
    import re
    content_new = re.sub(
        r"stop\s*=\s*'[^']*'",
        f"stop = '{stop_str}'",
        content
    )
    
    with open(inp_file, 'w') as f:
        f.write(content_new)
    
    # Run GETM
    print("\nStarting simulation...")
    start_time = time.time()
    
    wsl_case_dir = "/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/luomahu_case"
    wsl_getm_bin = "/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/install_gcc9_v3/bin/getm_cartesian"
    
    cmd = f"cd {wsl_case_dir} && {wsl_getm_bin} getm.inp"
    
    result = subprocess.run(
        ["wsl", "-e", "bash", "-c", cmd],
        capture_output=True,
        text=True,
        timeout=3600
    )
    
    elapsed = time.time() - start_time
    
    with open(log_file, 'w') as f:
        f.write("=== STDOUT ===\n")
        f.write(result.stdout)
        f.write("\n=== STDERR ===\n")
        f.write(result.stderr)
    
    print(f"\nSimulation completed in {elapsed:.1f} seconds")
    print(f"Return code: {result.returncode}")
    
    if result.returncode != 0:
        print("FAILED!")
        print("\nLast 80 lines of output:")
        lines = (result.stdout + result.stderr).split('\n')
        print('\n'.join(lines[-80:]))
        return False
    
    print("SUCCESS!")
    
    # Check output files
    print("\nOutput files:")
    for f in ['LUOMAHU_WET.2d.nc', 'LUOMAHU_WET.3d.nc']:
        fpath = os.path.join(CASE_DIR, f)
        if os.path.exists(fpath):
            size = os.path.getsize(fpath) / 1024 / 1024
            print(f"  {f}: {size:.2f} MB")
        else:
            print(f"  {f}: NOT FOUND")
    
    return True

def main():
    # Run 30-day test with full food web
    success = run_simulation("test_30d_full_foodweb", days=30)
    
    if success:
        print("\n" + "="*60)
        print("Full food web simulation test PASSED!")
        print("="*60)
        return 0
    else:
        print("\n" + "="*60)
        print("Full food web simulation test FAILED!")
        print("="*60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
