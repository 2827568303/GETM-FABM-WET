#!/usr/bin/env python3
"""逐步测试 WET 模块的 Python 脚本"""

import subprocess
import os
import shutil
import sys

CASE_DIR = r'c:\Users\dinod\Desktop\GETM-FABM-WET\test_luomahu_step'
GETM_BIN = r'c:\Users\dinod\Desktop\GETM-FABM-WET\install_gcc9_v3\bin\getm_cartesian'

def run_wsl_cmd(cmd, cwd=None):
    """Run a command via WSL"""
    wsl_cmd = ['wsl', '--'] + cmd
    result = subprocess.run(wsl_cmd, cwd=cwd, capture_output=True, text=True, 
                           encoding='utf-8', errors='replace')
    return result.returncode, result.stdout, result.stderr

def convert_path_to_wsl(win_path):
    """Convert Windows path to WSL path"""
    # C:\Users\... -> /mnt/c/Users/...
    drive = win_path[0].lower()
    path = win_path[2:].replace('\\', '/')
    return f'/mnt/{drive}{path}'

def run_test(step_name, fabm_yaml_file):
    """Run a single test step"""
    print(f"\n{'='*60}")
    print(f"Step: {step_name}")
    print(f"{'='*60}")
    
    # Copy fabm yaml
    src = os.path.join(CASE_DIR, fabm_yaml_file)
    dst = os.path.join(CASE_DIR, 'fabm.yaml')
    shutil.copy2(src, dst)
    print(f"  Using config: {fabm_yaml_file}")
    
    # Remove old output
    for f in ['output.nc', 'LUOMAHU_WET.2d.nc', 'LUOMAHU_WET.3d.nc']:
        fpath = os.path.join(CASE_DIR, f)
        if os.path.exists(fpath):
            os.remove(fpath)
    
    # Run GETM via WSL
    wsl_case_dir = convert_path_to_wsl(CASE_DIR)
    wsl_getm_bin = convert_path_to_wsl(GETM_BIN)
    
    log_file = os.path.join(CASE_DIR, f'{step_name}.log')
    
    print(f"  Running GETM...")
    ret, stdout, stderr = run_wsl_cmd(
        ['bash', '-c', f'cd {wsl_case_dir} && {wsl_getm_bin} 2>&1 | tee {step_name}.log']
    )
    
    # Check if output exists
    output_3d = os.path.join(CASE_DIR, 'LUOMAHU_WET.3d.nc')
    output_2d = os.path.join(CASE_DIR, 'LUOMAHU_WET.2d.nc')
    
    if ret == 0 and (os.path.exists(output_3d) or os.path.exists(output_2d)):
        print(f"  ✓ SUCCESS (exit code: {ret})")
        # Check output file size
        if os.path.exists(output_3d):
            size_mb = os.path.getsize(output_3d) / (1024*1024)
            print(f"  Output file: LUOMAHU_WET.3d.nc ({size_mb:.2f} MB)")
        return True
    else:
        print(f"  ✗ FAILED (exit code: {ret})")
        # Show last 30 lines of log
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
            print(f"  Last 30 lines of {step_name}.log:")
            for line in lines[-30:]:
                print(f"    {line.rstrip()}")
        return False

def main():
    print("=" * 60)
    print("WET 模块逐步测试")
    print("=" * 60)
    
    steps = [
        ('step1_abiotic', 'fabm_step1_abiotic.yaml', '仅 abiotic_water（无 temporal_mean）'),
    ]
    
    results = {}
    for step_name, fabm_file, description in steps:
        print(f"\n测试: {description}")
        success = run_test(step_name, fabm_file)
        results[step_name] = success
        
        if not success:
            print(f"\n❌ Step {step_name} failed! Stopping.")
            break
    
    print("\n" + "=" * 60)
    print("测试结果汇总:")
    print("=" * 60)
    for step_name, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {step_name}: {status}")
    
    if all(results.values()):
        print("\n所有测试通过！")
    else:
        print("\n有测试失败，需要进一步调试。")

if __name__ == '__main__':
    main()
