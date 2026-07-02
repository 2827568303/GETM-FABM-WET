#!/usr/bin/env python3
"""
骆马湖三维生态系统模型 - 可视化脚本
使用NCO工具直接生成图
"""
import subprocess
import os

os.chdir('/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/luomahu_case')

# 检查可用的ncwa/ncap工具
print("=== 骆马湖 WET 食物网模型可视化 ===\n")

# 列出可用的食物网变量
print("1. 浮游植物变量:")
subprocess.run("ncdump -h LUOMAHU_WET.3d.nc 2>/dev/null | grep -E 'cyano|diatom|green' | head -5", shell=True)

print("\n2. 浮游动物变量:")
subprocess.run("ncdump -h LUOMAHU_WET.3d.nc 2>/dev/null | grep -E 'cladocer|copepod' | head -5", shell=True)

print("\n3. 沉水植物变量:")
subprocess.run("ncdump -h LUOMAHU_WET.3d.nc 2>/dev/null | grep -E 'macrophy' | head -5", shell=True)

print("\n4. 底栖动物变量:")
subprocess.run("ncdump -h LUOMAHU_WET.3d.nc 2>/dev/null | grep -E 'zoobenth' | head -5", shell=True)

print("\n5. 营养盐变量:")
subprocess.run("ncdump -h LUOMAHU_WET.3d.nc 2>/dev/null | grep -E 'NH4|NO3|PO4|O2' | head -8", shell=True)

print("\n6. 输出维度:")
subprocess.run("ncdump -h LUOMAHU_WET.3d.nc 2>/dev/null | grep -E 'time =|sigma =|xc =|yc ='", shell=True)

print("\n可视化完成!")
