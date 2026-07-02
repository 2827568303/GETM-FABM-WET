#!/usr/bin/env python3
"""Fix all _PV couplings at once and test."""
import yaml
import os
import subprocess
import sys
import time
import re
from datetime import datetime, timedelta

WORK_DIR = r"C:\Users\dinod\Desktop\GETM-FABM-WET"
CASE_DIR = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\luomahu_case"
BASE_FABM = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\wet\testcases\fabm-wet.yaml"
LOG_DIR = os.path.join(r"C:\Users\dinod\Desktop\GETM-FABM-PCLake", "run_logs")

def copy_config_to_case(yaml_path):
    wsl_path = yaml_path.replace('C:', '/mnt/c').replace('\\', '/')
    result = subprocess.run(
        ["wsl", "-e", "bash", "-c", 
         f"cp {wsl_path} /mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/luomahu_case/fabm.yaml && echo OK"],
        capture_output=True, text=True
    )
    return result.returncode == 0

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
        capture_output=True, text=True, timeout=7200
    )
    
    elapsed = time.time() - start_time
    
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"=== {sim_name} ===\n\n=== STDOUT ===\n{result.stdout}\n=== STDERR ===\n{result.stderr}")
    
    output = result.stdout + result.stderr
    fatal_error = None
    for line in output.split('\n'):
        if 'FATAL ERROR' in line.upper():
            fatal_error = line.strip()
            break
    
    return result.returncode == 0, fatal_error, elapsed

def fix_all_pv_couplings(config):
    """Add all missing _PV couplings to all modules that need them."""
    instances = config['instances']
    
    # Standard _PV couplings needed by phytoplankton, zoobenthos, macrophytes
    pv_couplings = {
        # POM _PV
        'POM_DW_pool_sediment_PV': 'POM/sDS_PV',
        'POM_N_pool_sediment_PV': 'POM/sNS_PV',
        'POM_P_pool_sediment_PV': 'POM/sPS_PV',
        'POM_C_pool_sediment_PV': 'POM/sCS_PV',
        # DOM _PV
        'DOM_DW_pool_sediment_PV': 'DOM/sDS_PV',
        'DOM_N_pool_sediment_PV': 'DOM/sNS_PV',
        'DOM_P_pool_sediment_PV': 'DOM/sPS_PV',
        'DOM_C_pool_sediment_PV': 'DOM/sCS_PV',
    }
    
    # Modules that need these couplings (based on model type)
    modules_needing_pv = []
    for name, inst in instances.items():
        model = inst.get('model', '')
        if model in ['wet/phytoplankton', 'wet/zoobenthos', 'wet/macrophytes']:
            modules_needing_pv.append(name)
    
    print(f"Modules needing _PV couplings: {', '.join(modules_needing_pv)}")
    
    total_added = 0
    for name in modules_needing_pv:
        inst = instances[name]
        coupling = inst.setdefault('coupling', {})
        added = 0
        for var, target in pv_couplings.items():
            if var not in coupling:
                coupling[var] = target
                added += 1
        if added > 0:
            print(f"  {name}: added {added} _PV couplings")
            total_added += added
    
    # Also fix burial module - it needs humus _PV couplings
    if 'burial' in instances:
        burial = instances['burial']
        coupling = burial.setdefault('coupling', {})
        humus_pv = {
            'humus_DW_in_deep_sediment_PV': 'humus/sDS_PV',
            'humus_N_in_deep_sediment_PV': 'humus/sNS_PV',
            'humus_P_in_deep_sediment_PV': 'humus/sPS_PV',
            'humus_C_in_deep_sediment_PV': 'humus/sCS_PV',
        }
        added = 0
        for var, target in humus_pv.items():
            if var not in coupling:
                coupling[var] = target
                added += 1
        if added > 0:
            print(f"  burial: added {added} humus _PV couplings")
            total_added += added
        
        # Burial also needs POM and DOM _PV couplings for each POM/DOM group
        # Let's check nPOM and nDOM parameters
        params = burial.get('parameters', {})
        n_pom = params.get('nPOM', 2)  # default 2
        n_dom = params.get('nDOM', 1)  # default 1
        
        pom_pv = {}
        for i in range(1, n_pom + 1):
            pom_pv[f'POM_D_{i}_PV'] = f'POM/sDS_PV'  # might need different targets
            pom_pv[f'POM_N_{i}_PV'] = f'POM/sNS_PV'
            pom_pv[f'POM_P_{i}_PV'] = f'POM/sPS_PV'
            pom_pv[f'POM_C_{i}_PV'] = f'POM/sCS_PV'
        
        dom_pv = {}
        for i in range(1, n_dom + 1):
            dom_pv[f'DOM_D_{i}_PV'] = f'DOM/sDS_PV'
            dom_pv[f'DOM_N_{i}_PV'] = f'DOM/sNS_PV'
            dom_pv[f'DOM_P_{i}_PV'] = f'DOM/sPS_PV'
            dom_pv[f'DOM_C_{i}_PV'] = f'DOM/sCS_PV'
    
    # Remove fish modules
    fish_modules = [k for k in list(instances.keys()) if 'Fish' in k or 'fish' in k]
    for fm in fish_modules:
        del instances[fm]
        print(f"  Removed fish module: {fm}")
    
    print(f"\nTotal _PV couplings added: {total_added}")
    return config

def main():
    print("=" * 60)
    print("Fix All _PV Couplings At Once")
    print("=" * 60)
    
    with open(BASE_FABM, 'r') as f:
        config = yaml.safe_load(f)
    
    print(f"\nStarting instances: {len(config['instances'])}")
    
    config = fix_all_pv_couplings(config)
    
    print(f"\nFinal instances: {len(config['instances'])}")
    
    # Save
    config_path = os.path.join(WORK_DIR, "fabm_all_pv_fixed.yaml")
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    print(f"Config saved to: {config_path}")
    
    # Test
    print("\n--- Testing ---")
    copy_config_to_case(config_path)
    
    success, fatal_error, elapsed = run_simulation("all_pv_fixed", days=5)
    
    if success:
        print(f"\nSUCCESS! Simulation ran without errors ({elapsed:.1f}s)")
        
        try:
            import netCDF4 as nc
            ds = nc.Dataset(os.path.join(CASE_DIR, "LUOMAHU_WET.3d.nc"), 'r')
            print(f"Variables: {len(ds.variables)}")
            
            # List key food web variables
            print("\nKey food web variables:")
            key_terms = ['cyanobacteria', 'diatoms', 'greens', 'cladocerans', 
                        'copepods', 'zoobenthos', 'macrophytes', 'POM', 'DOM']
            for var in sorted(ds.variables.keys()):
                for term in key_terms:
                    if term.lower() in var.lower() and ('DW' in var or 'sD' in var):
                        print(f"  {var}")
                        break
            
            ds.close()
        except Exception as e:
            print(f"Could not read output: {e}")
        
        return 0
    else:
        print(f"\nFAILED: {fatal_error}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
