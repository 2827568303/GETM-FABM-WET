#!/usr/bin/env python3
"""Create a full food web config without fish modules."""
import yaml
import os
import sys

INPUT_YAML = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\wet\testcases\fabm-wet.yaml"
OUTPUT_YAML = r"C:\Users\dinod\Desktop\GETM-FABM-WET\fabm_foodweb_nofish.yaml"

PV_COUPLINGS = {
    'POM_DW_pool_sediment_PV': 'POM/sDS_PV',
    'POM_N_pool_sediment_PV': 'POM/sNS_PV',
    'POM_P_pool_sediment_PV': 'POM/sPS_PV',
    'POM_C_pool_sediment_PV': 'POM/sCS_PV',
    'DOM_DW_pool_sediment_PV': 'DOM/sDS_PV',
    'DOM_N_pool_sediment_PV': 'DOM/sNS_PV',
    'DOM_P_pool_sediment_PV': 'DOM/sPS_PV',
    'DOM_C_pool_sediment_PV': 'DOM/sCS_PV',
    'humus_DW_in_deep_sediment_PV': 'humus/sDS_PV',
    'humus_N_in_deep_sediment_PV': 'humus/sNS_PV',
    'humus_P_in_deep_sediment_PV': 'humus/sPS_PV',
    'humus_C_in_deep_sediment_PV': 'humus/sCS_PV',
}

MODULES_WITH_PV = [
    'macrophytes', 'zoobenthos', 'burial', 'sediment_exchange',
    'cyanobacteria', 'diatoms', 'greens', 'cladocerans', 'copepods',
]

FISH_MODULES = ['JuFish', 'AdFish', 'PiscFish']

def main():
    with open(INPUT_YAML, 'r') as f:
        config = yaml.safe_load(f)
    
    instances = config['instances']
    
    # Remove fish modules
    for fish_mod in FISH_MODULES:
        if fish_mod in instances:
            del instances[fish_mod]
            print(f"Removed fish module: {fish_mod}")
    
    # Fix Si parameters (disable Si tracking)
    for name, inst in instances.items():
        if 'parameters' in inst:
            params = inst['parameters']
            # Disable Si-related parameters
            for key in list(params.keys()):
                if key.startswith('lSi') and key[3:].isdigit():
                    params[key] = False
    
    # Add _PV couplings
    pv_count = 0
    for name in MODULES_WITH_PV:
        if name not in instances:
            continue
        inst = instances[name]
        coupling = inst.setdefault('coupling', {})
        for pv_var, target in PV_COUPLINGS.items():
            if pv_var not in coupling:
                coupling[pv_var] = target
                pv_count += 1
    
    print(f"Added {pv_count} _PV couplings")
    
    # Save
    with open(OUTPUT_YAML, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    print(f"Config saved to: {OUTPUT_YAML}")
    print(f"Modules: {list(instances.keys())}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
