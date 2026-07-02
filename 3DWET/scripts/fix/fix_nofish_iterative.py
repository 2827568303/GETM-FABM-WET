#!/usr/bin/env python3
"""Iteratively fix food web config WITHOUT macrophytes."""
import yaml
import os
import subprocess
import sys
import re

WORK_DIR = r"C:\Users\dinod\Desktop\GETM-FABM-WET"
CASE_DIR = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\luomahu_case"
LOG_DIR = os.path.join(r"C:\Users\dinod\Desktop\GETM-FABM-PCLake", "run_logs")
BASE_YAML = r"C:\Users\dinod\Desktop\GETM-FABM-WET\fabm_pvfix_25.yaml"

def copy_to_case(yaml_path):
    wsl_path = yaml_path.replace('C:', '/mnt/c').replace('\\', '/')
    subprocess.run(["wsl", "-e", "cp", wsl_path, 
                    "/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/luomahu_case/fabm.yaml"],
                   capture_output=True)

def run_sim(iter_name):
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, f"nofish_{iter_name}.log")
    result = subprocess.run(
        ["wsl", "-e", "bash", "-c", 
         f"cd /mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/luomahu_case && "
         f"/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/install_gcc9_v5/bin/getm_cartesian 2>&1"],
        capture_output=True, text=True, timeout=600
    )
    output = result.stdout + result.stderr
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(output)
    return output

def get_first_error(output):
    for line in output.split('\n'):
        if 'FATAL ERROR' not in line and 'Program received' not in line:
            continue
        
        # Segfault
        if 'SIGSEGV' in line or 'Segmentation fault' in line:
            return {'type': 'segfault'}
        
        # "Variable X/Y must be coupled to an existing state variable."
        m = re.search(r'Variable ([^/]+)/([^ ]+) must be coupled to an existing state variable', line)
        if m:
            return {'type': 'missing_coupling', 'module': m.group(1), 'variable': m.group(2)}
        
        # model X does not contain variable "Y" mentioned in coupling section
        m = re.search(r'model ([^ ]+) does not contain variable "([^"]+)" mentioned in coupling', line)
        if m:
            return {'type': 'extra_coupling', 'module': m.group(1), 'variable': m.group(2)}
        
        # Coupling target "X/Y" for "Z" was not found
        m = re.search(r'Coupling target "([^"]+)" for "([^"]+)" was not found', line)
        if m:
            return {'type': 'coupling_target_not_found', 'target': m.group(1), 'source': m.group(2), 'line': line}
    
    # Check for success
    if 'TIMERS SUM' in output or 'Copyright' in output:
        return {'type': 'success'}
    
    # Find any FATAL ERROR
    for line in output.split('\n'):
        if 'FATAL ERROR' in line:
            return {'type': 'unknown_fatal', 'line': line.strip()}
    
    return {'type': 'unknown'}

def infer_pv_target(var_name):
    for pool in ['POM', 'DOM', 'humus']:
        if not var_name.startswith(pool + '_'):
            continue
        rest = var_name[len(pool)+1:]
        for nutrient, suffix in [('DW', 'sDS_PV'), ('N', 'sNS_PV'), ('P', 'sPS_PV'), ('C', 'sCS_PV'), ('Si', 'sSiPaS_PV')]:
            if rest.startswith(nutrient + '_'):
                return f'{pool}/{suffix}'
    return None

def main():
    with open(BASE_YAML, 'r') as f:
        config = yaml.safe_load(f)
    
    instances = config['instances']
    
    # Remove macrophytes (causes segfault)
    if 'macrophytes' in instances:
        del instances['macrophytes']
        print("Removed macrophytes (causes segfault)")
    
    # Also remove fish modules if present
    for fm in ['JuFish', 'AdFish', 'PiscFish']:
        if fm in instances:
            del instances[fm]
    
    for i in range(1, 80):
        iter_name = f"{i:02d}"
        yaml_path = os.path.join(WORK_DIR, f"fabm_nofish_{iter_name}.yaml")
        
        with open(yaml_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        copy_to_case(yaml_path)
        
        print(f"\nIteration {i}...", end=" ")
        output = run_sim(iter_name)
        error = get_first_error(output)
        
        if error['type'] == 'success':
            print("SUCCESS!")
            print(f"  Final config: {yaml_path}")
            return 0
        
        if error['type'] == 'segfault':
            print("SEGFAULT!")
            return 1
        
        if error['type'] == 'missing_coupling':
            mod = error['module']
            var = error['variable']
            target = infer_pv_target(var)
            if target and mod in instances:
                coupling = instances[mod].setdefault('coupling', {})
                coupling[var] = target
                print(f"Added: {mod}/{var} -> {target}")
                continue
            else:
                print(f"Can't fix missing coupling: {mod}/{var}")
                return 1
        
        elif error['type'] == 'extra_coupling':
            mod = error['module']
            var = error['variable']
            if mod in instances and 'coupling' in instances[mod]:
                if var in instances[mod]['coupling']:
                    del instances[mod]['coupling'][var]
                    print(f"Removed extra: {mod}/{var}")
                    continue
            print(f"Can't fix extra coupling: {mod}/{var}")
            return 1
        
        elif error['type'] == 'coupling_target_not_found':
            target = error['target']
            source = error['source']
            print(f"Coupling target not found: {target} (from {source})")
            print(f"  Full line: {error.get('line', 'unknown')}")
            return 1
        
        else:
            print(f"Unknown error: {error}")
            return 1
    
    print("Reached max iterations")
    return 1

if __name__ == "__main__":
    sys.exit(main())
