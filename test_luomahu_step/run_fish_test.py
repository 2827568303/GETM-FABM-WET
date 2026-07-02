#!/usr/bin/env python3
"""测试含鱼类的完整食物网配置"""

import subprocess
import os
import shutil

CASE_DIR = r'c:\Users\dinod\Desktop\GETM-FABM-WET\test_luomahu_step'
FABM_CONFIG = r'c:\Users\dinod\Desktop\GETM-FABM-PCLake\luomahu_case\fabm_full.yaml'
GETM_BIN = r'c:\Users\dinod\Desktop\GETM-FABM-WET\install_gcc9_v5\bin\getm_cartesian'


def convert_path(path):
    drive = path[0].lower()
    rest = path[2:].replace('\\', '/')
    return f'/mnt/{drive}{rest}'


def main():
    wsl_case = convert_path(CASE_DIR)
    wsl_getm = convert_path(GETM_BIN)
    
    # Copy config
    src = FABM_CONFIG
    dst = os.path.join(CASE_DIR, 'fabm.yaml')
    shutil.copy2(src, dst)
    print(f'Copied {os.path.basename(src)} -> fabm.yaml')
    
    # Modify getm.inp for short test (5 minutes)
    inp_file = os.path.join(CASE_DIR, 'getm.inp')
    with open(inp_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "stop = '2020-01-01 00:10:00'" not in content:
        content = content.replace("stop = '2020-01-01 00:05:00'",
                                  "stop = '2020-01-01 00:05:00'")
        content = content.replace("stop = '2020-01-01 01:00:00'",
                                  "stop = '2020-01-01 00:05:00'")
        with open(inp_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print('Modified getm.inp: 5-minute simulation')
    
    # Remove old output
    for f in ['output.nc', 'LUOMAHU_WET.2d.nc', 'LUOMAHU_WET.3d.nc']:
        fp = os.path.join(CASE_DIR, f)
        if os.path.exists(fp):
            os.remove(fp)
            print(f'Removed {f}')
    
    print()
    print('=' * 60)
    print('Testing FULL config with FISH (GCC 9 compiled)')
    print(f'Config: {os.path.basename(FABM_CONFIG)}')
    print('=' * 60)
    
    cmd = f'cd {wsl_case} && timeout 180s {wsl_getm} 2>&1 | tee step_fish_test.log'
    result = subprocess.run(
        ['wsl', '--', 'bash', '-c', cmd],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    
    print(f'Exit code: {result.returncode}')
    print()
    print('Last 100 lines of output:')
    print('-' * 60)
    lines = result.stdout.split('\n')
    for line in lines[-100:]:
        print(line)
    print('-' * 60)
    
    # Check for errors
    if 'Segmentation fault' in result.stdout or '段错误' in result.stdout:
        print('\n✗ SEGMENTATION FAULT detected!')
    elif 'FATAL ERROR' in result.stdout:
        print('\n✗ FATAL ERROR detected!')
    elif result.returncode != 0:
        print(f'\n✗ Non-zero exit code: {result.returncode}')
    else:
        output_3d = os.path.join(CASE_DIR, 'LUOMAHU_WET.3d.nc')
        if os.path.exists(output_3d):
            size_mb = os.path.getsize(output_3d) / (1024 * 1024)
            print(f'\n✓ SUCCESS! Output: {size_mb:.2f} MB')
            
            print('\nFABM timer:')
            for line in lines:
                if 'getm_fabm' in line:
                    stripped = line.strip()
                    if stripped.startswith('getm_fabm'):
                        print(f'  {stripped}')
        else:
            print('\n✗ No output file found!')


if __name__ == '__main__':
    main()
