#!/usr/bin/env python3
"""
修改 fabm_full.yaml 添加 prey_suffix 参数
"""

import re

FILE_PATH = r'c:\Users\dinod\Desktop\GETM-FABM-PCLake\luomahu_case\fabm_full.yaml'

def read_file(path):
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    print(f"Reading {FILE_PATH}...")
    content = read_file(FILE_PATH)
    
    changes = 0
    
    # 为 zooplankton (cladecerans) 添加 prey_suffix 参数
    # prey_model1-3 是浮游植物，需要 _W 后缀
    # prey_model4 是 POM，不需要后缀
    old_zooplankton = """  cladecerans:
    long_name: cladecerans
    model: wet/zooplankton
    parameters:
      nPrey: 4
      diagnostics: false"""
    
    new_zooplankton = """  cladecerans:
    long_name: cladecerans
    model: wet/zooplankton
    parameters:
      nPrey: 4
      prey_suffix1: _W                                           # suffix for phytoplankton prey
      prey_suffix2: _W                                           # suffix for phytoplankton prey
      prey_suffix3: _W                                           # suffix for phytoplankton prey
      prey_suffix4: ''                                            # no suffix for POM prey
      diagnostics: false"""
    
    if old_zooplankton in content:
        content = content.replace(old_zooplankton, new_zooplankton)
        print("✓ Updated cladecerans parameters")
        changes += 1
    else:
        print("✗ Could not find cladecerans section")
    
    # 为 copepods 添加 prey_suffix 参数
    old_copepods = """  copepods:
    long_name: copepods
    model: wet/zooplankton
    parameters:
      cClearPrey1: 2.0                                           #  clearance rate for prey 1 (m3/gDW/d), default = 2.0
      cClearPrey2: 2.0                                           #  clearance rate for prey 2 (m3/gDW/d), default = 2.0
      cClearPrey3: 2.0                                           #  clearance rate for prey 3 (m3/gDW/d), default = 2.0
      cClearPrey4: 2.0                                           #  clearance rate for prey 4 (m3/gDW/d), default = 2.0"""
    
    new_copepods = """  copepods:
    long_name: copepods
    model: wet/zooplankton
    parameters:
      nPrey: 4
      prey_suffix1: _W                                           # suffix for phytoplankton prey
      prey_suffix2: _W                                           # suffix for phytoplankton prey
      prey_suffix3: _W                                           # suffix for phytoplankton prey
      prey_suffix4: ''                                            # no suffix for POM prey
      cClearPrey1: 2.0                                           #  clearance rate for prey 1 (m3/gDW/d), default = 2.0
      cClearPrey2: 2.0                                           #  clearance rate for prey 2 (m3/gDW/d), default = 2.0
      cClearPrey3: 2.0                                           #  clearance rate for prey 3 (m3/gDW/d), default = 2.0
      cClearPrey4: 2.0                                           #  clearance rate for prey 4 (m3/gDW/d), default = 2.0"""
    
    if old_copepods in content:
        content = content.replace(old_copepods, new_copepods)
        print("✓ Updated copepods parameters")
        changes += 1
    else:
        print("✗ Could not find copepods section")
    
    write_file(FILE_PATH, content)
    print(f"\n✓ Made {changes} changes to {FILE_PATH}")


if __name__ == '__main__':
    main()
