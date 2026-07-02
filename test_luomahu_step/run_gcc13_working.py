#!/usr/bin/env python3
"""使用 bin/getm_cartesian (GCC13) 运行完整测试"""

import subprocess
import os
import shutil

CASE_DIR = r'c:\Users\dinod\Desktop\GETM-FABM-WET\test_luomahu_step'
SRC_DIR = r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case'
GETM_BIN = r'c:\Users\dinod\Desktop\GETM-FABM-WET\bin\getm_cartesian'


def convert_path(path):
    drive = path[0].lower()
    rest = path[2:].replace('\\', '/')
    return f'/mnt/{drive}{rest}'


def main():
    wsl_case = convert_path(CASE_DIR)
    wsl_getm = convert_path(GETM_BIN)
    
    # Copy necessary files from luomahu_case
    files_to_copy = [
        'fabm_working.yaml',
        'gotm_fabm.nml',
        'gotmturb.nml',
        'bathymetry.nc',
        'rivers.nc',
        'meteo.nc',
    ]
    
    for f in files_to_copy:
        src = os.path.join(SRC_DIR, f)
        dst = os.path.join(CASE_DIR, f)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f'Copied {f}')
    
    # Copy fabm config
    src = os.path.join(CASE_DIR, 'fabm_working.yaml')
    dst = os.path.join(CASE_DIR, 'fabm.yaml')
    shutil.copy2(src, dst)
    print(f'Copied fabm_working.yaml -> fabm.yaml')
    
    # Modify getm.inp for short test (5 minutes)
    inp_file = os.path.join(CASE_DIR, 'getm.inp')
    with open(inp_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "stop = '2020-01-01 00:05:00'" not in content:
        content = content.replace("stop = '2020-01-01 00:05:00'",
                                  "stop = '2020-01-01 00:05:00'")
        if "stop = '2020-01-01 00:05:00'" not in content:
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
    print('Running 5-min test with bin/getm_cartesian (GCC13)')
    print(f'Config: fabm_working.yaml (with phytoplankton)')
    print('=' * 60)
    
    cmd = f'cd {wsl_case} && timeout 120s {wsl_getm} 2>&1 | tee step_gcc13_working.log'
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
            
            # Check if FABM actually ran (getm_fabm timer > 0)
            if 'getm_fabm' in result.stdout:
                for line in lines:
                    if 'getm_fabm' in line:
                        print(f'  FABM timer: {line.strip()}')
                        break
        else:
            print('\n✗ No output file found!')


if __name__ == '__main__':
    main()
