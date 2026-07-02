#!/usr/bin/env python3
"""Patch GETM-FABM interface to add bot_pel_conv support (needed by WET model)."""
import os
import shutil

GETM_FABM_FILE = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\getm\src\3d\getm_fabm.F90"
BACKUP_FILE = GETM_FABM_FILE + ".bak_botpel"

def apply_patch():
    if not os.path.exists(BACKUP_FILE):
        shutil.copy2(GETM_FABM_FILE, BACKUP_FILE)
        print(f"Backup created: {BACKUP_FILE}")
    
    with open(GETM_FABM_FILE, 'r', encoding='latin-1') as f:
        content = f.read()
    
    # 1. Add import for type_bulk_standard_variable
    old_import = "use fabm_types,only: output_instantaneous, output_none"
    new_import = "use fabm_types,only: output_instantaneous, output_none, type_bulk_standard_variable"
    if old_import in content and new_import not in content:
        content = content.replace(old_import, new_import)
        print("Added type_bulk_standard_variable import")
    else:
        print("Import already exists or not found")
    
    # 2. Add bot_pel_conv link after link_horizontal_data for bottom_depth
    old_link = """            call model%link_horizontal_data(id_bottom_depth_below_geoid,H(i,j))
            call model%link_horizontal_data(id_bottom_depth,D(i,j))"""
    
    new_link = """            call model%link_horizontal_data(id_bottom_depth_below_geoid,H(i,j))
            call model%link_horizontal_data(id_bottom_depth,D(i,j))

!           Link bot_pel_conv (benthic-pelagic conversion factor = 1/dz)
!           Needed by WET/PCLake model for _PV (pelagic mirror) variables
            block
               REALTYPE :: bot_pel_conv_col(kmax)
               integer :: kk
               do kk=1,kmax
                  bot_pel_conv_col(kk) = _ONE_ / max(hn(i,j,kk), 1e-6_RKTYPE)
               end do
               call model%link_bulk_data(type_bulk_standard_variable(name='bot_pel_conv',units='m-1'), &
                                        bot_pel_conv_col(1:kmax))
            end block"""
    
    if old_link in content and "bot_pel_conv" not in content[content.index(old_link):content.index(old_link)+800]:
        content = content.replace(old_link, new_link, 1)
        print("Added bot_pel_conv link")
    else:
        print("bot_pel_conv link already exists or pattern not found")
    
    with open(GETM_FABM_FILE, 'w', encoding='latin-1') as f:
        f.write(content)
    
    print(f"\nPatched file: {GETM_FABM_FILE}")
    print("Done.")

if __name__ == "__main__":
    apply_patch()
