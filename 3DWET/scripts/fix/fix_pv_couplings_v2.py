#!/usr/bin/env python3
"""Fix _PV (pelagic mirror) variable couplings by matching dependency names."""
import yaml
import os
import sys
import re

INPUT_YAML = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\wet\testcases\fabm-wet.yaml"
OUTPUT_YAML = r"C:\Users\dinod\Desktop\GETM-FABM-WET\fabm_full_fixed_pv.yaml"

# OM pool modules that have _PV variables
OM_POOL_MODULES = ['POM', 'DOM', 'humus']

# Mapping of dependency name patterns to target variables
# Pattern: (pool_name_prefix, pool_variable_suffix) -> target_module/target_variable
# e.g., "POM_DW_pool_sediment_PV" -> POM/sDS_PV
#       "DOM_N_pool_sediment_PV" -> DOM/sNS_PV
#       "humus_DW_in_deep_sediment_PV" -> humus/sDS_PV

def infer_pv_couplings(dep_name):
    """Try to infer the target variable for a _PV dependency."""
    # Pattern 1: {POOL}_{nutrient}_pool_sediment_PV (e.g., POM_DW_pool_sediment_PV)
    for pool in OM_POOL_MODULES:
        for nutrient, suffix in [('DW', 'sDS_PV'), ('N', 'sNS_PV'), ('P', 'sPS_PV'), ('C', 'sCS_PV'), ('Si', 'sSiPaS_PV')]:
            pattern = f'{pool}_{nutrient}_pool_sediment_PV'
            if dep_name == pattern:
                return f'{pool}/{suffix}'
    
    # Pattern 2: {POOL}_{nutrient}_in_deep_sediment_PV (e.g., humus_DW_in_deep_sediment_PV)
    for pool in OM_POOL_MODULES:
        for nutrient, suffix in [('DW', 'sDS_PV'), ('N', 'sNS_PV'), ('P', 'sPS_PV'), ('C', 'sCS_PV')]:
            pattern = f'{pool}_{nutrient}_in_deep_sediment_PV'
            if dep_name == pattern:
                return f'{pool}/{suffix}'
    
    return None

def main():
    with open(INPUT_YAML, 'r') as f:
        config = yaml.safe_load(f)
    
    instances = config['instances']
    
    # First, find all modules that have _PV state variables (provide them)
    pv_providers = {}  # {module_name: [list of _PV variable names]}
    for name, inst in instances.items():
        # Check initialization section for _PV variables
        init = inst.get('initialization', {})
        pv_vars = [k for k in init.keys() if k.endswith('_PV')]
        if pv_vars:
            pv_providers[name] = pv_vars
    
    print("Modules with _PV state variables:")
    for name, vars in pv_providers.items():
        print(f"  {name}: {vars}")
    
    # Now go through each module's coupling and see what _PV dependencies are missing
    total_added = 0
    for name, inst in instances.items():
        coupling = inst.get('coupling', {})
        
        # We can't easily know all dependencies from the yaml, so let's look at what's already there
        # and add similar patterns that are missing.
        # Actually, let's just try to be comprehensive - add all likely _PV couplings.
        
        # Find which pool modules this module already couples to
        pool_modules_used = set()
        for dep, target in coupling.items():
            if '_pool_sediment' in dep or '_in_deep_sediment' in dep:
                for pool in OM_POOL_MODULES:
                    if dep.startswith(pool + '_'):
                        pool_modules_used.add(pool)
        
        # If this module couples to POM_DW_pool_sediment, it probably also needs POM_DW_pool_sediment_PV
        # Let's add _PV versions for all existing non-PV pool couplings
        pv_to_add = {}
        for dep, target in list(coupling.items()):
            # Skip if already a _PV variable
            if dep.endswith('_PV'):
                continue
            
            # Check if this is a pool sediment coupling
            pv_target = infer_pv_couplings(dep + '_PV')
            if pv_target:
                pv_dep = dep + '_PV'
                if pv_dep not in coupling:
                    pv_to_add[pv_dep] = pv_target
        
        if pv_to_add:
            print(f"\nAdding {len(pv_to_add)} _PV couplings to {name}:")
            for dep, target in pv_to_add.items():
                print(f"  {dep}: {target}")
                coupling[dep] = target
                total_added += 1
    
    print(f"\nTotal _PV couplings added: {total_added}")
    
    # Also fix fish module parameter names
    fish_modules = [name for name in instances.keys() if name.endswith('Fish') or 'fish' in name.lower()]
    for name in fish_modules:
        inst = instances[name]
        params = inst.get('parameters', {})
        
        # Fix prey_suffix -> PLANprey_suffix
        for key in list(params.keys()):
            if key.startswith('prey_suffix') and key[11:].isdigit():
                num = key[11:]
                new_key = f'PLANprey_suffix{num}'
                params[new_key] = params.pop(key)
                print(f"Renamed {name}/{key} -> {new_key}")
    
    with open(OUTPUT_YAML, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    print(f"\nFixed config saved to: {OUTPUT_YAML}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
