"""
Step 1: Add diatoms (3rd phytoplankton group) to the working simple config.
Based on greens as template, with diatom-specific parameters from full config.
"""
import copy
import yaml

with open(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\fabm_simple_backup.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Copy greens to create diatoms template
diatoms = copy.deepcopy(config['instances']['greens'])
diatoms['long_name'] = 'diatoms'

# Update diatom-specific parameters
diatoms['parameters'] = {
    'qLightMethod': 0,
    'lSi': True,  # diatoms use silica
    'cSiD': 0.15,
    'hSiAss': 0.09,
    'diagnostics': False,
}

# Same initialization as greens but with Si
diatoms['initialization'] = {
    'sDW': 0.1,
    'sNW': 0.003,
    'sPW': 0.0003,
    'sCW': 0.04,
    'sDS': 0.003,
    'sNS': 0.00009,
    'sPS': 3e-05,
    'sCS': 0.0012,
    'sDS_PV': 0.003,
    'sNS_PV': 0.00009,
    'sPS_PV': 3e-05,
    'sCS_PV': 0.0012,
}

# Insert diatoms after greens
instances = config['instances']
new_instances = {}
for name, inst in instances.items():
    new_instances[name] = inst
    if name == 'greens':
        new_instances['diatoms'] = diatoms

config['instances'] = new_instances

# Update burial: nPHYT from 2 to 3, add POM_phytoplankton_update3
config['instances']['burial']['parameters']['nPHYT'] = 3
config['instances']['burial']['coupling']['POM_phytoplankton_update3'] = 'diatoms/tDPOMS'

# Update abiotic_sediment: add diatoms POM coupling (nPOM stays same if it tracks pools, not phytoplankton)
# abiotic_sediment uses nPOM which is about POM pools, not phytoplankton groups

# Update zooplankton: nPrey from 2 to 3, prey_model3
zoo = config['instances']['zooplankton']
zoo['parameters']['nPrey'] = 3
zoo['coupling']['prey_model3'] = 'diatoms'

# Add lSi3 false for zooplankton (only diatoms have Si, and prey 3 is diatoms -> lSi3=true)
# But we had issues with lSi, so keep lSi false for zooplankton prey tracking

with open(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\fabm.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)

print('Added diatoms. nPHYT=3, zooplankton nPrey=3')
