"""Initial condition presets for 3DWET.

Three trophic state presets based on PCLake+ defaults and Chinese lake water quality standards.
"""

# 中营养湖 (Mesotrophic) - 参考 PCLake Clear state
MESOTROPHIC = {
    # 营养盐 (Class II-III water quality)
    'sNH4W': 0.10, 'sNO3W': 0.30, 'sPO4W': 0.02,
    'sO2W': 8.0, 'sSiO2W': 2.0,
    # 浮游植物 (low biomass)
    'diatoms_sDW': 0.10, 'greens_sDW': 0.08, 'cyanobacteria_sDW': 0.05,
    # 浮游动物
    'cladocerans_sD': 0.15, 'copepods_sD': 0.15,
    # 鱼类 (low density)
    'JuFish_sD': 0.10, 'AdFish_sD': 0.25, 'PiscFish_sD': 0.03,
    # 其他
    'zoobenthos_sD': 0.25, 'POM_sDW': 2.0, 'DOM_sDW': 5.0,
}

# 富营养湖 (Eutrophic) - 参考 PCLake Turbid state, 异龙湖验证版
EUTROPHIC = {
    # 营养盐 (Class IV-V water quality)
    'sNH4W': 0.30, 'sNO3W': 1.00, 'sPO4W': 0.06,
    'sO2W': 10.0, 'sSiO2W': 3.5,
    # 浮游植物 (moderate-high biomass)
    'diatoms_sDW': 0.30, 'greens_sDW': 0.20, 'cyanobacteria_sDW': 0.30,
    # 浮游动物 (raised to avoid cascade crash)
    'cladocerans_sD': 0.30, 'copepods_sD': 0.30,
    # 鱼类 (lowered 50% to reduce predation)
    'JuFish_sD': 0.15, 'AdFish_sD': 0.40, 'PiscFish_sD': 0.05,
    # 其他
    'zoobenthos_sD': 0.40, 'POM_sDW': 5.0, 'DOM_sDW': 10.0,
}

# 重富营养湖 (Hypereutrophic) - 蓝藻水华频发
HYPEREUTROPHIC = {
    # 营养盐 (worse than Class V)
    'sNH4W': 0.80, 'sNO3W': 2.00, 'sPO4W': 0.15,
    'sO2W': 12.0, 'sSiO2W': 5.0,
    # 浮游植物 (high biomass, cyanobacteria dominant)
    'diatoms_sDW': 0.50, 'greens_sDW': 0.30, 'cyanobacteria_sDW': 0.80,
    # 浮游动物
    'cladocerans_sD': 0.40, 'copepods_sD': 0.35,
    # 鱼类
    'JuFish_sD': 0.20, 'AdFish_sD': 0.50, 'PiscFish_sD': 0.08,
    # 其他
    'zoobenthos_sD': 0.50, 'POM_sDW': 8.0, 'DOM_sDW': 15.0,
}

PRESETS = {
    'mesotrophic': MESOTROPHIC,
    'eutrophic': EUTROPHIC,
    'hypereutrophic': HYPEREUTROPHIC,
}
