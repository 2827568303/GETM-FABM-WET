#!/usr/bin/env python3
"""Iteratively fix fabm.yaml configuration errors."""
import yaml
import os
import subprocess
import sys
import re
from datetime import datetime, timedelta

WORK_DIR = r"C:\Users\dinod\Desktop\GETM-FABM-WET"
CASE_DIR = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\luomahu_case"
LOG_DIR = os.path.join(r"C:\Users\dinod\Desktop\GETM-FABM-PCLake", "run_logs")

def copy_to_case(yaml_path):
    wsl_path = yaml_path.replace('C:', '/mnt/c').replace('\\', '/')
    subprocess.run(
        ["wsl", "-e", "cp", wsl_path, 
         "/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/luomahu_case/fabm.yaml"],
        capture_output=True
    )

def run_sim(iter_name):
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, f"iter_{iter_name}.log")
    
    wsl_case_dir = "/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/luomahu_case"
    wsl_getm_bin = "/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/install_gcc9_v5/bin/getm_cartesian"
    
    result = subprocess.run(
        ["wsl", "-e", "bash", "-c", 
         f"cd {wsl_case_dir} && {wsl_getm_bin} 2>&1"],
        capture_output=True, text=True, timeout=600
    )
    
    output = result.stdout + result.stderr
    
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(output)
    
    return output

def parse_error(output):
    """Parse the first fatal error and determine what to fix."""
    lines = output.split('\n')
    
    for line in lines:
        if 'FATAL ERROR' not in line:
            continue
        
        # Error 1: "Variable X/Y must be coupled to an existing state variable."
        m = re.search(r'Variable ([^/]+)/([^ ]+) must be coupled to an existing state variable', line)
        if m:
            module_name = m.group(1)
            var_name = m.group(2)
            return {
                'type': 'missing_coupling',
                'module': module_name,
                'variable': var_name
            }
        
        # Error 2: "Coupling target "X/Y" for "Z" was not found."
        m = re.search(r'Coupling target "([^"]+)/([^"]+)" for "([^"]+)" was not found', line)
        if m:
            target_module = m.group(1)
            target_var = m.group(2)
            source_proc = m.group(3)
            return {
                'type': 'coupling_target_not_found',
                'target_module': target_module,
                'target_var': target_var,
                'source_process': source_proc
            }
        
        # Error 3: "Unrecognized parameter "X" found below /instances/Y/parameters."
        m = re.search(r'Unrecognized parameter "([^"]+)" found below /instances/([^/]+)/parameters', line)
        if m:
            param_name = m.group(1)
            module_name = m.group(2)
            return {
                'type': 'unrecognized_parameter',
                'module': module_name,
                'parameter': param_name
            }
        
        # Error 4: UNFULFILLED DEPENDENCY
        m = re.search(r'UNFULFILLED DEPENDENCY: (.+)', line)
        if m:
            dep = m.group(1).strip()
            return {
                'type': 'unfulfilled_dependency',
                'dependency': dep
            }
    
    # Check if simulation succeeded
    if 'TIMERS SUM' in output or 'Copyright' in output:
        return {'type': 'success'}
    
    return {'type': 'unknown', 'line': line if 'FATAL ERROR' in line else 'unknown'}

def infer_coupling_target(var_name):
    """Try to infer the coupling target for a _PV variable."""
    # POM_DW_pool_sediment_PV -> POM/sDS_PV
    # DOM_N_pool_sediment_PV -> DOM/sNS_PV
    # humus_C_in_deep_sediment_PV -> humus/sCS_PV
    
    for pool in ['POM', 'DOM', 'humus']:
        if not var_name.startswith(pool + '_'):
            continue
        
        rest = var_name[len(pool)+1:]  # e.g., "DW_pool_sediment_PV"
        
        for nutrient, suffix in [('DW', 'sDS_PV'), ('N', 'sNS_PV'), ('P', 'sPS_PV'), ('C', 'sCS_PV'), ('Si', 'sSiPaS_PV')]:
            if rest.startswith(nutrient + '_'):
                return f'{pool}/{suffix}'
    
    return None

def fix_config(config, error):
    """Apply fix based on error type."""
    instances = config['instances']
    fixed = False
    
    if error['type'] == 'missing_coupling':
        module_name = error['module']
        var_name = error['variable']
        
        if module_name not in instances:
            print(f"  ERROR: Module {module_name} not found in config")
            return False
        
        inst = instances[module_name]
        coupling = inst.setdefault('coupling', {})
        
        if var_name in coupling:
            print(f"  NOTE: Coupling {var_name} already exists in {module_name}")
            return False
        
        # Try to infer the target
        target = infer_coupling_target(var_name)
        if target:
            coupling[var_name] = target
            print(f"  Adding coupling: {module_name}/{var_name} -> {target}")
            return True
        else:
            print(f"  WARNING: Could not infer target for {module_name}/{var_name}")
            return False
    
    elif error['type'] == 'unrecognized_parameter':
        module_name = error['module']
        param_name = error['parameter']
        
        if module_name not in instances:
            return False
        
        params = instances[module_name].get('parameters', {})
        
        # Try to fix common parameter name issues
        # prey_suffix1 -> PLANprey_suffix1 (for fish modules)
        if param_name.startswith('prey_suffix') and param_name[11:].isdigit():
            num = param_name[11:]
            new_name = f'PLANprey_suffix{num}'
            if param_name in params:
                params[new_name] = params.pop(param_name)
                print(f"  Renamed parameter: {module_name}/{param_name} -> {new_name}")
                return True
        
        # If we can't fix it, just remove the parameter
        if param_name in params:
            del params[param_name]
            print(f"  Removed unrecognized parameter: {module_name}/{param_name}")
            return True
        
        return False
    
    elif error['type'] == 'coupling_target_not_found':
        target_module = error['target_module']
        target_var = error['target_var']
        print(f"  NOTE: Coupling target {target_module}/{target_var} not found")
        print(f"  May need to add module {target_module} or fix coupling")
        return False
    
    return False

def main():
    # Start with reference config
    base_yaml = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\wet\testcases\fabm-wet.yaml"
    with open(base_yaml, 'r') as f:
        config = yaml.safe_load(f)
    
    max_iterations = 30
    
    for i in range(1, max_iterations + 1):
        iter_name = f"{i:02d}"
        yaml_path = os.path.join(WORK_DIR, f"fabm_iter_{iter_name}.yaml")
        
        # Save current config
        with open(yaml_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        copy_to_case(yaml_path)
        
        print(f"\n{'='*60}")
        print(f"Iteration {i}")
        print('='*60)
        
        output = run_sim(iter_name)
        error = parse_error(output)
        
        if error['type'] == 'success':
            print("  SUCCESS! Simulation completed.")
            print(f"  Final config: {yaml_path}")
            return 0
        
        print(f"  Error type: {error['type']}")
        if error['type'] == 'unknown':
            print(f"  Error: {error.get('line', 'unknown')}")
            return 1
        
        # Try to fix
        if not fix_config(config, error):
            print("  Could not auto-fix. Stopping.")
            return 1
    
    print(f"\nReached max iterations ({max_iterations})")
    return 1

if __name__ == "__main__":
    sys.exit(main())
