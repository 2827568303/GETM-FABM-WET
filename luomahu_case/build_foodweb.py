"""
Build complete food web FABM config based on working simple config.
Adds: diatoms, copepods, macrophytes, zoobenthos, 3 fish groups
"""
import yaml

def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

simple = load_yaml(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\fabm_simple_backup.yaml')
full = load_yaml(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\fabm_full.yaml')

simple_instances = set(simple['instances'].keys())
full_instances = set(full['instances'].keys())

print('Simple instances:', sorted(simple_instances))
print('Full instances:', sorted(full_instances))
print()
print('Missing from simple:', sorted(full_instances - simple_instances))
