# -*- coding: utf-8 -*-
"""鱼类（食物网顶层）模块支持 —— fabm.yaml 中 wet/fish 实例的增删。

背景
----
WET 的 ``wet/fish``（``src/wet/src/fish.F90``）一直编译在 ``bin/getm_cartesian.exe``
里（``wet_model_library.F90`` 注册 ``fish`` / ``fish_pclake``），但项目里 **所有案例
的 fabm.yaml 都没有 fish 实例**：早年为绕开 ``id_time_step`` 悬垂指针导致的
SIGSEGV（见 docs/DEBUG_HISTORY_REPORT.md §4.4），用 ``remove_fish.py`` 把
JuFish/AdFish/PiscFish 全部删掉，之后所有案例（含 GUI 建案例用的模板
``case/Lake Luoma/fabm.yaml``）都继承了这份"无鱼"配置，食物网因此缺了顶层捕食者。
现在 ``fish.F90`` 已无任何 ``time_step`` 依赖（补丁 ``patches/fish_v2_patched.F90``
已并入源码），可以安全重新启用。

本模块提供：
  * ``load_fish_template()``  —— 读取标准鱼类实例块（JuFish/AdFish/PiscFish）
  * ``toggle_fish_modules()`` —— 按当前案例的食物网组成改写 fabm.yaml
  * ``fish_case_enabled()``   —— 判断某案例是否已启用鱼类

三个鱼类实例的食物网位置（与 docs/MODEL_MODULES.md 一致）::

    PiscFish（食鱼性鱼）
        ├── AdFish（底栖食性成鱼）──→ zoobenthos
        └── JuFish（浮游食性幼鱼）──→ cladocerans / copepods
"""
from __future__ import annotations

import copy
import os
from pathlib import Path

import yaml

CODE_DIR = Path(__file__).resolve().parent.parent
MODEL_ROOT = (Path(os.environ['WET_MODEL_ROOT']).expanduser().resolve()
              if os.environ.get('WET_MODEL_ROOT') else CODE_DIR)

FISH_INSTANCES = ("JuFish", "AdFish", "PiscFish")

# 模板查找顺序：优先项目自带的精简模板，再退回 WET 上游参考配置
FISH_TEMPLATE_FILES = (
    CODE_DIR / "model_builder" / "templates" / "fish_instances.yaml",
    CODE_DIR / "src" / "wet" / "testcases" / "fabm-wet.yaml",
    MODEL_ROOT / "model_builder" / "templates" / "fish_instances.yaml",
    MODEL_ROOT / "src" / "wet" / "testcases" / "fabm-wet.yaml",
)

# 默认（模板）猎物名 → 需要按案例实际实例名重映射
_DEFAULT_PLAN_PREY = ("copepods", "cladocerans")
_DEFAULT_BENT_PREY = ("zoobenthos",)


def load_fish_template():
    """返回 {实例名: 实例字典}；找不到可用模板时返回 None。"""
    for path in FISH_TEMPLATE_FILES:
        try:
            if not path.exists():
                continue
            raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        instances = (raw or {}).get("instances") or {}
        if all(name in instances for name in FISH_INSTANCES):
            return copy.deepcopy({n: instances[n] for n in FISH_INSTANCES})
    return None


def scan_foodweb(instances):
    """按 model 类型把案例现有实例分组，用于给鱼类挑猎物。"""
    groups = {"zoos": [], "bents": [], "bivs": [], "phyts": [], "oms": [],
              "abiotic_water": None, "abiotic_sediment": None, "bot_pel": None}
    for name, inst in (instances or {}).items():
        model = str((inst or {}).get("model", ""))
        short = model.split("/")[-1]
        if short == "zooplankton":
            groups["zoos"].append(name)
        elif short == "zoobenthos":
            groups["bents"].append(name)
        elif short == "bivalves":
            groups["bivs"].append(name)
        elif short == "phytoplankton":
            groups["phyts"].append(name)
        elif short == "om_pool":
            groups["oms"].append(name)
        elif short == "abiotic_water":
            groups["abiotic_water"] = name
        elif short == "abiotic_sediment":
            groups["abiotic_sediment"] = name
        elif short == "bot_pel_interface":
            groups["bot_pel"] = name
    return groups


def _pick_prey(available, defaults, count):
    """按模板默认名优先、其余按出现顺序补齐。"""
    chosen = [n for n in defaults if n in available]
    for n in available:
        if n not in chosen:
            chosen.append(n)
    return chosen[:count]


def build_fish_instances(instances, init=None):
    """按案例现有食物网生成 3 个鱼类实例。

    返回 (fish_dict, warnings)。instances 为案例 fabm.yaml 的 instances 字典。
    """
    template = load_fish_template()
    if template is None:
        return None, ["未找到鱼类实例模板（model_builder/templates/fish_instances.yaml 或 src/wet/testcases/fabm-wet.yaml）"]

    groups = scan_foodweb(instances)
    warnings = []

    zoo_prey = _pick_prey(groups["zoos"], _DEFAULT_PLAN_PREY, 2)
    bent_prey = _pick_prey(groups["bents"] + groups["bivs"], _DEFAULT_BENT_PREY, 1)

    if not zoo_prey:
        return None, ["启用鱼类模块需要至少一个浮游动物实例（JuFish 的猎物）"]
    if not bent_prey:
        return None, ["启用鱼类模块需要至少一个底栖动物实例（AdFish 的猎物）"]
    for missing, label in (("abiotic_water", "abiotic_water"),
                           ("bot_pel", "bot_pel_interface")):
        if not groups[missing]:
            return None, [f"启用鱼类模块缺少必需实例: {label}"]
    if len(zoo_prey) < 2:
        warnings.append(f"只找到 1 个浮游动物实例（{zoo_prey[0]}），JuFish 的 nPLAN 已设为 1")

    fish = copy.deepcopy(template)
    init = init or {}

    def _apply_init(name):
        vals = init.get(name)
        if not isinstance(vals, dict):
            return
        block = fish[name].setdefault("initialization", {})
        for key, val in vals.items():
            if val is not None:
                block[key] = float(val)

    # ── JuFish：浮游食性幼鱼，捕食浮游动物 ────────────────────────────
    ju = fish["JuFish"]
    ju["parameters"]["nPLAN"] = len(zoo_prey)
    coupling = ju.setdefault("coupling", {})
    for i in range(1, 3):
        coupling.pop(f"PLANprey{i}", None)
        ju["parameters"].pop(f"cClearPlan{i}", None)
        ju["parameters"].pop(f"fGutOccPlan{i}", None)
    for i, prey in enumerate(zoo_prey, start=1):
        coupling[f"PLANprey{i}"] = prey
        ju["parameters"][f"cClearPlan{i}"] = 0.18 if i == 1 else 0.24
        ju["parameters"][f"fGutOccPlan{i}"] = 1.0

    # ── AdFish：底栖食性成鱼，捕食底栖动物 ────────────────────────────
    ad = fish["AdFish"]
    ad["parameters"]["nBEN"] = len(bent_prey)
    ad_coupling = ad.setdefault("coupling", {})
    for i in range(1, 4):
        ad_coupling.pop(f"BENTprey{i}", None)
    for i, prey in enumerate(bent_prey, start=1):
        ad_coupling[f"BENTprey{i}"] = prey

    # ── PiscFish：食鱼性鱼，捕食 JuFish / AdFish ─────────────────────
    pi = fish["PiscFish"]
    pi["parameters"]["nPISC"] = 2
    pi_coupling = pi.setdefault("coupling", {})
    pi_coupling["PISCprey1"] = "JuFish"
    pi_coupling["PISCprey2"] = "AdFish"

    for name in FISH_INSTANCES:
        _apply_init(name)
        # FABM 的 yaml 解析器不支持带引号的空串，空值参数一律省略（取源码默认）
        params = fish[name].get("parameters") or {}
        for key in [k for k, v in params.items()
                    if v is None or (isinstance(v, str) and v.strip() == "")]:
            params.pop(key)
    return fish, warnings


def fish_case_enabled(fabm_path):
    """fabm.yaml 中是否已启用鱼类模块。"""
    try:
        raw = yaml.safe_load(Path(fabm_path).read_text(encoding="utf-8")) or {}
    except Exception:
        return False
    instances = (raw or {}).get("instances") or {}
    return all(n in instances for n in FISH_INSTANCES)


def toggle_fish_modules(filepath, enabled, init=None):
    """在 fabm.yaml 中启用/禁用鱼类模块。返回 (success, warnings)。"""
    filepath = Path(filepath)
    try:
        raw = yaml.safe_load(filepath.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        return False, [f"读取 fabm.yaml 失败: {exc}"]
    if not isinstance(raw.get("instances"), dict):
        raw["instances"] = {}
    instances = raw["instances"]

    if enabled:
        if all(n in instances for n in FISH_INSTANCES):
            return True, ["鱼类模块已处于启用状态，配置未改动"]
        fish, warnings = build_fish_instances(instances, init=init)
        if fish is None:
            return False, warnings
        instances.update(fish)
    else:
        removed = [n for n in FISH_INSTANCES if instances.pop(n, None) is not None]
        if not removed:
            return True, ["鱼类模块未启用，无需禁用"]
        warnings = [f"已移除鱼类实例: {', '.join(removed)}"]

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(raw, f, default_flow_style=False, allow_unicode=True,
                      sort_keys=False)
    except Exception as exc:
        return False, [f"写入 fabm.yaml 失败: {exc}"]
    return True, warnings
