"""
Switch from wet/fish to wet/fish_pclake to avoid time_step dependency
"""
import yaml

case_dir = r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case'

with open(f'{case_dir}/fabm_full.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Check if fish modules exist
if 'instances' in config and 'JuFish' in config['instances']:
    if config['instances']['JuFish'].get('model') == 'wet/fish':
        print("Found wet/fish modules, switching to wet/fish_pclake...")

        # Switch fish modules from wet/fish to wet/fish_pclake
        for fish_name in ['JuFish', 'AdFish', 'PiscFish']:
            if fish_name in config['instances']:
                old_model = config['instances'][fish_name].get('model')
                if old_model == 'wet/fish':
                    config['instances'][fish_name]['model'] = 'wet/fish_pclake'
                    print(f"  {fish_name}: wet/fish -> wet/fish_pclake")

        with open(f'{case_dir}/fabm_with_fish.yaml', 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        print("\nCreated fabm_with_fish.yaml with fish_pclake modules")
    else:
        print(f"Current model: {config['instances']['JuFish'].get('model')}")
else:
    print("No fish modules found")
