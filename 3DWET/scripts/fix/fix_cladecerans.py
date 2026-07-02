#!/usr/bin/env python3
"""
修改 fabm_full.yaml 为 cladecerans 添加 prey_suffix 参数
"""

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
    
    # 修改 cladecerans
    old_cladecerans = """  cladecerans:
    long_name: cladecerans
    model: wet/zooplankton
    parameters:
      cClearPrey1: 2.5                                           #  clearance rate for prey 1 (m3/gDW/d), default = 2.0
      cClearPrey2: 2.5                                           #  clearance rate for prey 2 (m3/gDW/d), default = 2.0
      cClearPrey3: 2.5                                           #  clearance rate for prey 3 (m3/gDW/d), default = 2.0
      cClearPrey4: 2.5"""
    
    new_cladecerans = """  cladecerans:
    long_name: cladecerans
    model: wet/zooplankton
    parameters:
      nPrey: 4
      prey_suffix1: _W                                           # suffix for phytoplankton prey
      prey_suffix2: _W                                           # suffix for phytoplankton prey
      prey_suffix3: _W                                           # suffix for phytoplankton prey
      prey_suffix4: ''                                            # no suffix for POM prey
      cClearPrey1: 2.5                                           #  clearance rate for prey 1 (m3/gDW/d), default = 2.0
      cClearPrey2: 2.5                                           #  clearance rate for prey 2 (m3/gDW/d), default = 2.0
      cClearPrey3: 2.5                                           #  clearance rate for prey 3 (m3/gDW/d), default = 2.0
      cClearPrey4: 2.5"""
    
    if old_cladecerans in content:
        content = content.replace(old_cladecerans, new_cladecerans)
        write_file(FILE_PATH, content)
        print("✓ Updated cladecerans parameters")
    else:
        print("✗ Could not find cladecerans section")
        # Show what's there
        import re
        match = re.search(r'  cladecerans:', content)
        if match:
            start = match.start()
            print(f"Found 'cladecerans:' at position {start}")
            print("Content around it:")
            print(content[start:start+500])


if __name__ == '__main__':
    main()
