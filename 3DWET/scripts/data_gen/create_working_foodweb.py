#!/usr/bin/env python3
"""Create a working food web config (no fish) with proper _PV couplings."""
import yaml
import sys

INPUT_YAML = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\wet\testcases\fabm-wet.yaml"
OUTPUT_YAML = r"C:\Users\dinod\Desktop\GETM-FABM-WET\fabm_foodweb_working.yaml"

FISH_MODULES = ['JuFish', 'AdFish', 'PiscFish']

# Modules that need _PV couplings (from OM pools)
# Based on the reference config, these modules have _PV couplings:
# - macrophytes (has POM_DW_pool_sediment_PV etc.)
# - zoobenthos 
# - cyanobacteria, diatoms, greens (phytoplankton)
# - cladocerans, copepods (zooplankton)
# - burial
# - sediment_exchange

# Standard OM pool _PV couplings
OM_PV_COUPLINGS = {
    # POM pool
    'POM_DW_pool_sediment_PV': 'POM/sDS_PV',
    'POM_N_pool_sediment_PV': 'POM/sNS_PV',
    'POM_P_pool_sediment_PV': 'POM/sPS_PV',
    'POM_C_pool_sediment_PV': 'POM/sCS_PV',
    # DOM pool
    'DOM_DW_pool_sediment_PV': 'DOM/sDS_PV',
    'DOM_N_pool_sediment_PV': 'DOM/sNS_PV',
    'DOM_P_pool_sediment_PV': 'DOM/sPS_PV',
    'DOM_C_pool_sediment_PV': 'DOM/sCS_PV',
    # Humus pool
    'humus_DW_in_deep_sediment_PV': 'humus/sDS_PV',
    'humus_N_in_deep_sediment_PV': 'humus/sNS_PV',
    'humus_P_in_deep_sediment_PV': 'humus/sPS_PV',
    'humus_C_in_deep_sediment_PV': 'humus/sCS_PV',
}

MODULES_WITH_OM_PV_NEEDS = [
    'macrophytes', 'zoobenthos', 'burial', 'sediment_exchange',
    'cyanobacteria', 'diatoms', 'greens', 'cladocerans', 'copepods',
]

def main():
    with open(INPUT_YAML, 'r') as f:
        config = yaml.safe_load(f)
    
    instances = config['instances']
    
    # Remove fish modules
    for fm in FISH_MODULES:
        if fm in instances:
            del instances[fm]
            print(f"Removed fish module: {fm}")
    
    # Disable Si tracking for all modules
    for name, inst in instances.items():
        if 'parameters' not in inst:
            continue
        params = inst['parameters']
        for key in list(params.keys()):
            # Look for lSi parameters like lSi1, lSi2, etc.
            if key.startswith('lSi') and key[3:].isdigit():
                params[key] = False
    
    # Add _PV couplings to modules that need them
    # But only add if the module already has similar (non-PV) couplings
    # This is a heuristic - if a module has POM_DW_pool_sediment, it probably needs POM_DW_pool_sediment_PV too
    added = 0
    for name in MODULES_WITH_OM_PV_NEEDS:
        if name not in instances:
            continue
        inst = instances[name]
        coupling = inst.setdefault('coupling', {})
        
        for pv_dep, pv_target in OM_PV_COUPLINGS.items():
            # Check if the base (non-PV) version of this coupling exists
            # e.g., if POM_DW_pool_sediment exists, then POM_DW_pool_sediment_PV is probably needed
            base_dep = pv_dep.replace('_PV', '').replace('_in_deep_sediment', '_pool_sediment')
            # Actually let's just check if any similar coupling exists
            pool_name = pv_dep.split('_')[0]  # POM, DOM, humus
            has_base = any(k.startswith(pool_name + '_') and 'sediment' in k and not k.endswith('_PV') 
                          for k in coupling.keys())
            
            if has_base and pv_dep not in coupling:
                coupling[pv_dep] = pv_target
                added += 1
                print(f"  Added {name}/{pv_dep} -> {pv_target}")
    
    print(f"\nTotal _PV couplings added: {added}")
    print(f"Modules: {list(instances.keys())}")
    
    with open(OUTPUT_YAML, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    print(f"\nSaved to: {OUTPUT_YAML}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
