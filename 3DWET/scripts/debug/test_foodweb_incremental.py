#!/usr/bin/env python3
"""Incrementally build up the full food web configuration and test each step."""
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
    log_file = os.path.join(LOG_DIR, f"foodweb_{sim_name}.log")
    
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
    
    return ran_successfully, fatal_error, unfulfilled, coupling_errors

def make_config(modules, base_config):
    all_instances = base_config['instances']
    config = {'instances': {}}
    for m in modules:
        if m in all_instances:
            config['instances'][m] = all_instances[m]
    return config

def main():
    print("=" * 60)
    print("Incremental Food Web Configuration Testing")
    print("=" * 60)
    
    base_config = load_base_config()
    all_instances = base_config['instances']
    
    test_steps = [
        ("step1_core", ['abiotic_water', 'abiotic_sediment', 'bot_pel_interface', 'POM', 'DOM', 'humus']),
        ("step2_phytoplankton", ['abiotic_water', 'abiotic_sediment', 'bot_pel_interface', 'POM', 'DOM', 'humus', 'cyanobacteria', 'diatoms', 'greens']),
        ("step3_sediment", ['abiotic_water', 'abiotic_sediment', 'bot_pel_interface', 'POM', 'DOM', 'humus', 'cyanobacteria', 'diatoms', 'greens', 'sediment_exchange', 'burial']),
        ("step4_zooplankton", ['abiotic_water', 'abiotic_sediment', 'bot_pel_interface', 'POM', 'DOM', 'humus', 'cyanobacteria', 'diatoms', 'greens', 'sediment_exchange', 'burial', 'cladocerans', 'copepods']),
        ("step5_zoobenthos", ['abiotic_water', 'abiotic_sediment', 'bot_pel_interface', 'POM', 'DOM', 'humus', 'cyanobacteria', 'diatoms', 'greens', 'sediment_exchange', 'burial', 'cladocerans', 'copepods', 'zoobenthos']),
        ("step6_macrophytes", ['abiotic_water', 'abiotic_sediment', 'bot_pel_interface', 'POM', 'DOM', 'humus', 'cyanobacteria', 'diatoms', 'greens', 'sediment_exchange', 'burial', 'cladocerans', 'copepods', 'zoobenthos', 'macrophytes']),
    ]
    
    for step_name, modules in test_steps:
        print(f"\n{'='*60}")
        print(f"Testing: {step_name}")
        print(f"Modules: {', '.join(modules)}")
        print('='*60)
        
        config = make_config(modules, base_config)
        
        # Fix known issues
        # Disable Si couplings (we don't have oSi module)
        for inst_name, inst in config['instances'].items():
            if 'parameters' in inst:
                params = inst['parameters']
                for key in list(params.keys()):
                    if key.startswith('lSi') or 'Silicon' in key or 'silicon' in key:
                        params[key] = False
        
        # Add _PV couplings for modules that need them
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
        
        modules_with_pv_needs = ['zoobenthos', 'macrophytes', 'burial', 'sediment_exchange',
                                  'cyanobacteria', 'diatoms', 'greens', 'cladocerans', 'copepods']
        for name in modules_with_pv_needs:
            if name in config['instances']:
                inst = config['instances'][name]
                coupling = inst.setdefault('coupling', {})
                if name == 'burial':
                    for var, target in humus_pv.items():
                        coupling[var] = target
                for var, target in pv_couplings.items():
                    coupling[var] = target
        
        path = os.path.join(WORK_DIR, f"fabm_{step_name}.yaml")
        with open(path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        copy_config_to_case(path)
        
        success, fatal, unfulfilled, coupling_errs = run_simulation(step_name, days=2)
        
        print(f"  Success: {success}")
        if fatal: print(f"  Fatal: {fatal}")
        if unfulfilled: print(f"  Unfulfilled deps ({len(unfulfilled)}): {unfulfilled[:10]}")
        if coupling_errs: print(f"  Coupling errors ({len(coupling_errs)}): {coupling_errs[:5]}")
        
        if not success and not unfulfilled and not coupling_errs:
            # Maybe it ran but with state variable issues - check if it's a real failure
            log_file = os.path.join(LOG_DIR, f"foodweb_{step_name}.log")
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
            if 'State variable values are invalid' in log_content:
                print("  NOTE: State variable invalid error - may need initial conditions")
        
        if not success:
            print(f"\n  Step {step_name} failed. Stopping.")
            print(f"  See log: {os.path.join(LOG_DIR, f'foodweb_{step_name}.log')}")
            return 1
    
    print("\n" + "=" * 60)
    print("ALL STEPS PASSED!")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())
