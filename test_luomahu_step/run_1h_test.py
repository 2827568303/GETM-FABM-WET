#!/usr/bin/env python3
"""运行 1 小时测试，验证模型稳定性"""

import subprocess
import os
import shutil

CASE_DIR = r'c:\Users\dinod\Desktop\GETM-FABM-WET\test_luomahu_step'
GETM_BIN = r'c:\Users\dinod\Desktop\GETM-FABM-WET\bin\getm_cartesian'


def convert_path(path):
    drive = path[0].lower()
    rest = path[2:].replace('\\', '/')
    return f'/mnt/{drive}{rest}'


def main():
    wsl_case = convert_path(CASE_DIR)
    wsl_getm = convert_path(GETM_BIN)
    
    # Modify getm.inp for 1-hour test
    inp_file = os.path.join(CASE_DIR, 'getm.inp')
    with open(inp_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace("stop = '2020-01-01 00:05:00'",
                              "stop = '2020-01-01 01:00:00'")
    content = content.replace("step_2d = 120", "step_2d = 240")
    content = content.replace("step_3d = 120", "step_3d = 240")
    
    with open(inp_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Modified getm.inp: 1-hour simulation, output every 240 steps (2hrs)')
    
    # Remove old output
    for f in ['output.nc', 'LUOMAHU_WET.2d.nc', 'LUOMAHU_WET.3d.nc']:
        fp = os.path.join(CASE_DIR, f)
        if os.path.exists(fp):
            os.remove(fp)
            print(f'Removed {f}')
    
    print()
    print('=' * 60)
    print('Running 1-hour stability test')
    print(f'Modules: abiotic + sediment + POM/DOM/humus + 2 phyto + zoo')
    print('=' * 60)
    
    cmd = f'cd {wsl_case} && timeout 300s {wsl_getm} 2>&1 | tee step_1h_test.log'
    result = subprocess.run(
        ['wsl', '--', 'bash', '-c', cmd],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    
    print(f'Exit code: {result.returncode}')
    print()
    print('Last 60 lines of output:')
    print('-' * 60)
    lines = result.stdout.split('\n')
    for line in lines[-60:]:
        print(line)
    print('-' * 60)
    
    # Check for segfault
    if 'Segmentation fault' in result.stdout or '段错误' in result.stdout:
        print('\n✗ SEGMENTATION FAULT detected!')
    elif result.returncode != 0:
        print(f'\n✗ Non-zero exit code: {result.returncode}')
    else:
        output_3d = os.path.join(CASE_DIR, 'LUOMAHU_WET.3d.nc')
        if os.path.exists(output_3d):
            size_mb = os.path.getsize(output_3d) / (1024 * 1024)
            print(f'\n✓ SUCCESS! Output: {size_mb:.2f} MB')
            
            # Print FABM timers
            print('\nFABM-related timers:')
            for line in lines:
                if 'getm_fabm' in line or 'advection getm_fabm' in line:
                    print(f'  {line.strip()}')
        else:
            print('\n✗ No output file found!')


if __name__ == '__main__':
    main()
