#!/usr/bin/env python3
"""
修改 getm_fabm.F90 添加 time_step 链接支持鱼类模块
"""

import re

FILE_PATH = r'c:\Users\dinod\Desktop\GETM-FABM-PCLake\getm\src\3d\getm_fabm.F90'

def wsl_path(path):
    """Convert Windows path to WSL path"""
    drive = path[0].lower()
    rest = path[2:].replace('\\', '/')
    return f'/mnt/{drive}{rest}'

def read_file(path):
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    path = FILE_PATH
    wsl_file = wsl_path(path)
    
    print(f"Reading {path}...")
    content = read_file(path)
    
    # 1. 修改 import 语句，添加 fabm_link_scalar_data 和 fabm_get_scalar_variable_id
    old_import = """   use fabm_types,only: output_instantaneous, output_none, type_bulk_standard_variable
   use fabm_standard_variables, only: standard_variables"""
    
    new_import = """   use fabm_types,only: output_instantaneous, output_none, type_bulk_standard_variable, type_scalar_variable_id
   use fabm, only: fabm_link_scalar_data, fabm_get_scalar_variable_id
   use fabm_standard_variables, only: standard_variables"""
    
    if old_import in content:
        content = content.replace(old_import, new_import)
        print("✓ Updated import statements")
    else:
        print("✗ Could not find import statements to update")
        return
    
    # 2. 添加 time_step_id 变量声明
    old_decl = """   REALTYPE, allocatable :: bot_pel_conv_col(:)

   type type_input_variable"""
    
    new_decl = """   REALTYPE, allocatable :: bot_pel_conv_col(:)
   type (type_scalar_variable_id) :: time_step_id

   type type_input_variable"""
    
    if old_decl in content:
        content = content.replace(old_decl, new_decl)
        print("✓ Added time_step_id variable declaration")
    else:
        print("✗ Could not find variable declaration section")
        return
    
    # 3. 在初始化部分获取 time_step_id
    # 在 "allocate(fabm_pel(I3DFIELD..." 之前添加
    old_init = """      end do

!     Allocate memory for pelagic state variables.
      allocate(fabm_pel(I3DFIELD,size(model%state_variables)),stat=rc)"""
    
    new_init = """      end do

!     Get time_step variable ID (needed by fish module)
      time_step_id = fabm_get_scalar_variable_id(model, 'time_step')

!     Allocate memory for pelagic state variables.
      allocate(fabm_pel(I3DFIELD,size(model%state_variables)),stat=rc)"""
    
    if old_init in content:
        content = content.replace(old_init, new_init)
        print("✓ Added time_step_id initialization")
    else:
        print("✗ Could not find initialization section")
        return
    
    # 4. 在 set_env_gotm_fabm 调用后添加 time_step 链接
    old_setenv = """            call set_env_gotm_fabm(latc(i,j),lonc(i,j),dt,0,0,T(i,j,1:),S(i,j,1:), &
                                   rho(i,j,1:),nuh(i,j,0:),hn(i,j,0:),ww(i,j,0:), &
                                   bioshade,I_0,cloud,taub_nonnorm,wind_speed,precip(i,j),evap(i,j), &
                                   z,A(i,j),g1(i,j),g2(i,j),yearday,secondsofday)
            call model%link_horizontal_data(id_bottom_depth_below_geoid,H(i,j))
            call model%link_horizontal_data(id_bottom_depth,D(i,j))

!           Update bot_pel_conv for this column (1/dz per layer)"""
    
    new_setenv = """            call set_env_gotm_fabm(latc(i,j),lonc(i,j),dt,0,0,T(i,j,1:),S(i,j,1:), &
                                   rho(i,j,1:),nuh(i,j,0:),hn(i,j,0:),ww(i,j,0:), &
                                   bioshade,I_0,cloud,taub_nonnorm,wind_speed,precip(i,j),evap(i,j), &
                                   z,A(i,j),g1(i,j),g2(i,j),yearday,secondsofday)
            call model%link_horizontal_data(id_bottom_depth_below_geoid,H(i,j))
            call model%link_horizontal_data(id_bottom_depth,D(i,j))

!           Link time_step scalar (needed by fish module)
            if (time_step_id%read_index /= -1) call fabm_link_scalar_data(model, time_step_id, dt)

!           Update bot_pel_conv for this column (1/dz per layer)"""
    
    if old_setenv in content:
        content = content.replace(old_setenv, new_setenv)
        print("✓ Added time_step linking after set_env_gotm_fabm")
    else:
        print("✗ Could not find set_env_gotm_fabm call section")
        return
    
    # 写回文件
    write_file(path, content)
    print(f"\n✓ Successfully modified {path}")
    print("\nChanges made:")
    print("  1. Added 'type_scalar_variable_id' to fabm_types import")
    print("  2. Added 'fabm_link_scalar_data, fabm_get_scalar_variable_id' to fabm import")
    print("  3. Added 'time_step_id' variable declaration")
    print("  4. Added time_step_id initialization after bot_pel_conv allocation")
    print("  5. Added time_step linking after set_env_gotm_fabm call")


if __name__ == '__main__':
    main()
