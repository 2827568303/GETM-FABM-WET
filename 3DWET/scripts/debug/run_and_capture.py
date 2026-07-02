import subprocess
import os
from pathlib import Path

case_dir = Path(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case')
exe = Path(r'c:\Users\dinod\Desktop\GETM-FABM-WET\bin\getm_cartesian')

print(f'工作目录: {case_dir}')
print(f'可执行文件: {exe}')
print(f'可执行文件存在: {exe.exists()}')
print()

os.chdir(case_dir)
result = subprocess.run(
    [str(exe)],
    capture_output=True,
    text=True,
    timeout=300
)

print('=== STDOUT ===')
print(result.stdout)
print()
print('=== STDERR ===')
print(result.stderr)
print()
print(f'返回码: {result.returncode}')
