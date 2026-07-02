#!/usr/bin/env python3
"""Fix _PV (pelagic mirror) variable couplings in fabm.yaml for WET model."""
import yaml
import os
import sys

INPUT_YAML = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\wet\testcases\fabm-wet.yaml"
OUTPUT_YAML = r"C:\Users\dinod\Desktop\GETM-FABM-WET\fabm_full_fixed.yaml"

# Define all _PV couplings needed
# Format: {module_name: {pv_variable_name: target_variable_path}}
PV_COUPLINGS = {
    # POM pool couplings
    'POM_DW_pool_sediment_PV': 'POM/sDS_PV',
    'POM_N_pool_sediment_PV': 'POM/sNS_PV',
    'POM_P_pool_sediment_PV': 'POM/sPS_PV',
    'POM_C_pool_sediment_PV': 'POM/sCS_PV',
    'POM_Si_pool_sediment_PV': 'POM/sSiPaS_PV',
    
    # DOM pool couplings
    'DOM_DW_pool_sediment_PV': 'DOM/sDS_PV',
    'DOM_N_pool_sediment_PV': 'DOM/sNS_PV',
    'DOM_P_pool_sediment_PV': 'DOM/sPS_PV',
    'DOM_C_pool_sediment_PV': 'DOM/sCS_PV',
    'DOM_Si_pool_sediment_PV': 'DOM/sSiO2S_PV',
    
    # Humus pool couplings
    'humus_DW_in_deep_sediment_PV': 'humus/sDS_PV',
    'humus_N_in_deep_sediment_PV': 'humus/sNS_PV',
    'humus_P_in_deep_sediment_PV': 'humus/sPS_PV',
    'humus_C_in_deep_sediment_PV': 'humus/sCS_PV',
}

# Modules that need _PV couplings (benthic modules and modules that interact with sediment)
MODULES_WITH_PV_NEEDS = [
    'macrophytes', 'zoobenthos', 'burial', 'sediment_exchange',
    'cyanobacteria', 'diatoms', 'greens', 'cladocerans', 'copepods',
    'JuFish', 'AdFish', 'PiscFish',
]

def fix_pv_couplings(config):
    """Add _PV couplings to modules that need them."""
    instances = config.get('instances', {})
    
    fixed_count = 0
    for module_name in MODULES_WITH_PV_NEEDS:
        if module_name not in instances:
            continue
        
        inst = instances[module_name]
        coupling = inst.setdefault('coupling', {})
        
        for pv_var, target in PV_COUPLINGS.items():
            # Check if this coupling already exists
            if pv_var not in coupling:
                coupling[pv_var] = target
                fixed_count += 1
    
    print(f"Added {fixed_count} _PV couplings")
    return config

def main():
    with open(INPUT_YAML, 'r') as f:
        config = yaml.safe_load(f)
    
    config = fix_pv_couplings(config)
    
    with open(OUTPUT_YAML, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    print(f"Fixed config saved to: {OUTPUT_YAML}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
