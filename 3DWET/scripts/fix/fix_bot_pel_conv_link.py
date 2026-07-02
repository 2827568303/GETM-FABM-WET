#!/usr/bin/env python3
"""Fix bot_pel_conv linking: should be a horizontal scalar, not bulk array."""

FILE = r'C:\Users\dinod\Desktop\GETM-FABM-PCLake\getm\src\3d\getm_fabm.F90'

with open(FILE, 'r') as f:
    content = f.read()

# Replace the bulk link with horizontal link
old = """!     Allocate and link bot_pel_conv (benthic-pelagic conversion factor)
!     Needed by WET/PCLake model for _PV (pelagic mirror) variables
      allocate(bot_pel_conv_col(kmax))
      bot_pel_conv_col = _ONE_
      call model%link_bulk_data(type_bulk_standard_variable(name='bot_pel_conv',units='-'), &
                               bot_pel_conv_col(1:kmax))"""

new = """!     Link bot_pel_conv (benthic-pelagic conversion factor = 1/bottom_layer_thickness)
!     Needed by WET/PCLake model for _PV (pelagic mirror) variables
!     bot_pel_conv is a HORIZONTAL variable (single scalar per column), representing 1/dz at bottom
      bot_pel_conv_scalar = _ONE_ / max(hn(i,j,1), 1e-6_rk)
      call model%link_horizontal_data( &
          type_horizontal_standard_variable(name='bot_pel_conv',units='-'), &
          bot_pel_conv_scalar)"""

if old in content:
    content = content.replace(old, new)
    print("Fixed bot_pel_conv linking in init_getm_fabm")
else:
    print("WARNING: Could not find bot_pel_conv init code")
    exit(1)

# Also need to update the declaration
old_decl = "   REALTYPE, allocatable :: bot_pel_conv_col(:)"
new_decl = """   REALTYPE :: bot_pel_conv_scalar
   REALTYPE, allocatable :: bot_pel_conv_col(:)"""

if old_decl in content:
    content = content.replace(old_decl, new_decl)
    print("Added bot_pel_conv_scalar declaration")
else:
    print("WARNING: Could not find bot_pel_conv_col declaration")

with open(FILE, 'w') as f:
    f.write(content)

print("Fix applied!")
