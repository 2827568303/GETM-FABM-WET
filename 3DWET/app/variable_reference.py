"""Chinese output semantics and provenance-bearing, chemically comparable references.

Registry labels come from WET variable registrations, not sampled output values.
Initial conditions are a comparison baseline, never an environmental target.
"""
from functools import lru_cache
import json
import math
from pathlib import Path
import re

import yaml

APP = Path(__file__).resolve().parent
STANDARD_URL = 'https://www.mee.gov.cn/gkml/hbb/bgth/200910/W020090724340379457140.pdf'
OVERRIDE_FILE = 'variable_references.json'


@lru_cache(maxsize=96)
def _read_cached(path, stamp, size):
    text = Path(path).read_text(encoding='utf-8-sig')
    return yaml.safe_load(text) if Path(path).suffix in ('.yaml', '.yml') else json.loads(text)


def _read(path):
    path = Path(path)
    try:
        stat = path.stat()
        return _read_cached(str(path.resolve()), stat.st_mtime_ns, stat.st_size) or {}
    except (OSError, ValueError, yaml.YAMLError):
        return {}


def _unit(unit):
    text = str(unit or '').strip().lower().replace('³', '3').replace('²', '2').replace('^', '').replace(' ', '')
    return {'meters': 'm', 'meter': 'm', 'celsius': 'degc', 'degrees_celsius': 'degc', '°c': 'degc', 'degc': 'degc', '1': '-', 'dimensionless': '-'}.get(text, text)


def _finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


_MODELS = {
    'POM': 'om_pool', 'DOM': 'om_pool', 'humus': 'om_pool',
    'cyanobacteria': 'phytoplankton', 'diatoms': 'phytoplankton', 'greens': 'phytoplankton',
    'cladocerans': 'zooplankton', 'copepods': 'zooplankton',
    'JuFish': 'fish', 'AdFish': 'fish', 'PiscFish': 'fish',
}
_GROUPS = {
    'abiotic_water': '水体非生物过程', 'abiotic_sediment': '沉积物非生物过程',
    'bot_pel_interface': '水底界面', 'sediment_exchange': '沉积物与水体交换', 'burial': '沉积物埋藏',
    'POM': '颗粒有机物', 'DOM': '溶解有机物', 'humus': '腐殖质', 'om_pool': '有机物库',
    'cyanobacteria': '蓝藻', 'diatoms': '硅藻', 'greens': '绿藻', 'phytoplankton': '浮游植物',
    'cladocerans': '枝角类', 'copepods': '桡足类', 'zooplankton': '浮游动物',
    'zoobenthos': '底栖动物', 'bivalves': '双壳类', 'macrophytes': '水生植物',
    'JuFish': '浮游食性幼鱼', 'AdFish': '底栖食性成鱼', 'PiscFish': '食鱼性鱼', 'fish': '鱼类',
    'inorganic_carbon': '无机碳', 'methane': '甲烷', 'resus_sed': '沉积物再悬浮',
}
_HYDRO = {
    'hcc': ('静水一致性指标', '地形跟随网格相邻层面坡度与层厚比形成的静水一致性诊断指标'),
    'tke': ('湍动能', '单位质量水体的湍动能'),
    'num': ('湍流黏性系数', '湍流闭合方案给出的垂向动量扩散黏性系数'),
    'nuh': ('湍流扩散系数', '湍流闭合方案给出的垂向标量扩散系数'),
    'diss': ('湍动能耗散率', '湍动能向热能转化的单位质量耗散速率'),
    'temp': ('水温', '水体温度'), 'salt': ('盐度', '水体实用盐度'),
    'elev': ('水面高程', '相对于模型高程基准的自由水面位置'), 'z': ('水面高程', '相对于模型高程基准的自由水面位置'),
    'D': ('水深', '当前自由水面至湖床的水柱深度'), 'hn': ('水层厚度', '模型垂向网格单层厚度'),
    'zc': ('水层中心高程', '模型垂向网格层中心坐标'),
    'u': ('东西向流速', '沿模型东西向坐标的有符号流速分量'),
    'v': ('南北向流速', '沿模型南北向坐标的有符号流速分量'),
    'w': ('垂向流速', '模型垂向有符号流速分量'), 'uu': ('东西向流速', '三维东西向流速分量'),
    'vv': ('南北向流速', '三维南北向流速分量'),
    'convc': ('网格旋转角', '模型网格与地理坐标的旋转角'),
    'latu': ('东西向速度点纬度', '交错网格上东西向速度节点纬度'),
    'latv': ('南北向速度点纬度', '交错网格上南北向速度节点纬度'),
    'lonu': ('东西向速度点经度', '交错网格上东西向速度节点经度'),
    'lonv': ('南北向速度点经度', '交错网格上南北向速度节点经度'),
    'bathymetry': ('地形水深', '地形文件定义的静态湖床水深'),
    'lon': ('经度', '网格经度坐标'), 'lat': ('纬度', '网格纬度坐标'),
    'time': ('模拟时间', '输出记录的模型时间'), 'sigma': ('垂向相对坐标', '垂向网格的无量纲相对坐标'),
}
_HYDRO_EN = {
    'hcc': ('Hydrostatic consistency indicator', 'Ratio of adjacent terrain-following layer slopes to layer thickness'),
    'tke': ('Turbulent kinetic energy', 'Turbulent kinetic energy per unit water mass'),
    'num': ('Turbulent viscosity', 'Vertical momentum diffusivity from the turbulence closure'),
    'nuh': ('Turbulent diffusivity', 'Vertical scalar diffusivity from the turbulence closure'),
    'diss': ('Turbulent energy dissipation rate', 'Rate of turbulent kinetic energy dissipation per unit water mass'),
    'temp': ('Water temperature', 'Temperature of the water column'),
    'salt': ('Salinity', 'Practical salinity of the water column'),
    'elev': ('Water surface elevation', 'Free-surface position relative to the model elevation datum'),
    'z': ('Water surface elevation', 'Free-surface position relative to the model elevation datum'),
    'D': ('Water depth', 'Water-column depth from the bed to the current free surface'),
    'hn': ('Layer thickness', 'Thickness of one vertical model layer'),
    'zc': ('Layer center elevation', 'Vertical coordinate of the model layer center'),
    'u': ('Zonal velocity', 'Signed velocity component along the model east-west coordinate'),
    'v': ('Meridional velocity', 'Signed velocity component along the model north-south coordinate'),
    'w': ('Vertical velocity', 'Signed vertical velocity component'),
    'uu': ('Zonal velocity', 'Three-dimensional zonal velocity component'),
    'vv': ('Meridional velocity', 'Three-dimensional meridional velocity component'),
    'convc': ('Grid rotation angle', 'Rotation between model grid and geographic coordinates'),
    'latu': ('Latitude at u points', 'Latitude of zonal velocity nodes on the staggered grid'),
    'latv': ('Latitude at v points', 'Latitude of meridional velocity nodes on the staggered grid'),
    'lonu': ('Longitude at u points', 'Longitude of zonal velocity nodes on the staggered grid'),
    'lonv': ('Longitude at v points', 'Longitude of meridional velocity nodes on the staggered grid'),
    'bathymetry': ('Bathymetric depth', 'Static bed depth defined by the bathymetry file'),
    'lon': ('Longitude', 'Longitude coordinate of the model grid'),
    'lat': ('Latitude', 'Latitude coordinate of the model grid'),
    'time': ('Simulation time', 'Model time of the output record'),
    'sigma': ('Relative vertical coordinate', 'Dimensionless relative coordinate of the vertical grid'),
}
_TOTALS_EN = {
    'total_aCovVeg_calculator_result': 'Total macrophyte coverage',
    'total_aDSubVeg_calculator_result': 'Total submerged macrophyte dry weight',
    'wet_fish_totD_calculator_result': 'Total fish dry weight',
    'total_bioturbation_calculator_result': 'Total bioturbation',
    'total_macrophyte_biomass_calculator_result': 'Total macrophyte biomass',
    'total_afCovSurfVeg_calculator_result': 'Total surface macrophyte cover fraction',
    'wet_totP_calculator_result': 'Total phosphorus aggregation diagnostic',
    'wet_totN_calculator_result': 'Total nitrogen aggregation diagnostic',
    'wet_chla_calculator_result': 'Total chlorophyll a concentration',
    'wet_totSusPar_calculator_result': 'Total suspended particulate concentration',
    'wet_totC_calculator_result': 'Total carbon aggregation diagnostic',
}


def _english(text, fallback):
    """Keep supplied English text; do not invent translations of custom prose."""
    text = str(text or '').strip()
    return text if text and not re.search(r'[\u3400-\u9fff]', text) else fallback


def _reference_english(reference):
    """Add language-specific prose without changing reference values or selection."""
    kind = reference['kind']
    defaults = {
        'unset': ('No reference configured', 'No applicable reference',
                  'No universal normal value applies. Configure a source-backed reference for this case. Zero process flux does not mean normal; signs follow the model definition.'),
        'initial': ('Case initial value (comparison baseline)', _english(reference.get('source'), 'Case initialization'),
                    'Initial configuration is a baseline for relative change, not a normal range or water-quality limit.'),
        'standard': ({'地表水Ⅲ类 pH范围': 'Class III surface-water pH range',
                      '地表水Ⅲ类溶解氧下限': 'Class III dissolved oxygen minimum',
                      '地表水Ⅲ类湖库总磷上限': 'Class III lake/reservoir total phosphorus maximum',
                      '地表水Ⅲ类湖库总氮上限': 'Class III lake/reservoir total nitrogen maximum'}.get(reference.get('label'), 'Class III surface-water reference'),
                     'GB 3838-2002, Table 1, Class III (lakes/reservoirs)',
                     'Environmental quality target for comparable surface-water quantities. Not applicable to sediment, individual nutrient species or process fluxes.'),
        'custom': (_english(reference.get('label'), 'User-defined reference'),
                   _english(reference.get('source'), 'User configuration'),
                   _english(reference.get('note'), 'User-defined comparison reference. Applicability depends on the stated source and case conditions.')),
    }
    label, source, note = defaults[kind]
    return dict(reference, label_en=_english(reference.get('label_en'), label),
                source_en=_english(reference.get('source_en'), source), note_en=_english(reference.get('note_en'), note))
_SPECIAL = {
    'BTdummy': '生物扰动占位量', 'TMdummy': '水生植物总量占位量',
    'aDSubVegdummy': '沉水植物干重占位量', 'aCovVegdummy': '植物覆盖率占位量',
    'afCovSurfVegdummy': '水面植物覆盖比例占位量', 'chladummy': '叶绿素a占位量',
    'pred_dummy': '捕食占位量', 'tDpseudofaecesBiv': '干重假粪产生速率',
    'f_food': '食物限制函数', 'f_temp': '温度限制函数', 'f_dens': '密度限制函数',
    'f_SS': '悬浮无机物限制函数', 'f_DOmort': '溶解氧致死响应函数', 'Imax': '最大潜在摄食速率',
    'extinction': '消光贡献', 'ext': '浮游植物消光因子', 'macroextinction': '水生植物消光贡献',
    'bfRootVeg_PV': '根系分配比例（水体映射）',
    'aDSubVeg_PV': '沉水部分干重（水体映射）', 'aCovVeg_PV': '植物覆盖率（水体映射）',
    'afCovSurfVeg_PV': '水面植物覆盖比例（水体映射）',
    'aDayInitVeg': '植物季节生长起始日', 'aDSubVeg': '沉水部分干重', 'aCovVeg': '植物覆盖率',
    'afCovSurfVeg': '水面植物覆盖比例', 'aLPAR1Veg': '植物冠层顶部光合有效辐射',
    'aLPAR2Veg': '植物冠层底部光合有效辐射', 'ufDay': '日照时长', 'aMuVeg': '干重实际比生长率',
    'Bioturbation': '生物扰动强度', 'oSiW': '水体硅浓度诊断量', 'oSiS': '沉积物硅存量诊断量',
    'pCO2W': '水体二氧化碳分压', 'sHCO3W': '水体碳酸氢根碳浓度', 'sCO3W': '水体碳酸根碳浓度',
    'k600': '施密特数600条件下气体交换速度',
    'extIM': '无机颗粒消光贡献', 'extPOM': '颗粒有机物消光贡献',
    'pO2Sat': '溶解氧饱和度', 'wind': '风速', 'pH': '水体酸碱度', 'ph': '水体酸碱度',
    'bot_pel_conv': '底栖面密度与水体体积浓度换算系数',
    'afOxySed': '好氧沉积物比例', 'aPEqIMS': '无机物平衡吸附磷酸盐', 'fPEqIMS': '吸附磷处于平衡的比例',
    'bPorS': '沉积物孔隙率', 'bPorCorS': '按曲折度修正的沉积物孔隙率',
    'cDepthS': '沉积物厚度', 'fDepthDifS': '沉积物扩散距离',
    'aFunTauTmSet': '基础沉降速率因子', 'tDResusDead': '死亡有机物再悬浮诊断量',
    'Day_last': '上一步模拟日', 'PStar': '规避捕食风险行为程度',
    'meanparout': '平均光合有效辐射', 'Swim': '游动速度', 'chla': '叶绿素a浓度',
    'fVul': '易受捕食生物量比例', 'sFRes': '储备生物量', 'sDSiz': '平均个体干重',
    'sAlkW': '水体总碱度', 'sDICW': '水体溶解无机碳浓度', 'sCH4W': '水体甲烷碳浓度',
}
_TOTALS = {
    'total_aCovVeg_calculator_result': '水生植物总覆盖率',
    'total_aDSubVeg_calculator_result': '沉水植物总干重',
    'wet_fish_totD_calculator_result': '鱼类总干重',
    'total_bioturbation_calculator_result': '总生物扰动强度',
    'total_macrophyte_biomass_calculator_result': '水生植物总生物量',
    'total_afCovSurfVeg_calculator_result': '水面植物总覆盖比例',
    'wet_totP_calculator_result': '总磷汇总诊断量', 'wet_totN_calculator_result': '总氮汇总诊断量',
    'wet_chla_calculator_result': '总叶绿素a浓度', 'wet_totSusPar_calculator_result': '总悬浮颗粒浓度',
    'wet_totC_calculator_result': '总碳汇总诊断量',
}


def _identity(name, case_path):
    instances = _read(Path(case_path) / 'fabm.yaml').get('instances', {}) if case_path else {}
    for group in sorted(set(instances) | set(_GROUPS), key=len, reverse=True):
        for separator in ('_', '/'):
            if name.startswith(group + separator):
                item = instances.get(group, {}) or {}
                model = item.get('model', 'wet/' + _MODELS.get(group, group))
                return group, name[len(group) + 1:], model, item
    return '', name, '', {}


def _record(model, local):
    registry = _read(APP / 'variable_registry.json').get(model, {})
    if local in registry:
        return registry[local]
    for key, record in registry.items():
        if key.endswith('*') and local.startswith(key[:-1]) and local[len(key)-1:].isdigit():
            return record
    docs = _read(APP / 'fabm_docs.json').get(model, {}).get('variables', {})
    return dict(docs[local], kind='state_variable') if local in docs else {}


_ELEMENTS = {'D': '干重', 'N': '氮', 'P': '磷', 'C': '碳', 'Si': '硅', 'O2': '氧'}
_PROCESS = [
    ('Nitr', '硝化'), ('Denit', '反硝化'), ('Resus', '再悬浮'), ('Sed', '沉降'), ('Set', '沉降'),
    ('Dif', '扩散'), ('Exch', '交换'), ('Bur', '埋藏'), ('Sorp', '吸附'), ('Chem', '化学固定'),
    ('Cons', '摄食'), ('Eges', '排粪'), ('Excr', '排泄'), ('Resp', '呼吸'), ('Mort', '死亡'),
    ('Ass', '同化'), ('Upt', '吸收'), ('Fix', '固氮'), ('Prod', '产生'), ('Min', '矿化'),
    ('Migr', '迁移'), ('Age', '成熟'), ('Repro', '繁殖'), ('Repr', '繁殖'), ('Aer', '复氧'),
    ('Trans', '转移'), ('Abio', '非生物过程更新'),
    ('Refr', '腐殖化'), ('Bed', '水底交换'),
]
_SUBSTANCES = [('SiO2', '溶解硅'), ('SiPa', '颗粒硅'), ('PAIM', '无机颗粒吸附磷'),
               ('PO4', '磷酸盐'), ('NH4', '铵态氮'), ('NO3', '硝态氮'), ('CO2', '二氧化碳'),
               ('CH4', '甲烷'), ('DIC', '溶解无机碳'), ('O2', '氧'), ('POM', '颗粒有机物'),
               ('DOM', '溶解有机物'), ('Hum', '腐殖质'), ('IM', '无机物')]


def _semantic(local, record, group, units):
    if local in _SPECIAL:
        return _SPECIAL[local]
    label = record.get('label', '')
    if local.startswith('s'):
        for code, zh in _SUBSTANCES:
            if code in local:
                return zh + ('浓度' if '/m3' in _unit(units) else '存量')
        match = re.match(r's([DNPC])([WS]?)(_PV)?$', local)
        if match:
            return _ELEMENTS[match[1]] + ('水体映射库' if match[3] else '生物量或有机物存量')
    if local.startswith('r') and re.search(r'[PNC]D', local):
        element = re.search(r'([PNC])D', local)[1]
        return _ELEMENTS[element] + '与干重比'
    if 'Lim' in local:
        token = re.search(r'(Nut|Si|N|P|L|T)Lim', local)
        return ({'Nut': '营养盐', 'Si': '硅', 'N': '氮', 'P': '磷', 'L': '光照', 'T': '温度'}.get(token[1] if token else '', '') + '限制因子')
    if 'FeedLvl' in local:
        return '摄食水平'
    if local in ('fFishPlan', 'fFishBent', 'fFishPisc'):
        return {'fFishPlan': '浮游食性觅食时间比例', 'fFishBent': '底栖食性觅食时间比例', 'fFishPisc': '食鱼觅食时间比例'}[local]
    if local.startswith(('t', 'w')):
        element_match = re.match(r'[tw](Si|O2|D|N|P|C)', local)
        element = _ELEMENTS.get(element_match[1], '') if element_match else ''
        process = next((zh for code, zh in _PROCESS if code in local), '')
        if not process:
            process = next((zh for english, zh in [('egest', '排粪'), ('excret', '排泄'), ('diffus', '扩散'), ('exchange', '交换')]
                            if english in label.lower()), '')
        substance = next((zh for code, zh in _SUBSTANCES if code in local), '')
        if process or substance:
            if 'Cons' in local:
                substance = next((zh for code, zh in [('Plan', '浮游猎物'), ('Bent', '底栖猎物'), ('Pisc', '鱼类猎物')]
                                  if code in local), substance)
            return substance + element + (process or '收支') + '速率'
    # Translate genuine source definitions without inferring a chemical species.
    phrases = {
        'fraction of aerobic sediment': '好氧沉积物比例', 'oxygen stress fraction': '氧胁迫比例',
        'extinction coefficient': '消光系数', 'sediment turnover depth': '沉积物更新厚度',
        'oxygen saturation': '溶解氧饱和度', 'windspeed': '风速', 'chlorophyll': '叶绿素浓度',
        'water filtration rate': '滤水速率', 'weight': '个体重量',
    }
    for phrase, zh in phrases.items():
        if phrase in label.lower():
            return zh
    glossary = _read(APP / 'fabm_glossary.json').get('vars', {})
    if local in glossary:
        return glossary[local]
    return ''


def _unset(unit):
    return {'kind': 'unset', 'label': '未设参考值', 'unit': unit, 'source': '', 'source_url': '',
            'note': '该量没有可直接适用的通用正常值；可配置有来源的自定义参考。过程通量的零值不代表正常，正负方向须按模型定义解释。'}


def _standard(name, local, group, units, long_name):
    u = _unit(units)
    # Only explicit water compartment identities are permitted.
    if any(word in (name + ' ' + long_name).lower() for word in ('sediment', 'bottom', 'pore', 'benthic')):
        return None
    species = None
    if (group == 'abiotic_water' and local == 'sO2W') or name in ('dissolved_oxygen', 'water_dissolved_oxygen'):
        species = 'O2'
    elif name in ('total_phosphorus', 'water_total_phosphorus') and 'water' in long_name.lower():
        species = 'P'
    elif name in ('total_nitrogen', 'water_total_nitrogen') and 'water' in long_name.lower():
        species = 'N'
    elif (group == 'inorganic_carbon' and local in ('pH', 'ph')) or name == 'water_pH':
        if u not in ('-', 'ph'):
            return None
        return {'lower': 6, 'upper': 9, 'label': '地表水Ⅲ类 pH范围'}
    if species:
        allowed = {f'g{species.lower()}/m3': 1, f'mg{species.lower()}/l': 1,
                   f'mg{species.lower()}/m3': 1000}
        # A known species' registered g/m3 explicitly measures that species.
        allowed.update({'g/m3': 1, 'mg/l': 1, 'mg/m3': 1000})
        if u not in allowed:
            return None
        value = {'O2': 5, 'P': .05, 'N': 1}[species] * allowed[u]
        return {('lower' if species == 'O2' else 'upper'): value,
                'label': '地表水Ⅲ类' + {'O2': '溶解氧下限', 'P': '湖库总磷上限', 'N': '湖库总氮上限'}[species]}
    return None


@lru_cache(maxsize=64)
def _namelist_constants(path, stamp, size):
    text = Path(path).read_text(encoding='utf-8-sig')
    text = re.sub(r'!.*', '', text)
    return {key.lower(): float(number.replace('D', 'e').replace('d', 'e'))
            for key, number in re.findall(r'\b(temp_method|temp_const|elev_method|elev_const)\s*=\s*([-+]?\d+(?:\.\d*)?(?:[eEdD][-+]?\d+)?)', text)}


def _initial(name, local, item, record, units, case_path):
    if not case_path:
        return None
    if record.get('kind') in ('state_variable', 'bottom_state_variable') and _unit(record.get('units')) == _unit(units):
        value = item.get('initialization', {}).get(local)
        source = 'fabm.yaml / initialization'
        if value is None:
            initial = _read(Path(case_path) / 'initial_conditions.json')
            # Only exact numeric variable entries, never trophic presets or group totals.
            value = initial.get(name)
            if value is None:
                value = initial.get('variables', {}).get(name) if isinstance(initial.get('variables'), dict) else None
            source = 'initial_conditions.json / exact variable'
        if _finite(value):
            return value, source
    if name in ('temp', 'elev', 'z') and _unit(units) == ('degc' if name == 'temp' else 'm'):
        path = Path(case_path) / 'getm.inp'
        try:
            stat = path.stat()
            constants = _namelist_constants(str(path.resolve()), stat.st_mtime_ns, stat.st_size)
        except (OSError, ValueError):
            return None
        prefix = 'temp' if name == 'temp' else 'elev'
        value = constants.get(prefix + '_const')
        if constants.get(prefix + '_method', 1) == 1 and _finite(value):
            return value, 'getm.inp / ' + prefix + '_const'
    return None


def _validate_reference(data, expected_unit=None):
    if not isinstance(data, dict):
        raise ValueError('参考值必须是对象')
    unit = str(data.get('unit', data.get('units', ''))).strip()
    if not unit and expected_unit != '':
        raise ValueError('必须填写与输出变量一致的单位')
    if expected_unit is not None and _unit(unit) != _unit(expected_unit):
        raise ValueError('参考值单位与输出变量不一致')
    numbers = {key: data[key] for key in ('value', 'lower', 'upper') if data.get(key) is not None}
    if not numbers or any(not _finite(value) for value in numbers.values()):
        raise ValueError('参考值必须包含有限数值')
    if 'lower' in numbers and 'upper' in numbers and numbers['upper'] < numbers['lower']:
        raise ValueError('参考上限不能低于下限')
    reference = dict(numbers, kind='custom', unit=unit, label=str(data.get('label') or '用户自定义参考'),
                source=str(data.get('source') or '用户配置'), source_url=str(data.get('source_url') or ''),
                note=str(data.get('note') or '用户指定参考；适用性由所填来源和使用场景决定。'))
    reference.update({key: data[key] for key in ('label_en', 'source_en', 'note_en') if key in data})
    return _reference_english(reference)


def save_reference(case_path, name, data, *, expected_units=None):
    """Save a reference matching trusted native units, or registry units if omitted.

    The API supplies expected_units from the actual result variable. No numeric
    conversion occurs, even when two different unit strings are equivalent.
    """
    if not isinstance(name, str) or not name.strip():
        raise ValueError('变量名不能为空')
    group, local, model, item = _identity(name, case_path)
    record = _record(model, local)
    expected = record.get('units')
    if name in ('temp',):
        expected = 'Celsius'
    elif name in ('elev', 'z', 'D', 'hn', 'zc'):
        expected = 'm'
    if expected_units is not None:
        expected = expected_units
    reset = isinstance(data, dict) and data.get('reset') is True
    saved = {'kind': 'reset'} if reset else _validate_reference(data, expected)
    path = Path(case_path) / OVERRIDE_FILE
    current = _read(path)
    current = dict(current) if isinstance(current, dict) else {}
    if reset:
        current.pop(name, None)
    else:
        current[name] = saved
    temporary = path.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(current, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    temporary.replace(path)
    return saved


def describe_variable(name, units='', long_name='', case_path=None):
    """Describe one native output field without reading result arrays."""
    name, units, long_name = str(name), str(units or ''), str(long_name or '')
    group, local, model, item = _identity(name, case_path)
    record = _record(model, local)
    label = record.get('label') or long_name or name
    state = record.get('kind') in ('state_variable', 'bottom_state_variable')
    rate = bool(re.match(r'[tw][DNPC]|[tw]Si|[tw]O2', local)) or bool(re.search(r'/(s|d|sec|day)$', _unit(units)))
    category = '水动力' if name in _HYDRO else ('状态量' if state else ('过程速率/通量' if rate else '诊断量'))
    if name in _HYDRO:
        zh_name, semantic = _HYDRO[name]
    else:
        semantic = _TOTALS.get(name) or _semantic(local, record, group, units)
        if semantic:
            for repeated in ('氧氧', '铵态氮氮', '硝态氮氮', '磷酸盐磷'):
                semantic = semantic.replace(repeated, repeated[:-1])
        prefix = _GROUPS.get(group, _GROUPS.get(model.removeprefix('wet/'), group))
        zh_name = (prefix + '：' if prefix else '') + (semantic or '未收录变量（' + name + '）')
    location = ('沉积物/底栖' if ('sediment' in model or group in ('burial', 'zoobenthos', 'bivalves') or local.endswith('S'))
                else '水体' if group and group not in ('sediment_exchange', 'bot_pel_interface', 'macrophytes') else '模型定义的空间位置')
    meaning = f'{semantic or "中文语义尚未收录"}；{location}的{category}。原始定义：{label}。单位：{units or "未提供"}。'
    if rate:
        meaning += '正负符号表示模型定义的收支或交换方向；具体方向以原始过程定义为准。'
    source_label_en = _english(label, _english(name, 'Unnamed output variable'))
    category_en = 'Hydrodynamic quantity' if name in _HYDRO else ('State variable' if state else ('Process rate/flux' if rate else 'Diagnostic quantity'))
    if name in _HYDRO_EN:
        en_name, definition_en = _HYDRO_EN[name]
    elif name in _TOTALS_EN:
        en_name = definition_en = _TOTALS_EN[name]
    elif record:
        group_en = _english(item.get('long_name'), _english(group.replace('_', ' '), 'Model component'))
        en_name = f'{group_en}: {source_label_en}' if group else source_label_en
        definition_en = f'Source definition: {source_label_en}'
    else:
        en_name = _english(long_name, _english(name, 'Unnamed output variable'))
        definition_en = f'Unknown variable definition: no registered semantic mapping is available. Supplied definition: {en_name}'
    location_en = {'沉积物/底栖': 'sediment/benthic compartment', '水体': 'water column',
                   '模型定义的空间位置': 'model-defined spatial location'}[location]
    meaning_en = f'{definition_en}; {category_en} in the {location_en}. Units: {_english(units, "not provided")}. '
    if rate:
        meaning_en += 'Positive and negative signs follow the model-defined balance or exchange direction; consult the source process definition.'
    reference = None
    overrides = _read(Path(case_path) / OVERRIDE_FILE) if case_path else {}
    if name in overrides:
        try:
            reference = _validate_reference(overrides[name], units)
        except ValueError:
            reference = None
    if reference is None:
        standard = _standard(name, local, group, units, long_name)
        if standard:
            reference = dict(standard, kind='standard', unit=units, source='GB 3838—2002 表1 Ⅲ类（湖库）',
                             source_url=STANDARD_URL, note='环境质量目标参考，适用于可比的地表水水体浓度；不能直接用于沉积物、单一营养盐形态或过程通量。')
    if reference is None:
        initial = _initial(name, local, item, record, units, case_path)
        if initial:
            reference = {'kind': 'initial', 'label': '本案例初始值（对比基线）', 'value': initial[0], 'unit': units,
                         'source': initial[1], 'source_url': '', 'note': '初始配置用于比较相对变化，不表示正常范围或水质达标限值。'}
    return {'zh_name': zh_name, 'meaning': meaning, 'en_name': en_name, 'meaning_en': meaning_en.strip(),
            'category': category, 'category_en': category_en,
            'reference': _reference_english(reference or _unset(units))}


def annotate_variables(items, case_path=None):
    """Return annotated copies, preserving native names and every original field."""
    return [dict(item, **describe_variable(item['name'], item.get('units', ''), item.get('long_name', ''), case_path)) for item in items]
