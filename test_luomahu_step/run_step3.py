#!/usr/bin/env python3
"""运行第三步测试：添加 phytoplankton 模块（测试 temporal_mean）"""

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
    src = os.path.join(CASE_DIR, 'fabm_step3_phytoplankton.yaml')
    dst = os.path.join(CASE_DIR, 'fabm.yaml')
    shutil.copy2(src, dst)
    print(f'Copied {os.path.basename(src)} -> fabm.yaml')
    
    # Remove old output
    for f in ['output.nc', 'LUOMAHU_WET.2d.nc', 'LUOMAHU_WET.3d.nc']:
        fp = os.path.join(CASE_DIR, f)
        if os.path.exists(fp):
            os.remove(fp)
            print(f'Removed {f}')
    
    print()
    print('=' * 60)
    print('Running Step 3: abiotic + phytoplankton (temporal_mean test)')
    print('=' * 60)
    
    cmd = f'cd {wsl_case} && timeout 30s {wsl_getm} 2>&1 | tee step3_phytoplankton.log'
    result = subprocess.run(
        ['wsl', '--', 'bash', '-c', cmd],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    
    print(f'Exit code: {result.returncode}')
    print()
    print('Last 80 lines of output:')
    print('-' * 60)
    lines = result.stdout.split('\n')
    for line in lines[-80:]:
        print(line)
    print('-' * 60)
    
    # Check for segfault
    if 'Segmentation fault' in result.stdout or '段错误' in result.stdout:
        print('\n✗ SEGMENTATION FAULT detected!')
    elif result.returncode != 0:
        print(f'\n✗ Non-zero exit code: {result.returncode}')
    else:
        # Check output
        output_3d = os.path.join(CASE_DIR, 'LUOMAHU_WET.3d.nc')
        if os.path.exists(output_3d):
            size_mb = os.path.getsize(output_3d) / (1024 * 1024)
            print(f'\n✓ Output file found: LUOMAHU_WET.3d.nc ({size_mb:.2f} MB)')
        else:
            print('\n✗ No output file found!')


if __name__ == '__main__':
    main()
