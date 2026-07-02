#!/usr/bin/env python3
"""Test with full WET template config, iteratively fixing issues."""
import yaml
import os
import subprocess
import sys
import re
import shutil
from datetime import datetime, timedelta

WORK_DIR = r"C:\Users\dinod\Desktop\GETM-FABM-WET"
CASE_DIR = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\luomahu_case"
BASE_FABM = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\wet\testcases\fabm-wet.yaml"
LOG_DIR = os.path.join(r"C:\Users\dinod\Desktop\GETM-FABM-PCLake", "run_logs")

def load_base_config():
    with open(BASE_FABM, 'r') as f:
        return yaml.safe_load(f)

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
    log_file = os.path.join(LOG_DIR, f"full_{sim_name}.log")
    
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
    
    coupling_errors = []
    for line in output.split('\n'):
        if 'Coupling target' in line and 'was not found' in line:
            coupling_errors.append(line.strip())
    
    fatal_error = None
    for line in output.split('\n'):
        if 'FATAL ERROR' in line.upper():
            fatal_error = line.strip()
            break
    
    ran_successfully = (result.returncode == 0 and not fatal_error and 
                        ('Copyright' in output or 'TIMERS SUM' in output))
    
    return ran_successfully, fatal_error, unfulfilled, coupling_errors, log_file

def main():
    print("=" * 60)
    print("Full Food Web Configuration Testing")
    print("=" * 60)
    
    # Start with the full WET template
    base_config = load_base_config()
    
    # Make a copy and apply known fixes
    config = {'instances': {}}
    for name, inst in base_config['instances'].items():
        config['instances'][name] = dict(inst)
    
    # Fix 1: Disable Si modules and couplings (we don't have oSi module)
    # Actually, let's see what modules reference Si first
    
    # Let's try to run and see what errors we get
    iteration = 0
    max_iterations = 20
    
    while iteration < max_iterations:
        iteration += 1
        sim_name = f"iter{iteration:02d}"
        
        # Save current config
        yaml_path = os.path.join(WORK_DIR, f"fabm_full_{sim_name}.yaml")
        with open(yaml_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        copy_config_to_case(yaml_path)
        
        print(f"\n{'='*60}")
        print(f"Iteration {iteration}: Testing...")
        print('='*60)
        
        success, fatal, unfulfilled, coupling_errs, log_file = run_simulation(sim_name, days=2)
        
        if success:
            print(f"  SUCCESS! Configuration is working.")
            print(f"  Final config: {yaml_path}")
            print(f"  Log: {log_file}")
            return 0
        
        print(f"  Failed.")
        if fatal: print(f"  Fatal: {fatal}")
        if unfulfilled: print(f"  Unfulfilled deps: {unfulfilled[:10]}")
        if coupling_errs: print(f"  Coupling errors: {coupling_errs[:5]}")
        
        # Analyze and fix
        fixed = False
        
        # Fix coupling errors
        for err in coupling_errs:
            # Parse: "Coupling target "X/Y" for "Z" was not found."
            m = re.search(r'Coupling target "([^"]+)/([^"]+)" for "([^"]+)" was not found', err)
            if m:
                target_model = m.group(1)
                target_var = m.group(2)
                source_proc = m.group(3)
                
                print(f"  -> Missing coupling: {target_model}/{target_var} (from {source_proc})")
                
                # Check if target model exists
                if target_model not in config['instances']:
                    print(f"     Model {target_model} not in config.")
                    # Could add the module or disable the coupling
                else:
                    print(f"     Model {target_model} exists but variable {target_var} missing.")
        
        if not fixed:
            print(f"\n  Could not auto-fix. See log: {log_file}")
            return 1
    
    print(f"\nReached max iterations ({max_iterations})")
    return 1

if __name__ == "__main__":
    sys.exit(main())
