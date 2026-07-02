#!/usr/bin/env python3
"""Patch GETM-FABM interface to add bot_pel_conv support (needed by WET model).
This version adds the link at initialization time so that fabm_check_ready passes.
"""
import os
import shutil

GETM_FABM_FILE = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\getm\src\3d\getm_fabm.F90"
BACKUP_FILE = GETM_FABM_FILE + ".bak_botpel_v2"

def apply_patch():
    with open(GETM_FABM_FILE, 'r', encoding='latin-1') as f:
        content = f.read()
    
    if 'bot_pel_conv' in content:
        print("bot_pel_conv already in file. Restoring from backup first...")
        if os.path.exists(BACKUP_FILE):
            shutil.copy2(BACKUP_FILE, GETM_FABM_FILE)
            with open(GETM_FABM_FILE, 'r', encoding='latin-1') as f:
                content = f.read()
        else:
            print("No backup file found!")
            return
    
    # Create backup
    shutil.copy2(GETM_FABM_FILE, BACKUP_FILE)
    print(f"Backup created: {BACKUP_FILE}")
    
    # 1. Add import for type_bulk_standard_variable
    old_import = "use fabm_types,only: output_instantaneous, output_none"
    new_import = "use fabm_types,only: output_instantaneous, output_none, type_bulk_standard_variable"
    content = content.replace(old_import, new_import, 1)
    print("  Added type_bulk_standard_variable import")
    
    # 2. Add module-level bot_pel_conv array in PRIVATE DATA MEMBERS section
    old_private = "   type (type_horizontal_variable_id) :: id_bottom_depth_below_geoid,id_bottom_depth"
    new_private = """   type (type_horizontal_variable_id) :: id_bottom_depth_below_geoid,id_bottom_depth
   REALTYPE, allocatable :: bot_pel_conv_col(:)"""
    content = content.replace(old_private, new_private, 1)
    print("  Added bot_pel_conv_col module variable")
    
    # 3. Allocate and link bot_pel_conv in init_getm_fabm (after id_bottom_depth assignment)
    old_init = """      id_bottom_depth_below_geoid = model%get_horizontal_variable_id(standard_variables%bottom_depth_below_geoid)
      id_bottom_depth = model%get_horizontal_variable_id(standard_variables%bottom_depth)"""
    
    new_init = """      id_bottom_depth_below_geoid = model%get_horizontal_variable_id(standard_variables%bottom_depth_below_geoid)
      id_bottom_depth = model%get_horizontal_variable_id(standard_variables%bottom_depth)

!     Allocate and link bot_pel_conv (benthic-pelagic conversion factor)
!     Needed by WET/PCLake model for _PV (pelagic mirror) variables
      allocate(bot_pel_conv_col(kmax))
      bot_pel_conv_col = _ONE_
      call model%link_bulk_data(type_bulk_standard_variable(name='bot_pel_conv',units='m-1'), &
                               bot_pel_conv_col(1:kmax))"""
    
    content = content.replace(old_init, new_init, 1)
    print("  Added init allocation and link")
    
    # 4. Update bot_pel_conv values in do_getm_fabm, per column
    old_do = """            call model%link_horizontal_data(id_bottom_depth_below_geoid,H(i,j))
            call model%link_horizontal_data(id_bottom_depth,D(i,j))"""
    
    new_do = """            call model%link_horizontal_data(id_bottom_depth_below_geoid,H(i,j))
            call model%link_horizontal_data(id_bottom_depth,D(i,j))

!           Update bot_pel_conv for this column (1/dz per layer)
            do kk=1,kmax
               bot_pel_conv_col(kk) = _ONE_ / max(hn(i,j,kk), 1e-6)
            end do"""
    
    content = content.replace(old_do, new_do, 1)
    print("  Added per-column update in do_getm_fabm")
    
    # 5. Need to add kk variable declaration in do_getm_fabm
    # Find the local variable declaration section in do_getm_fabm
    old_declare = "   integer                   :: i,j,n"
    new_declare = "   integer                   :: i,j,n,kk"
    # Only replace the first occurrence in do_getm_fabm (there might be multiple)
    # Let's be more specific - find the one near do_getm_fabm
    do_pos = content.find("subroutine do_getm_fabm")
    if do_pos > 0:
        decl_pos = content.find(old_declare, do_pos)
        if decl_pos > 0:
            content = content[:decl_pos] + new_declare + content[decl_pos+len(old_declare):]
            print("  Added kk to do_getm_fabm local variables")
        else:
            print("  WARNING: Could not find variable declaration in do_getm_fabm")
    else:
        print("  WARNING: Could not find do_getm_fabm subroutine")
    
    with open(GETM_FABM_FILE, 'w', encoding='latin-1') as f:
        f.write(content)
    
    print(f"\nPatched file: {GETM_FABM_FILE}")
    print("Done.")

if __name__ == "__main__":
    apply_patch()
