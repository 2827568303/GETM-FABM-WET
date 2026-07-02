#!/usr/bin/env python3
"""Build up FABM config incrementally and test each step."""
import subprocess
import os
import sys
import time
import shutil
from datetime import datetime, timedelta
import re

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
CASE_DIR = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\luomahu_case"
BASE_FABM = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\wet\testcases\fabm-wet.yaml"
GETM_BIN = r"install_gcc9_v4\bin\getm_cartesian.exe"
LOG_DIR = os.path.join(r"C:\Users\dinod\Desktop\GETM-FABM-PCLake", "run_logs")

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
        # Find fatal error
        for line in (result.stdout + result.stderr).split('\n'):
            if 'FATAL' in line.upper() or 'ERROR' in line.upper():
                print(f"  {line.strip()}")
        return False
    
    print(f"  OK ({elapsed:.1f}s)")
    return True

def create_minimal_config():
    """Create minimal config with only abiotic_water."""
    import yaml
    
    with open(BASE_FABM, 'r') as f:
        config = yaml.safe_load(f)
    
    instances = config.get('instances', {})
    
    # Keep only abiotic_water
    keep = ['abiotic_water']
    new_instances = {k: v for k, v in instances.items() if k in keep}
    
    config['instances'] = new_instances
    
    return config

def save_config(config, path):
    """Save config to YAML file."""
    import yaml
    
    with open(path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

def test_step(step_name, config):
    """Test a configuration step."""
    print(f"\nStep: {step_name}")
    
    fabm_path = os.path.join(CASE_DIR, "fabm.yaml")
    save_config(config, fabm_path)
    
    # Copy to case dir via WSL
    subprocess.run(
        ["wsl", "-e", "bash", "-c", 
         f"cp /mnt/c/Users/dinod/Desktop/GETM-FABM-WET/fabm_temp.yaml /mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/luomahu_case/fabm.yaml"],
        capture_output=True
    )
    
    return run_simulation(step_name, days=3)

def main():
    import yaml
    
    print("=" * 60)
    print("Incremental FABM-WET Configuration Testing")
    print("=" * 60)
    
    # Load base config
    with open(BASE_FABM, 'r') as f:
        base_config = yaml.safe_load(f)
    
    instances = base_config.get('instances', {})
    print(f"Base config has {len(instances)} instances")
    print(f"Instances: {', '.join(instances.keys())}")
    
    # Test step by step - let's first see what the error is with macrophytes
    # Let's try without macrophytes first
    print("\n--- Testing without macrophytes ---")
    config_no_macro = {'instances': {}}
    for name, inst in instances.items():
        if name != 'macrophytes':
            config_no_macro['instances'][name] = inst
    
    fabm_path = os.path.join(WORK_DIR, "fabm_temp.yaml")
    save_config(config_no_macro, fabm_path)
    
    # Copy via WSL
    subprocess.run(
        ["wsl", "-e", "bash", "-c", 
         f"cp /mnt/c/Users/dinod/Desktop/GETM-FABM-WET/fabm_temp.yaml /mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/luomahu_case/fabm.yaml"],
        capture_output=True
    )
    
    success = run_simulation("step_no_macrophytes", days=3)
    
    if success:
        print("\nConfig works without macrophytes!")
    else:
        print("\nStill failing without macrophytes...")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
