#!/usr/bin/env python3
"""运行第一步测试：仅 abiotic_water"""

import subprocess
import os
import shutil

CASE_DIR = r'c:\Users\dinod\Desktop\GETM-FABM-WET\test_luomahu_step'
GETM_BIN = r'c:\Users\dinod\Desktop\GETM-FABM-WET\install_gcc9_v3\bin\getm_cartesian'


def convert_path(path):
    drive = path[0].lower()
    rest = path[2:].replace('\\', '/')
    return f'/mnt/{drive}{rest}'


def main():
    wsl_case = convert_path(CASE_DIR)
    wsl_getm = convert_path(GETM_BIN)
    
    # Copy fabm config
    src = os.path.join(CASE_DIR, 'fabm_step1_abiotic.yaml')
    dst = os.path.join(CASE_DIR, 'fabm.yaml')
    shutil.copy2(src, dst)
    print(f'Copied {src} -> {dst}')
    
    # Remove old output
    for f in ['output.nc', 'LUOMAHU_WET.2d.nc', 'LUOMAHU_WET.3d.nc']:
        fp = os.path.join(CASE_DIR, f)
        if os.path.exists(fp):
            os.remove(fp)
            print(f'Removed {f}')
    
    print()
    print('=' * 60)
    print('Running Step 1: abiotic_water only')
    print('=' * 60)
    
    cmd = f'cd {wsl_case} && {wsl_getm} 2>&1 | tee step1_abiotic.log'
    result = subprocess.run(
        ['wsl', '--', 'bash', '-c', cmd],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    
    print(f'Exit code: {result.returncode}')
    print()
    print('Last 50 lines of output:')
    print('-' * 60)
    lines = result.stdout.split('\n')
    for line in lines[-50:]:
        print(line)
    print('-' * 60)
    
    # Check output
    output_3d = os.path.join(CASE_DIR, 'LUOMAHU_WET.3d.nc')
    if os.path.exists(output_3d):
        size_mb = os.path.getsize(output_3d) / (1024 * 1024)
        print(f'\n✓ Output file found: LUOMAHU_WET.3d.nc ({size_mb:.2f} MB)')
    else:
        print('\n✗ No output file found!')


if __name__ == '__main__':
    main()
