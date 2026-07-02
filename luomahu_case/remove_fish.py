import yaml

with open(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\fabm.yaml') as f:
    c = yaml.safe_load(f)

for fish in ['JuFish', 'AdFish', 'PiscFish']:
    if fish in c['instances']:
        del c['instances'][fish]
        print(f'Removed {fish}')

with open(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\fabm.yaml', 'w') as f:
    yaml.dump(c, f, default_flow_style=False, sort_keys=False)

print('Done - fish removed')
