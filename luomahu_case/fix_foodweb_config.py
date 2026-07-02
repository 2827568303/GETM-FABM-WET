"""
Iteratively fix fabm_full.yaml until it works with GETM (3D).
Run entirely in WSL.
"""
import subprocess
import os

case_dir = r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case'
test_yaml = os.path.join(case_dir, 'fabm.yaml')
getm_exe = '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/bin/getm_cartesian'
log_file = '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/luomahu_case/test_fabm.log'

def run_wsl(cmd):
    result = subprocess.run(
        ['wsl', '-d', 'Ubuntu', 'bash', '-c', cmd],
        capture_output=True, text=True, cwd=case_dir, timeout=180
    )
    return result.returncode, result.stdout + result.stderr

# Start fresh from full config, apply known fixes
run_wsl(f"""
cd /mnt/c/Users/dinod/Desktop/GETM-FABM-WET/luomahu_case
cp fabm_full.yaml fabm.yaml

# Fix 1: hypsograph false
sed -i 's/hypsograph: true/hypsograph: false/g' fabm.yaml

# Fix 2: lSiX false for all zooplankton (prey Si tracking)
sed -i 's/lSi1: true/lSi1: false/g; s/lSi2: true/lSi2: false/g; s/lSi3: true/lSi3: false/g; s/lSi4: true/lSi4: false/g' fabm.yaml

echo "Initial fixes applied"
""")

# Iteratively fix
for i in range(30):
    ret, _ = run_wsl(f"""
cd /mnt/c/Users/dinod/Desktop/GETM-FABM-WET/luomahu_case
timeout 90 {getm_exe} > test_fabm.log 2>&1
echo "EXIT:$?"
""")
    
    # Read log
    ret2, log_output = run_wsl("cat /mnt/c/Users/dinod/Desktop/GETM-FABM-WET/luomahu_case/test_fabm.log")
    
    if 'integrating' in log_output:
        print(f'\nSUCCESS after {i+1} iterations!')
        print(f'First timesteps reached.')
        break
    
    # Find FATAL ERROR
    fatal_line = None
    for line in log_output.split('\n'):
        if 'FATAL ERROR' in line:
            fatal_line = line.strip()
            break
    
    if not fatal_line:
        print(f'Iteration {i+1}: No FATAL ERROR found, but no integrating either')
        # Print last 20 lines
        lines = log_output.strip().split('\n')
        for l in lines[-10:]:
            print(f'  {l}')
        break
    
    print(f'Iteration {i+1}: {fatal_line}')
    
    # Try to fix automatically
    import re
    
    # Pattern: "Variable X/Y must be coupled to an existing state variable."
    m = re.search(r'Variable\s+(\S+)\s+must be coupled', fatal_line)
    if m:
        var_path = m.group(1)
        parts = var_path.split('/')
        instance_name = parts[0]
        coupling_name = parts[1]
        
        if '_PV' in coupling_name:
            base_name = coupling_name.replace('_PV', '')
            # Find the non-PV coupling target in same instance
            ret3, out = run_wsl(f"""
cd /mnt/c/Users/dinod/Desktop/GETM-FABM-WET/luomahu_case
python3 -c "
import yaml
with open('fabm.yaml') as f:
    c = yaml.safe_load(f)
inst = c['instances']['{instance_name}']
couplings = inst.get('coupling', {{}})
base_target = couplings.get('{base_name}', '')
print('BASE_TARGET:', base_target)
"
""")
            base_target = ''
            for line in out.split('\n'):
                if 'BASE_TARGET:' in line:
                    base_target = line.split('BASE_TARGET:')[1].strip()
            
            if base_target:
                # Target format: module/varname -> add _PV to varname
                tparts = base_target.split('/')
                new_target = f"{tparts[0]}/{tparts[1]}_PV"
                print(f'  Adding {coupling_name}: {new_target}')
                
                run_wsl(f"""
cd /mnt/c/Users/dinod/Desktop/GETM-FABM-WET/luomahu_case
python3 -c "
import yaml
with open('fabm.yaml') as f:
    c = yaml.safe_load(f)
c['instances']['{instance_name}']['coupling']['{coupling_name}'] = '{new_target}'
with open('fabm.yaml', 'w') as f:
    yaml.dump(c, f, default_flow_style=False, sort_keys=False)
print('Done')
"
""")
                continue
            else:
                print(f'  Could not find base coupling: {base_name}')
                break
    
    # If we get here, we couldn't fix automatically
    print('  Could not fix automatically')
    break
