"""Copy fabm.yaml from Theoretical lake and modify initial conditions for Yilong Lake.

Key changes (fixing cascade crash from previous run):
1. Phytoplankton: raise from 0.05 to 0.3 (PCLake Turbid defaults)
   - diatoms: 0.3, greens: 0.2, cyanobacteria: 0.3
2. Zooplankton: raise from 0.1 to 0.3 (avoid starvation)
   - cladocerans: 0.3, copepods: 0.3
3. Fish: lower by 50% (reduce predation pressure on zooplankton)
   - JuFish: 0.15, AdFish: 0.40, PiscFish: 0.05
4. Nutrients: moderate eutrophic (Yilong eutrophic)
   - NH4W: 0.30, NO3W: 1.0, PO4W: 0.06
"""
import os
import re

SRC = '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Theoretical lake/fabm.yaml'
DST = '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Yilong/fabm.yaml'

with open(SRC, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Diatom initial: sDW 0.05 -> 0.3, sNW/sPW scaled
# Find diatom section (after 'diatoms:' instance)
# Use line-based replacements with context

# Replace diatom init
content = content.replace(
    "      sDW: 0.05                                                  # water column DW (gDW/m3) - lowered from 0.5 (PCLake default ~0.015)\n      sNW: 0.0025                                                # water column N (gN/m3) - scaled with sDW\n      sPW: 0.00025                                               # water column P (gP/m3) - scaled with sDW\n      sCW: 0.20                                                  # water column C (gC/m3)",
    "      sDW: 0.30                                                  # water column DW (gDW/m3) - raised for Yilong (PCLake Turbid diatom ~0.3)\n      sNW: 0.015                                                 # water column N (gN/m3) - scaled with sDW (N/C=0.05)\n      sPW: 0.0015                                                # water column P (gP/m3) - scaled with sDW (P/C=0.005)\n      sCW: 0.20                                                  # water column C (gC/m3)"
)

# Replace greens init (same pattern, slightly lower than diatom)
content = content.replace(
    "      sDW: 0.05                                                  # water column DW (gDW/m3) - lowered from 0.3 (PCLake default ~0.028)\n      sNW: 0.0025                                                # water column N (gN/m3) - scaled with sDW\n      sPW: 0.00025                                               # water column P (gP/m3) - scaled with sDW\n      sCW: 0.12                                                  # water column C (gC/m3)",
    "      sDW: 0.20                                                  # water column DW (gDW/m3) - raised for Yilong (PCLake green ~0.2)\n      sNW: 0.010                                                 # water column N (gN/m3) - scaled with sDW\n      sPW: 0.0010                                                # water column P (gP/m3) - scaled with sDW\n      sCW: 0.12                                                  # water column C (gC/m3)"
)

# Replace cyanobacteria init (line 509-516)
content = content.replace(
    "      sDW: 0.1                                                   # water column DW (gDW/m3)\n      sNW: 0.03                                                  # water column N (gN/m3)\n      sPW: 0.003                                                 # water column P (gP/m3)\n      sCW: 0.040                                                 # water column C (gC/m3)",
    "      sDW: 0.30                                                  # water column DW (gDW/m3) - raised for Yilong (eutrophic, blue-green dominant)\n      sNW: 0.015                                                 # water column N (gN/m3)\n      sPW: 0.0015                                                # water column P (gP/m3)\n      sCW: 0.040                                                 # water column C (gC/m3)"
)

# 2. Zooplankton: raise from 0.1 to 0.3 (two zooplankton groups)
# cladocerans (line 801): sD: 0.1 -> 0.3
content = content.replace(
    "      sD: 0.1                                                    # DW (gDW/m3) - mesotrophic\n      sND: 0.01",
    "      sD: 0.30                                                   # DW (gDW/m3) - raised for Yilong (avoid zooplankton starvation)\n      sND: 0.01"
)
# copepods (line 866): same pattern
content = content.replace(
    "      sD: 0.1                                                    # DW (gDW/m3) - mesotrophic\n      sND: 0.012",
    "      sD: 0.30                                                   # DW (gDW/m3) - raised for Yilong (avoid zooplankton starvation)\n      sND: 0.012"
)

# 3. Fish: lower by 50% to reduce predation pressure
# JuFish (line 1009): 0.30 -> 0.15
content = content.replace(
    "      sD: 0.30                                                   # DW (gDW/m3) - Luomahu juvenile fish",
    "      sD: 0.15                                                   # DW (gDW/m3) - Yilong, lowered 50% to reduce predation pressure"
)
# AdFish (line 1069): 0.80 -> 0.40
content = content.replace(
    "      sD: 0.80                                                   # DW (gDW/m3) - Luomahu adult benthivorous fish",
    "      sD: 0.40                                                   # DW (gDW/m3) - Yilong, lowered 50% to reduce predation pressure"
)
# PiscFish (line 1128): 0.10 -> 0.05
content = content.replace(
    "      sD: 0.10                                                   # DW (gDW/m3) - Luomahu piscivorous fish (top predator)",
    "      sD: 0.05                                                   # DW (gDW/m3) - Yilong, lowered 50% to reduce predation pressure"
)

# 4. Nutrients: moderate eutrophic (Yilong eutrophic)
# NH4W: 0.4 -> 0.30, NO3W: 0.5 -> 1.0, PO4W: 0.1 -> 0.06
content = content.replace(
    "      sNH4W: 0.4                                                 # ammonium (g/m3) - PCLake+ Turbid default: 0.426\n      sNO3W: 0.5                                                 # nitrate (g/m3) - TN ~ 1.0 (Class III)\n      sPO4W: 0.1                                                 # phosphate (g/m3) - raised from 0.03 (PCLake+ Turbid: 0.839)",
    "      sNH4W: 0.30                                                # ammonium (g/m3) - Yilong eutrophic (TN ~ 1.3, Class IV-V)\n      sNO3W: 1.0                                                 # nitrate (g/m3) - Yilong eutrophic\n      sPO4W: 0.06                                                # phosphate (g/m3) - Yilong eutrophic (TP ~ 0.08, Class III)"
)

# 5. Zoobenthos (line 930): 0.5 -> 0.4
content = content.replace(
    "      sD: 0.5                                                    # DW (gDW/m2) - mesotrophic",
    "      sD: 0.40                                                   # DW (gDW/m2) - Yilong, moderate benthos"
)

# Write
with open(DST, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"fabm.yaml written to: {DST}")

# Verify changes
with open(DST, 'r', encoding='utf-8') as f:
    new_content = f.read()

print("\n=== Verification of key changes ===")
checks = [
    ("diatoms_sDW", "sDW: 0.30", "raised for Yilong"),
    ("greens_sDW", "sDW: 0.20", "raised for Yilong"),
    ("cyanobacteria_sDW", "sDW: 0.30", "raised for Yilong"),
    ("zooplankton_sD", "sD: 0.30", "raised for Yilong"),
    ("JuFish_sD", "sD: 0.15", "lowered 50%"),
    ("AdFish_sD", "sD: 0.40", "lowered 50%"),
    ("PiscFish_sD", "sD: 0.05", "lowered 50%"),
    ("NH4W", "sNH4W: 0.30", "eutrophic"),
    ("NO3W", "sNO3W: 1.0", "eutrophic"),
    ("PO4W", "sPO4W: 0.06", "eutrophic"),
]
for name, pattern, note in checks:
    if pattern in new_content:
        print(f"  ✅ {name}: {pattern} ({note})")
    else:
        print(f"  ❌ {name}: NOT FOUND ({pattern})")
