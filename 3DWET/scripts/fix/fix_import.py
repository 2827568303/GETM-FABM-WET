#!/usr/bin/env python3
"""
修复 getm_fabm.F90 中的导入语句
"""

FILE_PATH = r'c:\Users\dinod\Desktop\GETM-FABM-PCLake\getm\src\3d\getm_fabm.F90'

def read_file(path):
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    print(f"Reading {FILE_PATH}...")
    content = read_file(FILE_PATH)
    
    # 修复 import 语句
    old_import = """   use fabm_types,only: output_instantaneous, output_none, type_bulk_standard_variable, type_scalar_variable_id
   use fabm, only: fabm_link_scalar_data, fabm_get_scalar_variable_id"""
    
    new_import = """   use fabm_types,only: output_instantaneous, output_none, type_bulk_standard_variable
   use fabm, only: fabm_link_scalar_data, fabm_get_scalar_variable_id, type_scalar_variable_id"""
    
    if old_import in content:
        content = content.replace(old_import, new_import)
        write_file(FILE_PATH, content)
        print("✓ Fixed import statements")
        print("  - Moved type_scalar_variable_id from fabm_types to fabm import")
    else:
        print("✗ Could not find import statements to fix")
        # Check current state
        if "type_scalar_variable_id" in content:
            print("  type_scalar_variable_id is already in the file")
        else:
            print("  type_scalar_variable_id not found - need to add it")

if __name__ == '__main__':
    main()
