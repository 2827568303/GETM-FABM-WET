import re

with open(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\fabm_full.yaml', 'r', encoding='utf-8') as f:
    content = f.read()

old = """      DOM_C_pool_sediment: DOM/sCS                               # DOM C in sediment (g/m2)
      oxic_layer_fraction:"""

new = """      DOM_C_pool_sediment: DOM/sCS                               # DOM C in sediment (g/m2)
      DOM_DW_pool_sediment_PV: DOM/sDS_PV                        # DOM DW pel. var in sediment (g/m2)
      DOM_N_pool_sediment_PV: DOM/sNS_PV                         # DOM N pel. var in sediment (g/m2)
      DOM_P_pool_sediment_PV: DOM/sPS_PV                         # DOM P pel. var in sediment (g/m2)
      DOM_C_pool_sediment_PV: DOM/sCS_PV                         # DOM C pel. var in sediment (g/m2)
      oxic_layer_fraction:"""

content = content.replace(old, new)

old2 = """      DOM_C_pool_sediment: DOM/sCS                               # DOM C in sediment (g/m2)
      SiPa_pool_water:"""

new2 = """      DOM_C_pool_sediment: DOM/sCS                               # DOM C in sediment (g/m2)
      DOM_DW_pool_sediment_PV: DOM/sDS_PV                        # DOM DW pel. var in sediment (g/m2)
      DOM_N_pool_sediment_PV: DOM/sNS_PV                         # DOM N pel. var in sediment (g/m2)
      DOM_P_pool_sediment_PV: DOM/sPS_PV                         # DOM P pel. var in sediment (g/m2)
      DOM_C_pool_sediment_PV: DOM/sCS_PV                         # DOM C pel. var in sediment (g/m2)
      SiPa_pool_water:"""

content = content.replace(old2, new2)

old3 = """      DOM_C_pool_sediment: DOM/sCS                               # dissolved organic matter C in sediment (g/m2)
      SiO2_pool_sediment:"""

new3 = """      DOM_C_pool_sediment: DOM/sCS                               # dissolved organic matter C in sediment (g/m2)
      DOM_DW_pool_sediment_PV: DOM/sDS_PV                        # DOM DW pel. var in sediment (g/m2)
      DOM_N_pool_sediment_PV: DOM/sNS_PV                         # DOM N pel. var in sediment (g/m2)
      DOM_P_pool_sediment_PV: DOM/sPS_PV                         # DOM P pel. var in sediment (g/m2)
      DOM_C_pool_sediment_PV: DOM/sCS_PV                         # DOM C pel. var in sediment (g/m2)
      SiO2_pool_sediment:"""

content = content.replace(old3, new3)

with open(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\fabm_full.yaml', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! Added DOM_PV couplings.")
print(f"Old pattern 1 count: {content.count('DOM_DW_pool_sediment_PV: DOM/sDS_PV')}")
