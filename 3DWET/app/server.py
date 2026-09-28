"""
3DWET Web Application - Flask Backend
Comprehensive API for model configuration, running, visualization, and calibration.
"""
import os
import sys
import io
import csv
import json
import re
import time
import uuid
import shutil
import subprocess
import tempfile
import threading
import functools
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

import numpy as np
import netCDF4 as nc
import yaml
import shapefile  # pyshp
import crs_utils
import fish_support
from scipy.interpolate import griddata
from scipy.spatial import cKDTree
from flask import Flask, render_template, request, jsonify, send_from_directory

# ── Paths ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = Path(__file__).resolve().parent
CASE_DIR = BASE_DIR / "case"
DATA_DIR = APP_DIR / "data"
EXTERNAL_CASES_FILE = DATA_DIR / "external_cases.json"  # registry of cases opened from arbitrary paths

# ── Pre-process cache (in-memory store for uploaded shapes / generated grids) ─
# Holds boundary / bathymetry / grid artifacts between upload → generate → save steps.
_preprocess_cache = {"boundary": {}, "bathymetry": {}, "grid": {}}

def _pp_cache_id(prefix):
    """Stable short id for cached pre-process artifacts."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

BIN_DIR = BASE_DIR / "bin"
# Prefer the native Windows build (getm_cartesian.exe); fall back to the
# WSL/Linux ELF binary when the exe is absent.
_NATIVE_EXE = BIN_DIR / "getm_cartesian.exe"
EXE_PATH = _NATIVE_EXE if _NATIVE_EXE.exists() else BIN_DIR / "getm_cartesian"

# MinGW runtime DLL dir (libgfortran/libnetcdf/libhdf5...) needed by the exe.
MSYS_UCRT_BIN = Path.home() / ".local" / "share" / "msys64" / "ucrt64" / "bin"

DATA_DIR.mkdir(exist_ok=True)

# ── Guard: redirect stdout/stderr to log file if no console (e.g. pythonw) ──
class _SafeLog:
    """Fallback stream that writes to a log file when console is unavailable."""
    def __init__(self, path):
        self._path = path
        self._fh = None
    def write(self, msg):
        try:
            if self._fh is None:
                self._fh = open(self._path, "a", encoding="utf-8")
            self._fh.write(msg)
            self._fh.flush()
        except Exception:
            pass
    def flush(self):
        if self._fh:
            try: self._fh.flush()
            except Exception: pass

for _stream_name in ("stdout", "stderr"):
    _s = getattr(sys, _stream_name, None)
    if _s is None or not hasattr(_s, "write"):
        setattr(sys, _stream_name, _SafeLog(str(APP_DIR / f"server_{_stream_name}.log")))

import logging
import traceback
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler(str(APP_DIR / "server_debug.log"), mode='w', encoding='utf-8'),
    ]
)

app = Flask(__name__,
            template_folder=str(APP_DIR / "templates"),
            static_folder=str(APP_DIR / "static"))
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable static file caching

# ── NaN-safe JSON (CRITICAL) ──────────────────────────────────────────
# 陆地格掩膜 → float('nan')。Python json 容忍 NaN 字面量，但浏览器
# JSON.parse 是严格 JSON，遇到 NaN 直接抛错 → 前端 2D/3D viewer 全空。
# 全局把 NaN/Inf 递归转成 null（前端 drawHeatmap/Plotly 均按 null=空格处理）。
import math as _math
from flask.json.provider import DefaultJSONProvider

def _json_safe(o):
    if isinstance(o, float):
        return None if (_math.isnan(o) or _math.isinf(o)) else o
    if isinstance(o, dict):
        return {k: _json_safe(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_json_safe(v) for v in o]
    return o

class SafeJSONProvider(DefaultJSONProvider):
    def dumps(self, obj, **kwargs):
        return super().dumps(_json_safe(obj), **kwargs)

app.json = SafeJSONProvider(app)

# ── NetCDF thread-safety (CRITICAL) ───────────────────────────────────
# libnetcdf C 库不是线程安全的。waitress 是多线程服务器：浏览器并行发起的
# 多个请求同时 nc.Dataset() 打开（不同或相同的）NetCDF 文件时，netcdf.dll
# 内部全局状态竞争 → 0xC0000005 秒杀整个服务进程，前端表现为
# "[XHR_DEBUG] Network error (XHR) - cannot connect to server"。
# （2026-09-22 21:46 事故，Windows Event Log：faulting module=netcdf.dll，
#  exception=c0000005，python.exe。）
# 因此所有 nc.Dataset 打开（读/写/追加）必须经 nc_open() 或 _with_nc_lock
# 串行化。RLock 允许同线程重入，嵌套调用安全。
_NC_LOCK = threading.RLock()

@contextmanager
def nc_open(path, mode="r"):
    """Thread-safe netCDF4.Dataset open. ALWAYS use this instead of nc.Dataset."""
    with _NC_LOCK:
        ds = nc.Dataset(str(path), mode)
        try:
            yield ds
        finally:
            try:
                ds.close()
            except Exception:
                pass

def _with_nc_lock(fn):
    """Run a whole function (typically a NetCDF writer) under the global lock."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        with _NC_LOCK:
            return fn(*args, **kwargs)
    return wrapper

def _output_locked():
    """True while the model is running on the active case: its output files are
    being written (and may hold open handles). Reading them from API threads
    previously crashed the server via netcdf.dll access violations."""
    if run_status != "running" or not run_case_path or not active_case_path:
        return False
    return str(Path(run_case_path).resolve()).lower() == str(Path(active_case_path).resolve()).lower()

# ── Global State ───────────────────────────────────────────────────────
active_case = None          # case directory name
active_case_path = None     # full path
run_case_path = None        # case dir of the currently running model (delete/save-as guard)
cached_getm_config = None   # cached to avoid GC crashes with YAML C ext
cached_fabm_info = None
run_process = None
run_thread = None
run_logs = []
run_status = "idle"         # idle, running, completed, failed, stopped
run_start_time = None
run_config = {}             # snapshot of config at run start
calibration_points = []     # loaded from data/calibration_points.json
calibration_data = {}       # {point_id: {variable: [{time, value}]}}

# 上次激活的案例持久化：服务重启（改完代码后必做）后自动恢复，
# 否则所有结果接口都会报“未加载案例”，要用户回 GUI 重新载入一次。
_LAST_CASE_FILE = APP_DIR / ".active_case.json"
try:
    _last = json.loads(_LAST_CASE_FILE.read_text(encoding="utf-8"))
    _p = Path(_last["path"])
    if _p.is_dir():
        active_case = _p.name
        active_case_path = _p
except Exception:
    pass

# ── Helpers ────────────────────────────────────────────────────────────

def get_process_cpu_seconds(proc):
    """Cumulative CPU seconds (user+kernel) of a Popen process on Windows.

    Used by the run watchdog: the MinGW-built exe can freeze in its exit
    path after the simulation itself has finished (netCDF output is already
    flushed), so a stalled CPU counter means "done", not "hung".
    Returns None when unavailable (non-Windows or process gone).
    """
    if os.name != "nt":
        return None
    try:
        import ctypes
        from ctypes import wintypes

        class _FILETIME(ctypes.Structure):
            _fields_ = [("lo", wintypes.DWORD), ("hi", wintypes.DWORD)]

        creation, exit_time, kernel, user = (_FILETIME(), _FILETIME(),
                                             _FILETIME(), _FILETIME())
        handle = int(proc._handle)  # process handle kept open by Popen
        if not ctypes.windll.kernel32.GetProcessTimes(
                handle, ctypes.byref(creation), ctypes.byref(exit_time),
                ctypes.byref(kernel), ctypes.byref(user)):
            return None

        def _ft_sec(ft):
            return ((ft.hi << 32) | ft.lo) / 1e7  # 100ns units -> seconds

        return _ft_sec(kernel) + _ft_sec(user)
    except Exception:
        return None


def wsl_path(windows_path):
    """Convert Windows path to WSL path."""
    p = str(windows_path)
    drive = p[0].lower()
    rest = p[2:].replace("\\", "/")
    return f"/mnt/{drive}{rest}"

def load_json(path, default=None):
    if Path(path).exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default if default is not None else {}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_calibration():
    global calibration_points, calibration_data
    calibration_points = load_json(DATA_DIR / "calibration_points.json", [])
    calibration_data = load_json(DATA_DIR / "calibration_data.json", {})

def save_calibration():
    save_json(DATA_DIR / "calibration_points.json", calibration_points)
    save_json(DATA_DIR / "calibration_data.json", calibration_data)

load_calibration()

# ── getm.inp Parser ───────────────────────────────────────────────────

def parse_getm_inp(filepath):
    """Parse GETM namelist file into structured dict."""
    config = {}
    current_namelist = None
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("!"):
                continue
            if line.startswith("&"):
                current_namelist = line[1:].rstrip(",").strip()
                config[current_namelist] = {}
            elif line.startswith("/"):
                current_namelist = None
            elif "=" in line and current_namelist:
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.split("!")[0].strip().rstrip(",")
                # Parse Fortran logical values
                val_lower = val.lower().strip("'\"")
                if val_lower in (".true.", ".t.", "true"):
                    val = True
                elif val_lower in (".false.", ".f.", "false"):
                    val = False
                else:
                    # Try to convert to number
                    try:
                        if "." in val or "e" in val.lower():
                            val = float(val)
                        else:
                            val = int(val)
                    except (ValueError, TypeError):
                        val = val.strip('"').strip("'")
                config[current_namelist][key] = val
    return config

def write_getm_inp(filepath, config):
    """Write GETM namelist from structured dict."""
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        for namelist, params in config.items():
            f.write(f"&{namelist}\n")
            for key, val in params.items():
                if isinstance(val, bool):
                    f.write(f"   {key} = .{'true' if val else 'false'}.\n")
                elif isinstance(val, str):
                    f.write(f"   {key} = '{val}'\n")
                else:
                    f.write(f"   {key} = {val}\n")
            f.write("/\n\n")

def get_time_settings(config):
    """Extract time-related settings from getm.inp config."""
    time = config.get("time", {})
    io_spec = config.get("io_spec", {})
    return {
        "start": time.get("start", "2000-01-01 00:00:00"),
        "stop": time.get("stop", "2000-01-02 00:00:00"),
        "timestep": time.get("timestep", 300),
        "step_2d": io_spec.get("step_2d", 1440),
        "step_3d": io_spec.get("step_3d", 1440),
    }

def get_run_info(config):
    """Extract run metadata."""
    param = config.get("param", {})
    m3d = config.get("m3d", {})
    return {
        "title": param.get("title", "3DWET Run"),
        "runid": param.get("runid", "3DWET"),
        "nlev": m3d.get("M", 10),
        "hotstart": param.get("hotstart", False),
        "runtype": param.get("runtype", 4),
        "out_dir": config.get("io_spec", {}).get("out_dir", "."),
    }

# ── fabm.yaml Parser ──────────────────────────────────────────────────

MODULE_CATEGORIES = {
    "abiotic_water": {"category": "非生物-水体", "color": "#6b7280"},
    "abiotic_sediment": {"category": "非生物-沉积物", "color": "#78716c"},
    "bot_pel_interface": {"category": "界面过程", "color": "#a78bfa"},
    "burial": {"category": "埋藏", "color": "#64748b"},
    "sediment_exchange": {"category": "沉积物交换", "color": "#92400e"},
    "POM": {"category": "有机质", "color": "#7c3aed"},
    "DOM": {"category": "有机质", "color": "#8b5cf6"},
    "humus": {"category": "有机质", "color": "#a78bfa"},
    "macrophytes": {"category": "水生植物", "color": "#16a34a"},
    "cyanobacteria": {"category": "浮游植物", "color": "#0891b2"},
    "diatoms": {"category": "浮游植物", "color": "#0284c7"},
    "greens": {"category": "浮游植物", "color": "#22c55e"},
    "cladocerans": {"category": "浮游动物", "color": "#f59e0b"},
    "copepods": {"category": "浮游动物", "color": "#d97706"},
    "zoobenthos": {"category": "底栖动物", "color": "#dc2626"},
    "JuFish": {"category": "鱼类", "color": "#2563eb"},
    "AdFish": {"category": "鱼类", "color": "#1d4ed8"},
    "PiscFish": {"category": "鱼类", "color": "#1e40af"},
    "fish": {"category": "鱼类", "color": "#2563eb"},
    "inorganic_carbon": {"category": "温室气体", "color": "#0d9488"},
    "methane": {"category": "温室气体", "color": "#b45309"},
}

# Disabled FABM modules are stored in a sidecar file `fabm_disabled.yaml`
# next to fabm.yaml — NOT as a top-level `_disabled` key inside fabm.yaml:
# FABM fatals at startup on unrecognized root-level options
# ("Unrecognized option ... found at root level", fabm_config.F90).
FABM_DISABLED_SIDECAR = "fabm_disabled.yaml"

def _fabm_disabled_store(fabm_path, heal=True):
    """Return the {instance_name: instance_dict} store of disabled modules.

    Reads the sidecar; with heal=True also migrates a legacy top-level
    `_disabled` block out of fabm.yaml (rewriting the file without it).
    """
    fabm_path = Path(fabm_path)
    disabled = {}
    sidecar = fabm_path.parent / FABM_DISABLED_SIDECAR
    if sidecar.exists():
        try:
            with open(sidecar, "r", encoding="utf-8") as f:
                d = yaml.safe_load(f) or {}
            if isinstance(d, dict):
                disabled = d
        except Exception:
            disabled = {}
    if not fabm_path.exists():
        return disabled
    try:
        with open(fabm_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        legacy = raw.get("_disabled")
        if isinstance(legacy, dict) and legacy:
            for k, v in legacy.items():
                disabled.setdefault(k, v)
            if heal:
                raw.pop("_disabled", None)
                with open(fabm_path, "w", encoding="utf-8") as f:
                    yaml.dump(raw, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                # Persist the migrated modules so nothing is lost
                _fabm_write_disabled(fabm_path.parent, disabled)
    except Exception:
        pass
    return disabled

def _fabm_write_disabled(case_dir, disabled):
    """Persist the disabled-module sidecar (removed when empty)."""
    sidecar = Path(case_dir) / FABM_DISABLED_SIDECAR
    if disabled:
        with open(sidecar, "w", encoding="utf-8") as f:
            yaml.dump(disabled, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    elif sidecar.exists():
        try:
            sidecar.unlink()
        except OSError:
            pass

_FABM_DOCS_FILE = APP_DIR / "fabm_docs.json"
_FABM_GLOSSARY_FILE = APP_DIR / "fabm_glossary.json"
_fabm_docs_cache = None


def _fabm_docs():
    """fabm_docs.json (English units/descriptions scraped from the model
    sources) merged with fabm_glossary.json (Chinese wording).  Cached."""
    global _fabm_docs_cache
    if _fabm_docs_cache is None:
        merged = {}
        for f in (_FABM_DOCS_FILE, _FABM_GLOSSARY_FILE):
            try:
                merged.update(json.loads(f.read_text(encoding="utf-8")))
            except Exception as e:  # noqa: BLE001
                print(f"[fabm docs] cannot read {f.name}: {e}", file=sys.stderr)
        _fabm_docs_cache = merged
    return _fabm_docs_cache


def _fabm_lookup(model, section, name):
    """Find `name` in docs[model][section], falling back to any other model."""
    docs = _fabm_docs()
    hit = (docs.get(model) or {}).get(section, {}).get(name)
    if hit:
        return hit
    for key, val in docs.items():
        if key in ("vars", "params", "modules", "_note"):
            continue
        if name in (val.get(section) or {}):
            return val[section][name]
    return None


def _annotate_param(model, name):
    """{unit, desc, desc_en} for one FABM parameter."""
    docs = _fabm_docs()
    hit = _fabm_lookup(model, "parameters", name) or {}
    en = (hit.get("label") or "").strip()
    zh = (docs.get("params", {}) or {}).get(name, "").strip()
    if not en and zh:
        en = zh
    return {"unit": (hit.get("units") or "").strip(),
            "desc": zh or en,
            "desc_en": en}


def _annotate_variable(model, name):
    """{unit, zh, en} for one state/bottom variable."""
    docs = _fabm_docs()
    hit = _fabm_lookup(model, "variables", name) or {}
    en = (hit.get("label") or "").strip()
    zh = (docs.get("vars", {}) or {}).get(name, "").strip()
    if not en and zh:
        en = zh
    return {"unit": (hit.get("units") or "").strip(),
            "zh": zh,
            "desc": zh or en,
            "desc_en": en}


def parse_fabm_yaml(filepath):
    """Parse fabm.yaml into structured module list with parameters.

    Modules under top-level `instances` are considered enabled; disabled
    modules live in the sidecar fabm_disabled.yaml (their full config is
    preserved there and can be re-enabled without loss).
    """
    with open(filepath, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    # JSON round-trip to ensure pure Python objects (avoid LibYAML C ext GC crashes)
    raw = json.loads(json.dumps(raw, default=str))

    # Extract inline comments per (module, param) by scanning raw text.
    # WET yaml convention: `  param: value  # description, default = X`
    comments = _extract_fabm_comments(filepath)
    sidecar = Path(filepath).parent / FABM_DISABLED_SIDECAR
    if sidecar.exists():
        for mod, params in _extract_fabm_comments(sidecar).items():
            comments.setdefault(mod, {}).update(params)

    instances = raw.get("instances", {})
    # Sidecar store + legacy `_disabled` heal (FABM rejects unknown root keys)
    disabled = _fabm_disabled_store(filepath)
    legacy = raw.get("_disabled")
    if isinstance(legacy, dict):
        for k, v in legacy.items():
            if k not in disabled:
                disabled[k] = v

    def _build(name, inst, enabled):
        if not isinstance(inst, dict):
            return None
        meta = MODULE_CATEGORIES.get(name, {"category": "其他", "color": "#6b7280"})
        params = inst.get("parameters", {})
        init = inst.get("initialization", {})
        coupling = inst.get("coupling", {})
        model = inst.get("model", "")

        # Flatten parameters into list (annotated with unit + description)
        param_list = []
        if isinstance(params, dict):
            for pname, pval in params.items():
                meta_c = comments.get(name, {}).get(pname, {})
                ann = _annotate_param(model, pname)
                param_list.append({
                    "name": pname,
                    "value": pval,
                    "type": "number" if isinstance(pval, (int, float)) else "string",
                    "comment": meta_c.get("comment", ""),
                    "default_value": meta_c.get("default_value"),
                    "unit": ann["unit"],
                    "desc": ann["desc"],
                    "desc_en": ann["desc_en"],
                })

        init_list = []
        if isinstance(init, dict):
            for iname, ival in init.items():
                init_list.append({"name": iname, "value": ival})

        return {
            "name": name,
            "long_name": inst.get("long_name", name),
            "model": model,
            "desc": _fabm_docs().get("modules", {}).get(name, ""),
            "category": meta["category"],
            "color": meta["color"],
            "enabled": enabled,
            "parameters": param_list,
            "initialization": init_list,
            "has_coupling": bool(coupling),
            "n_params": len(param_list),
        }

    modules = []
    for name, inst in instances.items():
        m = _build(name, inst, True)
        if m:
            modules.append(m)
    for name, inst in disabled.items():
        m = _build(name, inst, False)
        if m:
            modules.append(m)

    # Identify cross-module coupling references for disable-safety checks.
    # Coupling values look like "other_module/varname"; collect references per module.
    enabled_names = {m["name"] for m in modules if m["enabled"]}
    for m in modules:
        refs = set()
        inst = (instances if m["enabled"] else disabled).get(m["name"], {})
        coupling = inst.get("coupling", {}) if isinstance(inst, dict) else {}
        if isinstance(coupling, dict):
            for v in coupling.values():
                if isinstance(v, str) and "/" in v:
                    ref = v.split("/", 1)[0]
                    if ref in enabled_names:
                        refs.add(ref)
        m["coupling_refs"] = sorted(refs)

    # Group by category
    categories = defaultdict(list)
    for m in modules:
        categories[m["category"]].append(m)

    return {
        "modules": modules,
        "categories": dict(categories),
        "total_modules": len(modules),
        "total_enabled": sum(1 for m in modules if m["enabled"]),
        "total_disabled": sum(1 for m in modules if not m["enabled"]),
        "total_params": sum(m["n_params"] for m in modules),
    }

def _extract_fabm_comments(filepath):
    """Scan fabm.yaml text and return {module: {param: {comment, default_value}}}.

    WET yaml uses `# description, default = X` inline comments on every
    parameter line. PyYAML's safe_load strips these; this helper recovers them
    so the parameter editor can show doc + a "reset to default" affordance.
    """
    result = {}
    current_module = None
    default_re = re.compile(r"default\s*=\s*([^\s,;]+)", re.IGNORECASE)
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                stripped = line.rstrip()
                if not stripped or stripped.lstrip().startswith("#"):
                    continue
                # Detect top-level container keys (instances:, _disabled:) at column 0.
                # These reset current_module so we don't attach stray comments to a stale module.
                m_top = re.match(r"^(\w[\w_]*)\s*:\s*$", line)
                if m_top and not line.startswith(" ") and not line.startswith("\t"):
                    current_module = None
                    continue
                # Detect module block headers at exactly 2-space indent
                # (e.g. "  abiotic_water:"), excluding the container keys above.
                m_inst = re.match(r"^  (\w[\w_]*)\s*:\s*$", line)
                if m_inst:
                    current_module = m_inst.group(1)
                    result.setdefault(current_module, {})
                    continue
                # Detect "  param: value  # comment" lines (only if inside a module block)
                if "#" in line and current_module:
                    m_param = re.match(r"^(\s+)(\w[\w_]*)\s*:\s*(.+?)\s*(?:#.*)?$", line)
                    if m_param:
                        pname = m_param.group(2)
                        comment_part = line.split("#", 1)[1].strip()
                        default_match = default_re.search(comment_part)
                        default_val = None
                        if default_match:
                            dv_str = default_match.group(1).rstrip(",;")
                            try:
                                if "." in dv_str or "e" in dv_str.lower():
                                    default_val = float(dv_str)
                                else:
                                    default_val = int(dv_str)
                            except (ValueError, TypeError):
                                default_val = dv_str
                        result.setdefault(current_module, {})[pname] = {
                            "comment": comment_part,
                            "default_value": default_val,
                        }
    except Exception:
        pass
    return result

def _fabm_set_value(instance, key, value):
    """Set a fabm.yaml value under the right section.

    State-variable initial values (sDW, sNH4W, ...) live under
    `initialization:`; real model parameters under `parameters:`.
    Writing an initial value into `parameters:` makes FABM abort at
    startup with an unknown-parameter fatal error.
    """
    init = instance.get("initialization")
    if isinstance(init, dict) and key in init:
        init[key] = value
        return
    params = instance.get("parameters")
    if not isinstance(params, dict):
        params = {}
        instance["parameters"] = params
    params[key] = value

def update_fabm_parameter(filepath, module_name, param_name, value):
    """Update a single parameter in fabm.yaml."""
    with open(filepath, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    if module_name in raw.get("instances", {}):
        _fabm_set_value(raw["instances"][module_name], param_name, value)
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(raw, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        return True
    return False

def update_fabm_parameter_batch(filepath, params):
    """Update multiple parameters in fabm.yaml in one write.

    params: list of {module, param, value}.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    instances = raw.get("instances", {})
    applied = 0
    for p in params:
        m = p["module"]; k = p["param"]; v = p["value"]
        if m in instances and isinstance(instances[m], dict):
            _fabm_set_value(instances[m], k, v)
            applied += 1
    with open(filepath, "w", encoding="utf-8") as f:
        yaml.dump(raw, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return applied

def toggle_fabm_module(filepath, module_name, enabled):
    """Enable/disable a FABM module.

    Disabled instances are moved to the sidecar fabm_disabled.yaml (keeping
    their full configuration); enabling restores them. A legacy top-level
    `_disabled` block is migrated to the sidecar on the way — FABM fatals
    at startup on unrecognized root-level options.
    Returns (success, warnings) where warnings lists dependent enabled
    modules that reference the disabled module through `coupling:` entries.
    """
    filepath = Path(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    if raw is None:
        raw = {}
    if "instances" not in raw or not isinstance(raw["instances"], dict):
        raw["instances"] = {}

    legacy = raw.pop("_disabled", None)
    disabled = _fabm_disabled_store(filepath)
    if isinstance(legacy, dict):
        for k, v in legacy.items():
            disabled.setdefault(k, v)

    warnings = []
    if enabled:
        # Restore from the sidecar to instances
        if module_name not in disabled:
            return False, [f"模块 {module_name} 未在禁用列表中找到"]
        raw["instances"][module_name] = disabled.pop(module_name)
    else:
        # Move from instances to the sidecar
        if module_name not in raw["instances"]:
            return False, [f"模块 {module_name} 未启用，无需禁用"]
        # Scan other enabled modules' coupling for references to module_name
        for other_name, other_inst in raw["instances"].items():
            if other_name == module_name or not isinstance(other_inst, dict):
                continue
            coupling = other_inst.get("coupling", {})
            if not isinstance(coupling, dict):
                continue
            for key, val in coupling.items():
                if isinstance(val, str) and "/" in val and val.split("/", 1)[0] == module_name:
                    warnings.append(f"{other_name} 通过耦合 {key} 引用 {module_name}")
        disabled[module_name] = raw["instances"].pop(module_name)

    with open(filepath, "w", encoding="utf-8") as f:
        yaml.dump(raw, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    _fabm_write_disabled(filepath.parent, disabled)
    return True, warnings

# ── Greenhouse Gas (GHG) module support ───────────────────────────────
# GHG extension = wet/inorganic_carbon (DIC/TA/pH + air-water CO2 flux)
# + wet/methane (CH4 production/oxidation/ebullition/emission). Both are
# compiled into getm_cartesian.exe and couple ONLY to existing diagnostic
# variables of other WET modules (wCO2UptW, wCMin, tCTrans, tCProdVeg...),
# so enabling them never rewrites other modules — apart from switching
# their `diagnostics` parameter to true, because several of the coupled
# diagnostics are registered only when that flag is on.

GHG_IC_INSTANCE = "inorganic_carbon"
GHG_CH4_INSTANCE = "methane"
GHG_WET_SRC = BASE_DIR / "src" / "wet" / "src"
GHG_BUILD_FABM = BASE_DIR / "build-win" / "fabm"
GHG_BUILD_GETM = BASE_DIR / "build-win" / "getm"
GHG_BUILT_EXE = GHG_BUILD_GETM / "getm_cartesian.exe"

# Build pipeline state shared with the GUI (polled via GET /api/config/ghg)
ghg_build_state = {"running": False, "ok": None, "logs": [], "finished_at": None}

def _ghg_sources_mtime():
    mt = 0.0
    for fname in ("inorganic_carbon.F90", "methane.F90", "wet_model_library.F90"):
        p = GHG_WET_SRC / fname
        if p.exists():
            mt = max(mt, p.stat().st_mtime)
    return mt

def _ghg_exe_is_stale():
    """True when bin/getm_cartesian.exe predates the GHG sources (i.e. does
    not contain the modules) or a newer built exe awaits deployment."""
    if not _NATIVE_EXE.exists():
        return _ghg_sources_mtime() > 0
    if _NATIVE_EXE.stat().st_mtime < _ghg_sources_mtime():
        return True
    if GHG_BUILT_EXE.exists() and GHG_BUILT_EXE.stat().st_mtime > _NATIVE_EXE.stat().st_mtime:
        return True
    return False

def _ghg_built_exe_is_fresh():
    """True when the build-tree exe is up to date with the GHG sources."""
    return GHG_BUILT_EXE.exists() and GHG_BUILT_EXE.stat().st_mtime >= _ghg_sources_mtime()

def _ghg_case_enabled(case_path):
    """True when fabm.yaml of the case enables the GHG modules."""
    fabm_path = Path(case_path) / "fabm.yaml"
    if not fabm_path.exists():
        return False
    try:
        with open(fabm_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        inst = raw.get("instances", {})
        return isinstance(inst, dict) and GHG_IC_INSTANCE in inst
    except Exception:
        return False

def _fish_case_enabled(case_path):
    """True when fabm.yaml of the case contains the three fish instances."""
    return fish_support.fish_case_enabled(Path(case_path) / "fabm.yaml")


def _ghg_scan_instances(instances):
    """Classify enabled instances (by their `model:`) for GHG coupling."""
    scan = {"phyts": [], "zoos": [], "ompools": [], "macs": [], "bents": [],
            "bivs": [], "fishes": [], "abiotic_water": None,
            "abiotic_sediment": None, "bot_pel": None}
    by_model = {
        "wet/phytoplankton": "phyts", "wet/zooplankton": "zoos",
        "wet/om_pool": "ompools", "wet/macrophytes": "macs",
        "wet/zoobenthos": "bents", "wet/bivalves": "bivs", "wet/fish": "fishes",
    }
    for name, inst in instances.items():
        if not isinstance(inst, dict):
            continue
        model = inst.get("model", "")
        if model in by_model:
            scan[by_model[model]].append(name)
        elif model == "wet/abiotic_water":
            scan["abiotic_water"] = name
        elif model == "wet/abiotic_sediment":
            scan["abiotic_sediment"] = name
        elif model == "wet/bot_pel_interface":
            scan["bot_pel"] = name
    # Terminal DOM = the om_pool whose C mineralization ends in the water
    # column, i.e. the instance WITHOUT a C_transformation_water coupling.
    scan["terminal_dom"] = [
        n for n in scan["ompools"]
        if "C_transformation_water" not in (instances[n].get("coupling") or {})
    ]
    return scan

def _ghg_generate_instances(scan):
    """Build the two GHG instance dicts (parameters/initialization/coupling)
    from the classified module scan."""
    ic_coupling = {}
    for i, n in enumerate(scan["phyts"], 1):
        ic_coupling[f"CO2_uptake_water_{i}"] = f"{n}/wCO2UptW"
        ic_coupling[f"CO2_respiration_water_{i}"] = f"{n}/wCO2RespW"
    for i, n in enumerate(scan["zoos"], 1):
        ic_coupling[f"C_respiration_zooplankton_{i}"] = f"{n}/wCRespZoo"
    for i, n in enumerate(scan["terminal_dom"], 1):
        ic_coupling[f"C_mineralization_water_{i}"] = f"{n}/wCMin"
    if scan["fishes"]:
        ic_coupling["C_respiration_fish"] = f"{scan['fishes'][0]}/tCRespFi"
    for i, n in enumerate(scan["macs"], 1):
        ic_coupling[f"C_production_macrophyte_{i}"] = f"{n}/tCProdVeg"
        ic_coupling[f"C_respiration_macrophyte_{i}"] = f"{n}/tCRespVeg"
    for i, n in enumerate(scan["bents"], 1):
        ic_coupling[f"C_respiration_zoobenthos_{i}"] = f"{n}/tCRespBent"
    for i, n in enumerate(scan["bivs"], 1):
        ic_coupling[f"C_respiration_bivalves_{i}"] = f"{n}/tCRespBiv"
    if scan["bot_pel"]:
        ic_coupling["bot_pel_conv"] = f"{scan['bot_pel']}/bot_pel_conv"

    ic = {
        "long_name": "inorganic carbon, pH and CO2 air-water exchange (GHG)",
        "model": "wet/inorganic_carbon",
        "parameters": {
            "nPHYT": len(scan["phyts"]), "nZOO": len(scan["zoos"]),
            "nDOM": len(scan["terminal_dom"]), "nMAC": len(scan["macs"]),
            "nBENT": len(scan["bents"]), "nBIV": len(scan["bivs"]),
            "lFish": bool(scan["fishes"]),
            "cPco2Atm": 420.0, "hDICW": 0.1,
        },
        "initialization": {"sDICW": 20.0, "sAlkW": 2000.0},
        "coupling": ic_coupling,
    }

    ch4_coupling = {
        "DIC_pool_water": f"{GHG_IC_INSTANCE}/sDICW",
        "oxygen_pool_water": f"{scan['abiotic_water']}/sO2W",
        "aerobic_fraction_sediment": f"{scan['abiotic_sediment']}/afOxySed",
    }
    if scan["bot_pel"]:
        ch4_coupling["bot_pel_conv"] = f"{scan['bot_pel']}/bot_pel_conv"
    for i, n in enumerate(scan["ompools"], 1):
        ch4_coupling[f"C_mineralization_sediment_{i}"] = f"{n}/tCTrans"

    ch4 = {
        "long_name": "methane production, oxidation and emission (GHG)",
        "model": "wet/methane",
        "parameters": {
            "nOM": len(scan["ompools"]), "fMeth": 0.5, "fEbul": 0.6,
            "kCH4Oxid": 0.5, "cThetaCH4Oxid": 1.07,
            "hO2CH4Oxid": 0.5, "cPch4Atm": 1.9,
        },
        "initialization": {"sCH4W": 0.01},
        "coupling": ch4_coupling,
    }
    return ic, ch4

def toggle_ghg_modules(filepath, enabled):
    """Enable/disable the GHG modules in fabm.yaml.

    Enable: generate both instances with couplings derived from the
    currently enabled module set and switch `diagnostics` to true on the
    source instances. Disable: remove both instances — they are fully
    regenerated on the next enable. Returns (success, warnings).
    """
    filepath = Path(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    if not isinstance(raw.get("instances"), dict):
        raw["instances"] = {}
    instances = raw["instances"]

    warnings = []
    if enabled:
        if GHG_IC_INSTANCE in instances and GHG_CH4_INSTANCE in instances:
            return True, ["温室气体模块已处于启用状态，配置未改动"]
        scan = _ghg_scan_instances(instances)
        missing = [k for k in ("abiotic_water", "abiotic_sediment", "bot_pel") if not scan[k]]
        if missing:
            return False, [f"启用温室气体模块缺少必需实例: {', '.join(missing)}"]
        if not scan["phyts"]:
            return False, ["启用温室气体模块需要至少一个浮游植物实例"]
        if not scan["terminal_dom"]:
            warnings.append("未找到终端 DOM 实例（无 C_transformation_water 耦合的 om_pool），水柱有机碳矿化未耦合到 DIC")
        ic, ch4 = _ghg_generate_instances(scan)
        # Coupled diagnostics (wCO2UptW, wCRespZoo, tCProdVeg, ...) are only
        # registered when the source instance runs with diagnostics: true.
        flipped = []
        for key in ("phyts", "zoos", "macs", "bents", "bivs", "fishes"):
            for n in scan[key]:
                inst = instances[n]
                params = inst.get("parameters")
                if not isinstance(params, dict):
                    params = {}
                    inst["parameters"] = params
                if params.get("diagnostics") is not True:
                    params["diagnostics"] = True
                    flipped.append(n)
        if flipped:
            warnings.append("已开启 " + ", ".join(flipped) + " 的 diagnostics（温室气体模块依赖其诊断通量）")
        instances[GHG_IC_INSTANCE] = ic
        instances[GHG_CH4_INSTANCE] = ch4
    else:
        removed = [n for n in (GHG_IC_INSTANCE, GHG_CH4_INSTANCE)
                   if instances.pop(n, None) is not None]
        if not removed:
            return True, ["温室气体模块未启用，无需禁用"]

    # Legacy heal: never leave a top-level `_disabled` key in fabm.yaml
    legacy = raw.pop("_disabled", None)
    with open(filepath, "w", encoding="utf-8") as f:
        yaml.dump(raw, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    if isinstance(legacy, dict) and legacy:
        disabled = _fabm_disabled_store(filepath)
        for k, v in legacy.items():
            disabled.setdefault(k, v)
        _fabm_write_disabled(filepath.parent, disabled)
    return True, warnings

def _ghg_build_exe(log):
    """Rebuild getm_cartesian.exe in the build-win trees (incremental).

    Returns (ok, deployed): deployed=False when bin/getm_cartesian.exe is
    locked by a running model — the fresh exe then stays in the build tree
    and is deployed automatically before the next run start.
    """
    env = os.environ.copy()
    if MSYS_UCRT_BIN.exists():
        env["PATH"] = str(MSYS_UCRT_BIN) + os.pathsep + env.get("PATH", "")
    # Windows 上 CreateProcess 用父进程 PATH 定位可执行文件（env 只影响子进程
    # 内部的 DLL 搜索），因此必须自行在增强 PATH 中解析 cmake 的绝对路径。
    cmake = shutil.which("cmake", path=env.get("PATH", ""))
    if not cmake:
        log.append(f"[GHG] 未找到 cmake，请确认工具链位于 {MSYS_UCRT_BIN}")
        return False, False
    steps = [
        ("编译 FABM 库", [cmake, "--build", str(GHG_BUILD_FABM), "--target", "fabm"]),
        ("安装 FABM 库", [cmake, "--install", str(GHG_BUILD_FABM)]),
        ("链接 getm_cartesian", [cmake, "--build", str(GHG_BUILD_GETM)]),
    ]
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    for label, cmd in steps:
        log.append(f"[GHG] {label}...")
        try:
            r = subprocess.run(cmd, env=env, capture_output=True, text=True,
                               cwd=str(BASE_DIR), timeout=3600, creationflags=flags)
        except Exception as e:
            log.append(f"[GHG] {label} 失败: {e}")
            return False, False
        if r.returncode != 0:
            log.append(f"[GHG] {label} 失败 (exit {r.returncode})")
            for ln in (r.stdout or "").splitlines()[-15:]:
                log.append(f"  {ln}")
            for ln in (r.stderr or "").splitlines()[-15:]:
                log.append(f"  {ln}")
            return False, False
    if not GHG_BUILT_EXE.exists():
        log.append(f"[GHG] 编译产物缺失: {GHG_BUILT_EXE}")
        return False, False
    if run_status == "running":
        log.append("[GHG] 模型正在运行，暂不替换 bin 程序；下次启动运行前将自动部署新程序")
        return True, False
    try:
        shutil.copyfile(GHG_BUILT_EXE, _NATIVE_EXE)
        log.append("[GHG] 已部署新程序到 bin/getm_cartesian.exe")
    except PermissionError:
        log.append("[GHG] bin 程序被占用，暂不替换；下次启动运行前将自动部署")
        return True, False
    return True, True

def _ghg_build_worker():
    log = ghg_build_state["logs"]
    try:
        ok, _deployed = _ghg_build_exe(log)
        ghg_build_state["ok"] = ok
        log.append("[GHG] 编译" + ("完成" if ok else "失败"))
    except Exception as e:
        ghg_build_state["ok"] = False
        log.append(f"[GHG] 编译异常: {e}")
    finally:
        ghg_build_state["running"] = False
        ghg_build_state["finished_at"] = datetime.now().strftime("%H:%M:%S")

def _ghg_start_build():
    """Start the GHG build pipeline in a background thread (no-op if busy)."""
    if ghg_build_state["running"]:
        return False
    ghg_build_state.update({
        "running": True, "ok": None,
        "logs": ["[GHG] 开始编译温室气体模块..."], "finished_at": None,
    })
    threading.Thread(target=_ghg_build_worker, daemon=True).start()
    return True

def _ghg_build_snapshot():
    return {
        "running": ghg_build_state["running"],
        "ok": ghg_build_state["ok"],
        "logs": ghg_build_state["logs"][-30:],
        "finished_at": ghg_build_state["finished_at"],
    }

def _ghg_ensure_exe_for_run(log):
    """Before a run whose fabm.yaml enables GHG: make sure bin exe contains
    the modules. Deploys a pending fresh build; starts a rebuild when
    sources changed. Raises ValueError when the exe cannot be made ready."""
    if not _ghg_exe_is_stale():
        return
    if _ghg_built_exe_is_fresh():
        try:
            shutil.copyfile(GHG_BUILT_EXE, _NATIVE_EXE)
            log.append("[GHG] 已部署含温室气体模块的新程序 (bin/getm_cartesian.exe)")
            return
        except PermissionError:
            raise ValueError("bin/getm_cartesian.exe 被占用，无法部署含温室气体模块的程序")
    if ghg_build_state["running"]:
        raise ValueError("温室气体模块正在编译中，请编译完成后再次启动运行")
    _ghg_start_build()
    raise ValueError("正在重新编译含温室气体模块的程序，请编译完成后再次启动运行")

# ── NetCDF Results ────────────────────────────────────────────────────

def _nc_time_len(path):
    """Safely get time-dim length; 0 on any error (locked/corrupt/missing)."""
    try:
        return get_ntimesteps(path)
    except Exception:
        return 0

# ── Case directory layout ─────────────────────────────────────────────
# 标准案例目录结构（对齐 QWET 的工程组织习惯）：
#   案例根目录/        模型设置与运行文件（getm.inp、fabm.yaml、*.nc 等，
#                      GETM 以案例根为工作目录运行，这些文件必须在根目录）
#   Input/             用户提供的原始数据（气象/河流 CSV、水深文本、shapefile）
#   output/            模型运行产物（运行成功结束后自动归档到这里）
#   analysis/          分析产物（图表、诊断报告）
#   calibration/       率定配置与结果
_CASE_SUBDIRS = {
    "Input": "用户提供的原始数据放这里（气象/河流 CSV、水深文本、hypsograph.dat、shapefile 等）。\n"
             "模型运行需要的 .nc 文件由 GUI 转换后放在案例根目录——GETM 以根目录为工作目录，这是模型侧要求。",
    "output": "模型运行产物归档目录。每次运行成功结束后，*.2d.nc / *.3d.nc / output.nc / restart.nc\n"
              "会自动从根目录移入这里（根目录只保留运行中的临时文件）。GUI 读取结果时两个位置都会找。",
    "analysis": "分析产物目录：图表、诊断报告、导出的时间序列等。",
    "calibration": "率定相关文件：观测数据、率定配置、率定结果与最优参数记录。",
}


def _ensure_case_dirs(case_path):
    """Create the standard case sub-directories (Input/output/analysis/calibration).

    对新建案例和已有案例都幂等：存在则跳过，不存在则创建并放一份 README.txt
    说明用途。已有案例在加载时自动补齐，达到无痛迁移。
    """
    try:
        case = Path(case_path)
        for name, desc in _CASE_SUBDIRS.items():
            d = case / name
            d.mkdir(exist_ok=True)
            readme = d / "README.txt"
            if not readme.exists():
                readme.write_text(f"{name}/ — {desc}\n", encoding="utf-8")
    except Exception:
        pass  # 目录结构是便利设施，绝不能因为建目录失败而阻断案例加载


def find_output_files(case_path):
    """Find 2D and 3D output NetCDF files.

    GETM 新式运行把全部输出写到 output.nc，*.3d.nc/*.2d.nc 可能只是运行
    开始时创建的 0 记录空壳（2026-09-22 滇池重跑实锤：.3d.nc 仅 490KB
    time=0，而 output.nc 17.9GB 含 362 天完整输出）。时间维为 0 的文件
    视为无效，回退到 output.nc，避免把有数据的输出当不存在。
    """
    case = Path(case_path)
    result = {"2d": None, "3d": None}
    # 根目录是运行中的写入位置；output/ 是运行成功后的归档位置，两个都要找。
    # 候选按“根目录优先、归档其次”排列，取第一个有时间记录的有效文件——
    # 根目录的 0 记录空壳不能遮蔽 output/ 里归档好的有效文件。
    cands = {"2d": [], "3d": []}
    for f in list(case.glob("*.2d.nc")) + list(case.glob("*.3d.nc")) + \
             list((case / "output").glob("*.2d.nc")) + list((case / "output").glob("*.3d.nc")):
        if ".2d.nc" in f.name:
            cands["2d"].append(f)
        elif ".3d.nc" in f.name:
            cands["3d"].append(f)
    for key in ("3d", "2d"):
        for f in cands[key]:
            if _nc_time_len(f) > 0:
                result[key] = f
                break
    if result["3d"] is None:
        for out_nc in (case / "output.nc", case / "output" / "output.nc"):
            if out_nc.exists() and _nc_time_len(out_nc) > 0:
                result["3d"] = out_nc
                break
    return result

def get_variable_list(nc_path):
    """Get list of variables from a NetCDF file."""
    if not nc_path or not Path(nc_path).exists():
        return []
    with nc_open(nc_path) as ds:
        vars = []
        for vname, var in ds.variables.items():
            if vname in ("time", "x", "y", "xc", "yc", "lonc", "latc", "sigma", "z", "bathymetry", "mask"):
                continue
            dims = list(var.dimensions)
            if len(dims) >= 2:
                vars.append({
                    "name": vname,
                    "long_name": getattr(var, "long_name", vname),
                    "units": getattr(var, "units", ""),
                    "ndim": var.ndim,
                    "dims": dims,
                })
        return vars

def get_2d_field(nc_path, var_name, timestep=0, level=0):
    """Extract a 2D field from NetCDF.

    只读请求的时步/层（hyperslab），禁止 var[:] 整变量读取——滇池级案例
    单变量可达数百 MB，整读会让 API 卡死、前端永远"加载中"。
    """
    with nc_open(nc_path) as ds:
        if var_name not in ds.variables:
            return None
        var = ds.variables[var_name]

        # Find spatial dims
        dims = list(var.dimensions)
        time_idx = next((i for i, d in enumerate(dims) if "time" in d.lower()), 0)

        def _fill(a):
            return a.filled(np.nan) if isinstance(a, np.ma.MaskedArray) else np.asarray(a, dtype=float)

        if var.ndim == 3 and time_idx == 0:  # time, y, x
            nt = var.shape[0]
            if nt == 0:
                return None  # numrecs=0：异常中断/ sync_interval=0，无任何时间记录
            t = max(0, min(nt - 1, int(timestep)))
            field = _fill(var[t, :, :])
        elif var.ndim == 4 and time_idx == 0:  # time, z, y, x
            nt = var.shape[0]
            if nt == 0:
                return None
            t = max(0, min(nt - 1, int(timestep)))
            lev = max(0, min(var.shape[1] - 1, int(level)))
            field = _fill(var[t, lev, :, :])
        else:
            field = _fill(var[:])

        # Get coordinates
        bathy = None
        if "bathymetry" in ds.variables:
            bathy = _fill(ds.variables["bathymetry"][:])

        return {
            "data": field.tolist(),
            "shape": list(field.shape),
            "min": float(np.nanmin(field)) if not np.all(np.isnan(field)) else 0,
            "max": float(np.nanmax(field)) if not np.all(np.isnan(field)) else 0,
            "mean": float(np.nanmean(field)) if not np.all(np.isnan(field)) else 0,
            "bathymetry": bathy.tolist() if bathy is not None else None,
        }

def get_timeseries(nc_path, var_name, i=None, j=None, region=None, lake_avg=False, level=-1, per_layer=False, tstride=None):
    """Extract time series at a point, region, or lake average.

    全部使用 hyperslab 按需读取（禁止 var[:] 整变量读取）。对 4D 变量
    （time,z,y,x），`level` 支持 -1=表层（默认，与 GETM sigma 约定一致）。
    per_layer=True 时返回每一层的序列（series 为 nlev×nt 的二维数组），
    配合点位/区域/全湖范围给出垂向结构随时间的变化；此时忽略 level。

    时间降采样：滇池级输出可达百万时步，若全量返回会让前端 JSON 爆掉/绘图卡死。
    tstride 指定时按该步长取样；未指定时自动计算使返回点数 ≤ MAX_TS_POINTS（默认 3000）。
    分块读取保证内存有界、对任意大小文件都正确。
    """
    MAX_TS_POINTS = 3000
    with nc_open(nc_path) as ds:
        if var_name not in ds.variables:
            return None
        var = ds.variables[var_name]

        dims = list(var.dimensions)
        time_dim = next((d for d in dims if "time" in d.lower()), dims[0])
        ntime = len(ds.dimensions[time_dim]) if time_dim in ds.dimensions else 0
        # 时间步长（降采样）：自动上限 3000 点，避免百万时步文件压垮前端
        if not tstride or tstride < 1:
            tstride = max(1, (ntime + MAX_TS_POINTS - 1) // MAX_TS_POINTS)
        ts_idx = list(range(0, ntime, tstride))
        nts = len(ts_idx)

        def _fill(a):
            return a.filled(np.nan) if isinstance(a, np.ma.MaskedArray) else np.asarray(a, dtype=float)

        # Get time values（仅按步长取样的时间标签）
        times = []
        if time_dim in ds.variables:
            tvals_all = ds.variables[time_dim][:]
            tunits = getattr(ds.variables[time_dim], "units", "")
            try:
                tvals = nc.num2date(tvals_all[::tstride], tunits).tolist()
                times = [t.strftime("%Y-%m-%d %H:%M:%S") if hasattr(t, "strftime") else str(t) for t in tvals]
            except Exception:
                times = [float(t) for t in tvals_all[::tstride]]
        else:
            times = ts_idx

        # ── 每一层模式：返回 nlev × nts 的二维序列 ──────────────────────
        if per_layer:
            if var.ndim != 4:
                # 无垂向层：FABM 里这类变量多为「水柱积分通量 / 表层量」，物理上
                # 本就不随深度分层，并非模块未编译。给出同模块的 4D 状态变量作为
                # 替代，避免用户误判为编译问题。
                prefix = var_name.split("_")[0] if "_" in var_name else ""
                alt4d = sorted(
                    n for n, v in ds.variables.items()
                    if v.ndim == 4 and (n == var_name or (prefix and n.startswith(prefix + "_")))
                )
                head = (
                    f"变量「{var_name}」在输出中是无垂向层的 {var.ndim}D 变量"
                    f"（维度 {'、'.join(var.dimensions)}），不能生成垂向热图。"
                )
                if prefix and alt4d:
                    head += (
                        f"它不是模块未编译，而是该量本身是水柱积分通量/表层量，"
                        f"物理上不随深度分层。请改用同一模块的垂向状态变量："
                        + "、".join(alt4d[:8])
                        + ("…" if len(alt4d) > 8 else "")
                        + "。"
                    )
                else:
                    head += "请改选带 sigma 维度（time,sigma,yc,xc）的垂向状态变量。"
                return {"error": head, "ndim": var.ndim, "dims": list(var.dimensions), "alts_4d": alt4d}
            nlev = var.shape[1]
            z_levels = ds.variables["sigma"][:].tolist() if "sigma" in ds.variables else list(range(nlev))
            series2d = [[None] * nts for _ in range(nlev)]
            pos = {t: k for k, t in enumerate(ts_idx)}  # 时间索引 -> 输出列
            chunk = 2000  # 分块读取，避免一次性把整变量读入内存（滇池 3D 文件约百 GB 当量）
            for t0 in range(0, ntime, chunk):
                t1 = min(ntime, t0 + chunk)
                if i is not None and j is not None:
                    slab = _fill(var[t0:t1, :, j, i])          # (chunk, nlev) 仅该点位列
                elif region:
                    i1, i2, j1, j2 = region
                    slab = _fill(var[t0:t1, :, j1:j2, i1:i2])  # (chunk, nlev, h, w)
                else:
                    slab = _fill(var[t0:t1, :, :, :])          # (chunk, nlev, ny, nx) 全湖
                for t in range(t0, t1):
                    if t not in pos:
                        continue
                    out = pos[t]
                    for k in range(nlev):
                        if region:
                            sub = slab[t - t0, k]
                            val = float(np.nanmean(sub)) if not np.all(np.isnan(sub)) else None
                        elif i is not None and j is not None:
                            v = slab[t - t0, k]
                            val = float(v) if not np.isnan(v) else None
                        else:
                            sub = slab[t - t0, k]
                            val = float(np.nanmean(sub)) if not np.all(np.isnan(sub)) else None
                        series2d[k][out] = val
            return {
                "times": times,
                "series": series2d,
                "layers": z_levels,
                "per_layer": True,
                "n_layers": nlev,
                "tstride": tstride,
                "var_name": var_name,
                "long_name": getattr(var, "long_name", var_name),
                "units": getattr(var, "units", ""),
            }

        if ntime <= 0:
            series = []

        elif var.ndim == 3:  # time, y, x
            if lake_avg:
                arr = _fill(var[:, :, :])          # nt*ny*nx*4 ≈ 几 MB，可整段读
                series = [float(np.nanmean(arr[t])) if not np.all(np.isnan(arr[t])) else None for t in ts_idx]
            elif region:
                i1, i2, j1, j2 = region
                arr = _fill(var[:, j1:j2, i1:i2])
                series = [float(np.nanmean(arr[t])) if not np.all(np.isnan(arr[t])) else None for t in ts_idx]
            elif i is not None and j is not None:
                col = _fill(var[:, j, i])
                series = [float(v) if not np.isnan(v) else None for v in col[::tstride]]
            else:
                arr = _fill(var[:, :, :])
                series = [float(np.nanmean(arr[t])) if not np.all(np.isnan(arr[t])) else None for t in ts_idx]
        elif var.ndim == 4:  # time, z, y, x
            nlev = var.shape[1]
            lev = level if level >= 0 else nlev + level
            lev = max(0, min(nlev - 1, lev))
            if lake_avg:
                arr = _fill(var[:, lev, :, :])
                series = [float(np.nanmean(arr[t])) if not np.all(np.isnan(arr[t])) else None for t in ts_idx]
            elif region:
                i1, i2, j1, j2 = region
                arr = _fill(var[:, lev, j1:j2, i1:i2])
                series = [float(np.nanmean(arr[t])) if not np.all(np.isnan(arr[t])) else None for t in ts_idx]
            elif i is not None and j is not None:
                col = _fill(var[:, lev, j, i])
                series = [float(v) if not np.isnan(v) else None for v in col[::tstride]]
            else:
                arr = _fill(var[:, lev, :, :])
                series = [float(np.nanmean(arr[t])) if not np.all(np.isnan(arr[t])) else None for t in ts_idx]
        else:
            col = _fill(var[:])
            series = [float(v) if not np.isnan(v) else None for v in col[::tstride]]

        return {
            "times": times,
            "values": series,
            "var_name": var_name,
            "long_name": getattr(var, "long_name", var_name),
            "units": getattr(var, "units", ""),
            "layer": (lev if var.ndim == 4 and ntime > 0 else None),
            "tstride": tstride,
        }

def _nc_time_labels(nc_path, max_items=2000):
    """Return human-readable labels for the time axis of a NetCDF output file.

    GETM 的 2d/3d 文件按 step_2d/step_3d 抽帧写，间隔常常不是 1 天
    （例如 step_2d=8640 且 dt=25s → 2.5 天一帧）。GUI 若直接把滑块索引
    当“第 N 天”显示，用户会误以为模型只跑了 N 天就停了。这里返回每帧的
    真实日期，供前端在滑块旁标注。
    """
    import numpy as np
    if not nc_path or not Path(nc_path).exists():
        return []
    try:
        with nc_open(nc_path) as ds:
            if "time" not in ds.variables:
                return []
            tvar = ds["time"]
            vals = np.asarray(tvar[:]).ravel()
            units = getattr(tvar, "units", "")
            try:
                dates = nc.num2date(vals, units, only_use_cftime_datetimes=False,
                                    only_use_python_datetimes=True)
                return [d.strftime("%Y-%m-%d") for d in dates[:max_items]]
            except Exception:
                # 无法解码时间单位时退化为原始数值
                return [f"{float(v):g}" for v in vals[:max_items]]
    except Exception:
        logging.debug("读取时间轴失败: %s", traceback.format_exc())
        return []


def get_ntimesteps(nc_path):
    """Get number of timesteps in output file."""
    with nc_open(nc_path) as ds:
        for dname, dim in ds.dimensions.items():
            if "time" in dname.lower():
                return len(dim)
    return 0

def _cfl_max_timestep(case_path):
    """Estimate the maximum numerically sane timestep (seconds) for a case.

    重力波 CFL: dt_cfl = 0.5 * dx / sqrt(g * h_max)。GETM 半隐式格式允许
    超过 CFL 若干倍，这里取 15 倍封顶（下限 180s 保护极浅网格）。
    2026-09-22 事故：滇池 timestep 被改成 8640s（CFL 的 ~300 倍），
    check_cfl=.false. 下模型静默数值发散——全湖变干、输出全部 NaN，
    耗时 4 分钟产出 17.9GB 无效数据。
    Returns (dt_max, dt_cfl)；网格信息缺失时返回 (None, None) 跳过校验。
    """
    try:
        bathy = Path(case_path) / "bathymetry.nc"
        if not bathy.exists():
            return None, None
        with nc_open(bathy) as ds:
            dxs = []
            for axis in ("x", "y", "xc", "yc"):
                if axis in ds.variables and ds.variables[axis].size > 1:
                    diffs = np.abs(np.diff(np.asarray(ds.variables[axis][:]).ravel()))
                    if diffs.size:
                        dxs.append(float(diffs.mean()))
            if "dx" in ds.variables:
                dxs.append(float(np.ravel(ds.variables["dx"][:])[0]))
            if "bathymetry" not in ds.variables or not dxs:
                return None, None
            b = ds.variables["bathymetry"][:]
            bf = b.filled(np.nan) if np.ma.isMaskedArray(b) else np.asarray(b, dtype=float)
            pos = bf[np.isfinite(bf) & (bf > 0)]
            if not pos.size:
                return None, None
            dx = min(dxs)
            hmax = float(pos.max())
            dt_cfl = 0.5 * dx / (9.81 * hmax) ** 0.5
            return max(180, int(round(15 * dt_cfl))), dt_cfl
    except Exception:
        return None, None

# ── Run Control ───────────────────────────────────────────────────────

def estimate_run_time(case_path, config):
    """Estimate run time based on grid size, timestep, and duration."""
    try:
        bathy_path = Path(case_path) / "bathymetry.nc"
        if bathy_path.exists():
            with nc_open(bathy_path) as ds:
                ny, nx = ds.variables["bathymetry"].shape
                nwater = int((ds.variables["bathymetry"][:] > 0).sum())
        else:
            nx, ny, nwater = 24, 20, 280

        time_cfg = get_time_settings(config)
        start = datetime.strptime(str(time_cfg["start"]), "%Y-%m-%d %H:%M:%S")
        stop = datetime.strptime(str(time_cfg["stop"]), "%Y-%m-%d %H:%M:%S")
        duration_sec = (stop - start).total_seconds()
        dt = float(time_cfg["timestep"])
        nsteps = int(duration_sec / dt)

        # Empirical: ~0.01 sec/step per 100 water cells for serial build
        est_sec = nsteps * nwater * 0.0001

        dt_max, dt_cfl = _cfl_max_timestep(case_path)

        return {
            "nsteps": nsteps,
            "nwater": nwater,
            "grid": f"{nx}x{ny}",
            "duration_days": duration_sec / 86400,
            "estimated_seconds": est_sec,
            "estimated_minutes": est_sec / 60,
            "estimated_hours": est_sec / 3600,
            "timestep": dt,
            "cfl_max": dt_max,
            "cfl_dt": dt_cfl,
            "cfl_ok": (dt_max is None or dt <= dt_max),
        }
    except Exception as e:
        return {"error": str(e), "estimated_seconds": 0}

def _extend_nc_time_coverage(path, need_end):
    """Extend a forcing NetCDF (meteo.nc / rivers.nc) so its time axis covers
    need_end, by repeating the last record. Returns (n_ext, last_old_datetime);
    (0, last) when already sufficient. Raises ValueError on unreadable files.
    滇池 2020 事故：meteo 比 stop 早 20 步结束 → 模型在 99.999% 处 EOF 崩溃。
    """
    path = Path(path)
    with nc_open(path) as ds:
        tv = ds.variables.get("time")
        if tv is None or len(tv) == 0:
            raise ValueError(f"{path.name} 无时间步数据")
        units = getattr(tv, "units", "")
        if "since" not in units:
            raise ValueError(f"{path.name} 时间单位异常: {units!r}")
        base = _parse_date(units.split("since", 1)[1].strip())
        if base is None:
            raise ValueError(f"{path.name} 无法解析时间起点: {units!r}")
        tvals = np.array(tv[:], dtype="f8")
        dt = float(np.median(np.diff(tvals))) if len(tvals) > 1 else 86400.0
        last = base + timedelta(seconds=float(tvals[-1]))
        if last >= need_end:
            return 0, last
        time_unlimited = "time" in ds.dimensions and ds.dimensions["time"].isunlimited()
        time_attrs = {k: tv.getncattr(k) for k in tv.ncattrs()}
        static_vars, time_vars = {}, {}
        for name, var in ds.variables.items():
            if name == "time":
                continue
            arr = var[:]
            if isinstance(arr, np.ma.MaskedArray):
                arr = arr.filled(np.nan)
            attrs = {k: var.getncattr(k) for k in var.ncattrs()}
            entry = (np.array(arr), tuple(var.dimensions), attrs)
            if var.dimensions and var.dimensions[0] == "time":
                time_vars[name] = entry
            else:
                static_vars[name] = entry
    ext_secs, t = [], float(tvals[-1]) + dt
    while base + timedelta(seconds=t) <= need_end:
        ext_secs.append(t)
        t += dt
    if not ext_secs:
        return 0, last
    new_tvals = np.concatenate([tvals, np.array(ext_secs, dtype="f8")])
    tmp = path.with_name(path.name + ".tmp")
    with nc_open(tmp, "w") as out:
        created = set()
        def ensure_dim(dname, size):
            if dname not in created:
                out.createDimension(dname, size)
                created.add(dname)
        for arr, dims, _ in static_vars.values():
            for k, d in enumerate(dims):
                ensure_dim(d, arr.shape[k])
        # rivers.nc 的 time 维必须保持 unlimited（GETM init_river_input_ncdf
        # 直接查询 unlimdimid；固定长度会触发致命初始化错误）。
        ensure_dim("time", None if time_unlimited else len(new_tvals))
        for name, (arr, dims, attrs) in static_vars.items():
            v = out.createVariable(name, arr.dtype, dims)
            for k, val in attrs.items():
                setattr(v, k, val)
            v[:] = arr
        tvn = out.createVariable("time", "f8", ("time",))
        for k, val in time_attrs.items():
            setattr(tvn, k, val)
        tvn[:] = new_tvals
        for name, (arr, dims, attrs) in time_vars.items():
            extra = np.repeat(arr[-1:], len(ext_secs), axis=0)
            v = out.createVariable(name, arr.dtype, dims)
            for k, val in attrs.items():
                setattr(v, k, val)
            v[:] = np.concatenate([arr, extra], axis=0)
    tmp.replace(path)
    return len(ext_secs), last


def _ensure_forcing_coverage(case_path, config):
    """Pre-flight before a run: make sure meteo.nc / rivers.nc cover the model
    stop time; auto-extend by repeating the last record when short. Returns a
    list of warning strings. Raises ValueError when a forcing file is broken."""
    warnings = []
    stop_str = (config.get("time", {}) or {}).get("stop")
    stop = _parse_date(str(stop_str)) if stop_str else None
    if stop is None:
        return warnings
    need_end = stop + timedelta(days=1)
    for fname in ("meteo.nc", "rivers.nc"):
        p = Path(case_path) / fname
        if not p.exists():
            continue
        n_ext, last = _extend_nc_time_coverage(p, need_end)
        if n_ext:
            warnings.append(f"{fname} 原截止 {last:%Y-%m-%d %H:%M}，已自动延长 "
                            f"{n_ext} 步（重复末段数据）以覆盖模拟结束时间")
    return warnings


def _river_cell_problems(rivers, case_path):
    """Validate river cells against bathymetry. Returns (errors, warnings).
    滇池事故：盘龙江入湖点在孤立水域 → 该格点堆积 712m 水柱、178.6M m³。
    i/j 为 1-based（i=列/x, j=行/y），bathymetry 数组按 [j-1, i-1] 索引。"""
    bathy_p = Path(case_path) / "bathymetry.nc"
    if not bathy_p.exists():
        return [], []
    try:
        with nc_open(bathy_p) as ds:
            raw = ds.variables["bathymetry"][:]
            dep = raw.filled(np.nan) if isinstance(raw, np.ma.MaskedArray) else np.array(raw)
    except Exception:
        return [], []
    ny, nx = dep.shape
    errors, warnings = [], []

    def wet(ii, jj):
        return 0 <= ii < nx and 0 <= jj < ny and np.isfinite(dep[jj, ii]) and dep[jj, ii] > 0

    for r in rivers:
        i, j, name = int(r["i"]), int(r["j"]), r["name"]
        if not (1 <= i <= nx and 1 <= j <= ny):
            errors.append(f"{name}: 格点 ({i},{j}) 超出网格范围 {nx}x{ny}")
            continue
        d = dep[j - 1, i - 1]
        if not np.isfinite(d) or d <= 0:
            errors.append(f"{name}: 格点 ({i},{j}) 是陆地（无水深），河流入湖点必须位于水域内")
            continue
        # 只数面连通（上下左右）：对角线连接在 GETM 中不产生水量交换。
        nb = sum(1 for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)) if wet(i - 1 + di, j - 1 + dj))
        if nb == 0:
            errors.append(f"{name}: 格点 ({i},{j}) 水深 {d:.2f}m 但无任何面连通水格"
                          f"（仅对角线相邻不算连通），入流无法排出会无限堆积水位，"
                          f"必须移到与开阔水域面连通的格点")
        elif nb < 2:
            warnings.append(f"{name}: 格点 ({i},{j}) 水深 {d:.2f}m 但仅 {nb} 个面连通水格，"
                            f"死端水道易造成水量堆积/数值发散，建议移到开阔水域")
    return errors, warnings


def _archive_run_outputs(case_path, run_logs):
    """运行成功后把输出产物从根目录归档到 output/ 子目录。

    GETM 以案例根为工作目录，运行时必须写在根目录；跑完后根目录只保留
    配置与输入，产物统一收进 output/（find_output_files 两个位置都会找）。
    只归档有时间记录的有效文件，0 记录空壳留在根目录由 run_check 提示。
    """
    case = Path(case_path)
    out_dir = case / "output"
    try:
        out_dir.mkdir(exist_ok=True)
        moved = []
        with _NC_LOCK:  # 与结果读取端点互斥，避免移动到一半被打开
            for pat in ("*.2d.nc", "*.3d.nc", "output.nc", "restart.nc"):
                for f in case.glob(pat):
                    if not f.is_file():
                        continue
                    if f.suffix == ".nc" and f.name != "restart.nc" and _nc_time_len(f) == 0:
                        continue  # 空壳不归档
                    dest = out_dir / f.name
                    try:
                        if dest.exists():
                            dest.unlink()
                        f.rename(dest)
                        moved.append(f.name)
                    except OSError:
                        # 跨设备或占用时退化为复制
                        try:
                            shutil.copy2(str(f), str(dest))
                            f.unlink()
                            moved.append(f.name)
                        except OSError:
                            pass
        if moved:
            run_logs.append(f"[INFO] 输出已归档到 output/：{', '.join(moved)}")
    except Exception as e:
        run_logs.append(f"[WARN] 输出归档失败（不影响结果读取）: {e}")


def run_model_thread(case_path, exe_path):
    """Run model in background thread, output to log file for stability."""
    global run_process, run_status, run_logs, run_start_time, run_case_path

    case_path = Path(case_path)
    model_log = case_path / "model_run.log"
    is_native = str(exe_path).lower().endswith(".exe")

    run_logs.append(f"[INFO] 启动模型运行...")
    run_logs.append(f"[INFO] 案例目录: {case_path.name}")
    run_logs.append(f"[INFO] 可执行文件: {exe_path} ({'Windows 原生' if is_native else 'WSL/Linux'})")
    run_logs.append(f"[INFO] 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    run_start_time = time.time()

    try:
        log_fh = open(model_log, "w", encoding="utf-8", errors="replace")
        if is_native:
            # Native Windows exe: run directly with MinGW runtime DLLs on PATH.
            env = os.environ.copy()
            if MSYS_UCRT_BIN.exists():
                env["PATH"] = str(MSYS_UCRT_BIN) + os.pathsep + env.get("PATH", "")
            # Unbuffered stderr so model_run.log tracks real progress; the WET
            # Patankar solver floods stdout ("is zero and has negative
            # derivative", GBs over a multi-day run), so stdout is discarded.
            env["GFORTRAN_UNBUFFERED_PRECONNECTED"] = "y"
            env["GFORTRAN_UNBUFFERED_ALL"] = "y"
            run_process = subprocess.Popen(
                [str(exe_path)],
                cwd=str(case_path),
                stdout=subprocess.DEVNULL,
                stderr=log_fh,
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
        else:
            # WSL/Linux binary: launch through wsl.exe with shell redirection.
            case_wsl = wsl_path(case_path)
            exe_wsl = wsl_path(exe_path)
            log_wsl = wsl_path(model_log)
            log_fh.close()
            run_process = subprocess.Popen(
                ["wsl.exe", "bash", "-c",
                 f"cd '{case_wsl}' && '{exe_wsl}' > '{log_wsl}' 2>&1"],
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
        # Poll log file for progress while model runs
        log_read_pos = 0
        # Exit-hang watchdog (native exe only): the MinGW build can freeze in
        # its exit path after the simulation finished; netCDF output is already
        # on disk by then. CPU-time stall -> reclaim as completed.
        finished_by_watchdog = False
        last_cpu = None
        cpu_stall = 0
        while run_process.poll() is None:
            time.sleep(1.0)
            try:
                with open(model_log, "r", encoding="utf-8", errors="replace") as f:
                    f.seek(log_read_pos)
                    new_lines = f.read()
                    log_read_pos = f.tell()
                for line in new_lines.splitlines():
                    line = line.strip()
                    if line:
                        run_logs.append(line)
                if len(run_logs) > 5000:
                    run_logs = run_logs[-2000:]
            except Exception:
                pass
            if is_native and os.name == "nt":
                cpu = get_process_cpu_seconds(run_process)
                if cpu is not None:
                    if last_cpu is not None and (cpu - last_cpu) < 0.05:
                        cpu_stall += 1
                    else:
                        cpu_stall = 0
                    last_cpu = cpu
                    if (cpu_stall >= 90 and (time.time() - run_start_time) > 60):
                        run_logs.append("[INFO] 模拟计算已完成（进程退出清理阶段自动回收）")
                        try:
                            run_process.terminate()
                            run_process.wait(timeout=30)
                        except Exception:
                            pass
                        finished_by_watchdog = True
                        break
        # Read remaining output
        time.sleep(0.5)
        try:
            with open(model_log, "r", encoding="utf-8", errors="replace") as f:
                f.seek(log_read_pos)
                for line in f.read().splitlines():
                    line = line.strip()
                    if line:
                        run_logs.append(line)
        except Exception:
            pass
        try:
            log_fh.close()
        except Exception:
            pass
        elapsed = time.time() - run_start_time
        # 看门狗回收或正常退出后，仍需依据日志判定是否真成功：
        # MinGW 构建在 STOP 1 / fatal_error 后会卡在退出路径（CPU≈0），
        # 看门狗会误判为“算完在清理”而标 completed。必须按日志致命字样纠正，
        # 否则会把崩溃伪装成成功并归档空壳。
        _log_blob = "\n".join(run_logs)
        _crashed = any(k in _log_blob for k in (
            "STOP 1", "collect_from_categories",
            "fatal_error", "FATAL GETM ERROR", "FATAL ERROR",
            "out-of-bound", "IEEE_INVALID", "IEEE_DIVIDE_BY_ZERO",
            "Floating invalid", "forrtl:", "NaN",
        ))
        if (run_process.returncode == 0 or finished_by_watchdog) and not _crashed:
            run_status = "completed"
            run_logs.append(f"[INFO] 模型运行完成！耗时: {elapsed:.1f}秒 ({elapsed/60:.1f}分钟)")
            _archive_run_outputs(case_path, run_logs)
        else:
            run_status = "failed"
            if finished_by_watchdog and _crashed:
                run_logs.append("[ERROR] 模型运行失败：日志检测到 STOP 1 / fatal_error，"
                                "看门狗误回收已纠正为失败（未归档空壳）")
            else:
                run_logs.append(f"[ERROR] 模型运行失败，退出码: {run_process.returncode}")
    except Exception as e:
        run_status = "failed"
        run_logs.append(f"[ERROR] 运行异常: {str(e)}")
    finally:
        run_case_path = None

# ── Routes: Pages ─────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

# ── Routes: Case Management ───────────────────────────────────────────

def _load_external_cases():
    """Registered external case paths (cases opened from arbitrary locations)."""
    try:
        with open(EXTERNAL_CASES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [p for p in data if isinstance(p, str)]
    except Exception:
        return []

def _save_external_cases(paths):
    with open(EXTERNAL_CASES_FILE, "w", encoding="utf-8") as f:
        json.dump(paths, f, ensure_ascii=False, indent=2)

def _register_external_case(path):
    key = str(Path(path).resolve()).lower()
    if key not in [str(Path(p).resolve()).lower() for p in _load_external_cases()]:
        _save_external_cases(_load_external_cases() + [str(path)])

def _unregister_external_case(path):
    key = str(Path(path).resolve()).lower()
    _save_external_cases([p for p in _load_external_cases()
                          if str(Path(p).resolve()).lower() != key])

def _is_case_dir(p):
    """A directory counts as a case when it holds getm.inp or bathymetry.nc."""
    return (p / "getm.inp").exists() or (p / "bathymetry.nc").exists()

def _under_case_dir(p):
    try:
        p.relative_to(CASE_DIR.resolve())
        return True
    except ValueError:
        return False

def _case_in_use(path):
    """True when a model run is active inside the given case directory."""
    if run_status != "running" or not run_case_path:
        return False
    return str(Path(run_case_path).resolve()).lower() == str(Path(path).resolve()).lower()

def _activate_case(case_path):
    """Make case_path the active case and return the standard load payload."""
    global active_case, active_case_path, cached_getm_config, cached_fabm_info
    _ensure_case_dirs(case_path)
    case_name = case_path.name
    active_case = case_name
    active_case_path = case_path
    # 记住本次选择，服务重启后自动恢复
    try:
        _LAST_CASE_FILE.write_text(
            json.dumps({"path": str(case_path)}, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass
    # Load configs - cache in globals to avoid GC crashes with YAML C ext
    # New cases built via preprocess may not have getm.inp yet (built later
    # on the input-data page); get_time_settings/get_run_info fall back to
    # defaults for an empty config.
    inp_path = case_path / "getm.inp"
    cached_getm_config = parse_getm_inp(inp_path) if inp_path.exists() else {}
    cached_fabm_info = parse_fabm_yaml(case_path / "fabm.yaml") if (case_path / "fabm.yaml").exists() else {"modules": [], "categories": {}}
    time_settings = get_time_settings(cached_getm_config)
    run_info = get_run_info(cached_getm_config)
    output_files = find_output_files(case_path)

    # Output.yaml sanity check: sync_interval=0 wipes all output (Lake Luoma incident).
    # Use the regex parser because PyYAML's safe_load crashes on `source: *` wildcard.
    output_warning = None
    out_path = case_path / "output.yaml"
    if out_path.exists():
        try:
            out_parsed = _parse_output_yaml(out_path)
            if out_parsed.get("sync_interval", 0) == 0:
                output_warning = (
                    "output.yaml 中 sync_interval=0，运行后输出文件 time 维度将为 0，"
                    "所有模拟结果将丢失。请改为 ≥1（1 表示每个时间步同步一次输出）。"
                )
        except Exception:
            pass

    # 输出文件时间步数（numrecs）：0 表示文件存在但从未写入数据
    # （上次运行异常中断或 sync_interval=0），前端据此给出明确警告。
    output_ntimesteps = None
    if output_files["2d"] is not None or output_files["3d"] is not None:
        try:
            output_ntimesteps = get_ntimesteps(output_files["3d"] or output_files["2d"])
        except Exception:
            output_ntimesteps = None

    return jsonify({
        "success": True,
        "case_name": case_name,
        "case_path": str(case_path),
        "time_settings": time_settings,
        "run_info": run_info,
        "fabm": cached_fabm_info,
        "output_files": {k: str(v) if v else None for k, v in output_files.items()},
        "has_results": output_files["2d"] is not None or output_files["3d"] is not None,
        "output_ntimesteps": output_ntimesteps,
        "output_warning": output_warning,
    })

@app.route("/api/cases")
def list_cases():
    def _case_info(d, external):
        return {
            "name": d.name,
            "path": str(d),
            "external": external,
            "has_bathymetry": (d / "bathymetry.nc").exists(),
            "has_fabm": (d / "fabm.yaml").exists(),
            "has_meteo": (d / "meteo.nc").exists(),
            "has_rivers": (d / "riverinfo.dat").exists(),
            "has_2d_output": any(d.glob("*.2d.nc")),
            "has_3d_output": any(d.glob("*.3d.nc")),
        }
    cases = []
    seen = set()
    if CASE_DIR.exists():
        for d in CASE_DIR.iterdir():
            if d.is_dir() and (d / "getm.inp").exists():
                cases.append(_case_info(d, False))
                seen.add(str(d.resolve()).lower())
    for raw in _load_external_cases():
        d = Path(raw)
        if not d.is_dir() or not _is_case_dir(d):
            continue
        key = str(d.resolve()).lower()
        if key in seen:
            continue
        cases.append(_case_info(d, True))
        seen.add(key)
    return jsonify(cases)

@app.route("/api/case/inputs")
def case_inputs():
    """Return inventory of expected input files for the active case."""
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    expected = [
        {"name": "bathymetry.nc", "desc": "水下地形（网格+水深）", "is_nc": True},
        {"name": "fabm.yaml", "desc": "生态模型配置（模块+参数）", "is_nc": False},
        {"name": "meteo.nc", "desc": "气象强迫数据", "is_nc": True},
        {"name": "riverinfo.dat", "desc": "河流配置（入/出流位置）", "is_nc": False},
        {"name": "rivers.nc", "desc": "河流流量与水质时间序列", "is_nc": True},
        {"name": "fabm_init.nc", "desc": "生态初始条件", "is_nc": True},
        {"name": "getm.inp", "desc": "GETM 主配置文件", "is_nc": False},
        {"name": "gotmturb.nml", "desc": "湍流模型配置", "is_nc": False},
        {"name": "output.yaml", "desc": "输出配置（sync_interval 等）", "is_nc": False},
    ]
    files = []
    for f in expected:
        path = active_case_path / f["name"]
        info = {"name": f["name"], "desc": f["desc"], "exists": path.exists()}
        if info["exists"]:
            stat = path.stat()
            info["size_bytes"] = stat.st_size
            info["mtime"] = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            if f["is_nc"]:
                try:
                    with nc_open(path) as ds:
                        info["n_vars"] = len(ds.variables)
                except Exception:
                    info["n_vars"] = None
            else:
                info["n_vars"] = None
        else:
            info["size_bytes"] = 0
            info["mtime"] = ""
            info["n_vars"] = None
        files.append(info)
    return jsonify({"case_name": active_case, "files": files})

@app.route("/api/case/load", methods=["POST"])
def load_case():
    data = request.json
    case_name = data.get("case_name")
    case_path = CASE_DIR / case_name
    if not case_path.exists():
        return jsonify({"success": False, "error": "案例不存在"}), 404
    return _activate_case(case_path)

@app.route("/api/case/open", methods=["POST"])
def open_case():
    """Open (and register) a case from an arbitrary filesystem path."""
    data = request.json or {}
    raw = str(data.get("path") or "").strip().strip('"').strip("'")
    if not raw:
        return jsonify({"success": False, "error": "请提供案例目录的绝对路径"}), 400
    p = Path(raw)
    if not p.is_absolute():
        return jsonify({"success": False, "error": "请提供绝对路径，例如 D:\\lakes\\mycase"}), 400
    p = p.resolve()
    protected = {BASE_DIR.resolve(), APP_DIR.resolve(), CASE_DIR.resolve(), Path.home().resolve()}
    if p in protected or p.parent == p or not p.is_dir():
        return jsonify({"success": False, "error": f"目录不存在或不可用: {p}"}), 400
    if not _is_case_dir(p):
        return jsonify({"success": False, "error": "该目录不是有效案例（需包含 getm.inp 或 bathymetry.nc）"}), 400
    if not _under_case_dir(p):
        _register_external_case(p)
    return _activate_case(p)

# Files skipped by save-as unless the user opts to include results.
SAVE_AS_EXCLUDE = ["*.2d.nc", "*.3d.nc", "output.nc",
                   "run.log", "model_run.log", "visualize_run.log"]

@app.route("/api/case/save_as", methods=["POST"])
def case_save_as():
    """Copy a case to an arbitrary destination directory."""
    data = request.json or {}
    src = Path(str(data.get("source_path") or "").strip().strip('"'))
    dest_raw = str(data.get("dest_path") or "").strip().strip('"')
    include_results = bool(data.get("include_results"))
    if not str(src) or not dest_raw:
        return jsonify({"error": "请提供源案例路径与目标目录"}), 400
    if not src.is_absolute():
        return jsonify({"error": "源案例路径必须是绝对路径"}), 400
    src = src.resolve()
    if not src.is_dir() or not _is_case_dir(src):
        return jsonify({"error": "源目录不是有效案例"}), 400
    dest = Path(dest_raw)
    if not dest.is_absolute():
        return jsonify({"error": "目标目录必须是绝对路径，例如 D:\\mycases\\backup01"}), 400
    dest = dest.resolve()
    protected = {BASE_DIR.resolve(), APP_DIR.resolve(), CASE_DIR.resolve(), Path.home().resolve()}
    if dest in protected or dest.parent == dest:
        return jsonify({"error": "目标目录不可用"}), 400
    if dest == src:
        return jsonify({"error": "目标目录与源目录相同"}), 400
    try:
        dest.relative_to(src)
        return jsonify({"error": "目标目录不能位于源案例目录内"}), 400
    except ValueError:
        pass
    if _case_in_use(src):
        return jsonify({"error": "该案例的模型正在运行，请先停止运行再另存"}), 400
    if dest.exists():
        if not dest.is_dir():
            return jsonify({"error": f"目标路径已存在且不是目录: {dest}"}), 400
        if any(dest.iterdir()):
            return jsonify({"error": f"目标目录已存在且非空: {dest}"}), 400
    else:
        try:
            dest.mkdir(parents=True)
        except OSError as e:
            return jsonify({"error": f"无法创建目标目录: {e}"}), 400
    try:
        if include_results:
            shutil.copytree(src, dest, dirs_exist_ok=True)
        else:
            shutil.copytree(src, dest, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns(*SAVE_AS_EXCLUDE))
    except Exception as e:
        return jsonify({"error": f"复制失败: {e}"}), 500
    n_files, size_bytes = 0, 0
    for f in dest.rglob("*"):
        if f.is_file():
            n_files += 1
            size_bytes += f.stat().st_size
    if not _under_case_dir(dest):
        _register_external_case(dest)
    return jsonify({"success": True, "dest_path": str(dest),
                    "n_files": n_files, "size_bytes": size_bytes})

@app.route("/api/case/delete", methods=["POST"])
def case_delete():
    """Delete a case directory. Only cases shown in the list (under CASE_DIR
    or registered external) can be deleted; running cases are refused."""
    data = request.json or {}
    raw = str(data.get("path") or "").strip().strip('"')
    if not raw:
        return jsonify({"error": "请提供案例路径"}), 400
    p = Path(raw)
    if not p.is_absolute():
        return jsonify({"error": "请提供绝对路径"}), 400
    p = p.resolve()
    protected = {BASE_DIR.resolve(), APP_DIR.resolve(), CASE_DIR.resolve(), Path.home().resolve()}
    if p in protected or p.parent == p:
        return jsonify({"error": "非法目录"}), 400
    if not p.is_dir() or not _is_case_dir(p):
        return jsonify({"error": "目录不存在或不是有效案例"}), 400
    if not _under_case_dir(p):
        known = any(str(Path(x).resolve()).lower() == str(p).lower()
                    for x in _load_external_cases())
        if not known:
            return jsonify({"error": "只能删除案例列表中显示的案例"}), 403
    if _case_in_use(p):
        return jsonify({"error": "该案例的模型正在运行，请先停止运行再删除"}), 400
    n_files, size_bytes = 0, 0
    for f in p.rglob("*"):
        if f.is_file():
            try:
                n_files += 1
                size_bytes += f.stat().st_size
            except OSError:
                pass
    try:
        shutil.rmtree(p)
    except OSError as e:
        return jsonify({"error": f"删除失败: {e}"}), 500
    _unregister_external_case(p)
    global active_case, active_case_path, cached_getm_config, cached_fabm_info
    if active_case_path and str(Path(active_case_path).resolve()).lower() == str(p).lower():
        active_case = None
        active_case_path = None
        cached_getm_config = None
        cached_fabm_info = None
        # 该案例已删除，别让重启后自动恢复它
        try:
            if _LAST_CASE_FILE.exists():
                _LAST_CASE_FILE.unlink()
        except Exception:
            pass
    return jsonify({"success": True, "n_files": n_files, "size_bytes": size_bytes})

# ── Routes: Configuration ─────────────────────────────────────────────

@app.route("/api/config/time", methods=["GET", "POST"])
def config_time():
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    inp_path = active_case_path / "getm.inp"
    if request.method == "GET":
        config = parse_getm_inp(inp_path)
        return jsonify(get_time_settings(config))
    else:
        data = request.json
        config = parse_getm_inp(inp_path)
        if "time" not in config:
            config["time"] = {}
        # &time only accepts timestep/timefmt/nlast/start/stop; strip stray
        # keys (e.g. step_2d) inherited from older buggy templates.
        for bad in set(config["time"]) - {"timestep", "timefmt", "nlast", "start", "stop"}:
            del config["time"][bad]
        if "start" in data:
            config["time"]["start"] = data["start"]
        if "stop" in data:
            config["time"]["stop"] = data["stop"]
        if "timestep" in data:
            try:
                new_dt = float(data["timestep"])
            except (TypeError, ValueError):
                return jsonify({"success": False, "error": "timestep 必须是数字"}), 400
            if new_dt <= 0:
                return jsonify({"success": False, "error": "timestep 必须为正数"}), 400
            dt_max, dt_cfl = _cfl_max_timestep(active_case_path)
            if dt_max and new_dt > dt_max:
                return jsonify({
                    "success": False,
                    "error": (f"时间步长 {new_dt:g}s 超过稳定上限 {dt_max}s"
                              f"（本网格重力波 CFL≈{dt_cfl:.0f}s，上限取 15 倍）。"
                              f"步长过大会导致数值发散：水位崩溃、全场变 NaN。建议 60~{int(dt_cfl * 3)}s。"),
                }), 400
            config["time"]["timestep"] = data["timestep"]
        if "step_2d" in data:
            if "io_spec" not in config:
                config["io_spec"] = {}
            config["io_spec"]["step_2d"] = data["step_2d"]
        if "step_3d" in data:
            if "io_spec" not in config:
                config["io_spec"] = {}
            config["io_spec"]["step_3d"] = data["step_3d"]
        write_getm_inp(inp_path, config)
        return jsonify({"success": True})

@app.route("/api/config/fabm")
def config_fabm():
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    fabm_path = active_case_path / "fabm.yaml"
    if not fabm_path.exists():
        return jsonify({"error": "fabm.yaml 不存在"}), 404
    return jsonify(parse_fabm_yaml(fabm_path))

@app.route("/api/config/fabm/param", methods=["POST"])
def config_fabm_param():
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    data = request.json
    module = data.get("module")
    param = data.get("param")
    value = data.get("value")
    fabm_path = active_case_path / "fabm.yaml"
    ok = update_fabm_parameter(fabm_path, module, param, value)
    return jsonify({"success": ok})

@app.route("/api/config/fabm/module", methods=["POST"])
def config_fabm_module():
    """Toggle a FABM module between enabled and disabled.

    Request body: {"module": "macrophytes", "enabled": false}
    Disabling moves the instance to top-level `_disabled`; enabling restores it.
    Before disabling, scans other enabled modules' coupling for references and
    returns them as warnings (the caller decides whether to proceed).
    """
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    data = request.json
    module = data.get("module")
    enabled = bool(data.get("enabled"))
    if not module:
        return jsonify({"error": "缺少 module 参数"}), 400
    fabm_path = active_case_path / "fabm.yaml"
    if not fabm_path.exists():
        return jsonify({"error": "fabm.yaml 不存在"}), 404
    force = bool(data.get("force", False))
    ok, warnings = toggle_fabm_module(fabm_path, module, enabled)
    if not ok:
        return jsonify({"success": False, "warnings": warnings}), 400
    if warnings and not force:
        # Refuse the operation but surface the dependent modules so the UI can confirm
        return jsonify({"success": False, "warnings": warnings, "needs_confirmation": True}), 409
    # Refresh cached fabm info
    global cached_fabm_info
    cached_fabm_info = parse_fabm_yaml(fabm_path)
    return jsonify({
        "success": True,
        "enabled": enabled,
        "module": module,
        "warnings": warnings,
        "fabm": cached_fabm_info,
    })

@app.route("/api/config/ghg", methods=["GET"])
def config_ghg_get():
    """GHG module status: yaml enablement, exe readiness, build progress."""
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    fabm_path = active_case_path / "fabm.yaml"
    if not fabm_path.exists():
        return jsonify({"error": "fabm.yaml 不存在"}), 404
    return jsonify({
        "enabled": _ghg_case_enabled(active_case_path),
        "exe_has_ghg": not _ghg_exe_is_stale(),
        "model_running": run_status == "running",
        "build": _ghg_build_snapshot(),
    })

@app.route("/api/config/ghg", methods=["POST"])
def config_ghg_post():
    """Toggle the greenhouse-gas modules (wet/inorganic_carbon + wet/methane).

    Request body: {"enabled": true|false} and/or {"rebuild": true}.
    Enabling generates both instances with couplings derived from the
    current module set and — when the exe lacks the GHG modules — kicks off
    the build pipeline in the background (poll GET for progress). The bin
    exe is only replaced when no model is running; otherwise the fresh exe
    is deployed automatically before the next run start.
    """
    global cached_fabm_info
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    data = request.json or {}
    fabm_path = active_case_path / "fabm.yaml"
    if not fabm_path.exists():
        return jsonify({"error": "fabm.yaml 不存在"}), 404

    rebuild = bool(data.get("rebuild"))
    enabled = data.get("enabled")
    warnings = []
    changed = False
    if enabled is not None:
        ok, warnings = toggle_ghg_modules(fabm_path, bool(enabled))
        if not ok:
            return jsonify({"success": False, "warnings": warnings}), 400
        changed = True
        cached_fabm_info = parse_fabm_yaml(fabm_path)

    build_started = False
    if (changed and enabled) or rebuild:
        if _ghg_exe_is_stale():
            build_started = _ghg_start_build()
            if not build_started:
                warnings.append("编译已在进行中")
            if run_status == "running":
                warnings.append("模型正在运行：配置与编译正常进行，新程序将在下次启动运行前自动部署")
        elif rebuild:
            warnings.append("当前程序已包含温室气体模块，无需编译")

    return jsonify({
        "success": True,
        "enabled": _ghg_case_enabled(active_case_path),
        "warnings": warnings,
        "build_started": build_started,
        "build": _ghg_build_snapshot(),
        "model_running": run_status == "running",
        "fabm": cached_fabm_info,
    })

@app.route("/api/config/hotstart", methods=["GET", "POST"])
def config_hotstart():
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    inp_path = active_case_path / "getm.inp"
    if request.method == "GET":
        config = parse_getm_inp(inp_path)
        param = config.get("param", {})
        return jsonify({
            "enabled": param.get("hotstart", False),
            "file": param.get("hotstart_file", ""),
            "type": param.get("hotstarttype", 1),
        })
    else:
        data = request.json
        config = parse_getm_inp(inp_path)
        if "param" not in config:
            config["param"] = {}
        config["param"]["hotstart"] = data.get("enabled", False)
        if "file" in data:
            config["param"]["hotstart_file"] = data.get("file", "")
        write_getm_inp(inp_path, config)
        return jsonify({"success": True})

def _parse_output_yaml(out_path):
    """Parse output.yaml via regex — avoids PyYAML's failure on `source: *`
    (a bare wildcard `*` that FABM accepts but PyYAML treats as an alias).
    Returns dict with keys time_unit, time_step, sync_interval, variables (raw text).
    """
    text = Path(out_path).read_text(encoding="utf-8", errors="replace")
    tu = re.search(r"time_unit\s*:\s*['\"]?(\w+)['\"]?", text)
    ts = re.search(r"time_step\s*:\s*([0-9.]+)", text)
    si = re.search(r"sync_interval\s*:\s*(-?[0-9.]+)", text)
    # Extract the `variables:` block as raw text (everything after the variables: line)
    var_match = re.search(r"\n\s*variables\s*:\s*\n(.*)$", text, re.DOTALL)
    variables_raw = var_match.group(1).strip() if var_match else ""
    return {
        "time_unit": tu.group(1) if tu else "day",
        "time_step": int(ts.group(1)) if ts and ts.group(1).isdigit() else (float(ts.group(1)) if ts else 1),
        "sync_interval": int(si.group(1)) if si and "." not in si.group(1) else (float(si.group(1)) if si else 0),
        "variables_raw": variables_raw,
    }

# ── Output subscription (P0) ─────────────────────────────────────────────
# FABM's output manager (flexout) resolves each `source:` entry as:
#   `*`        → root category = EVERY registered variable (the 17.9 GB trap)
#   `NAME/*`   → category NAME (one FABM model instance, e.g. `abiotic_water/*`)
#   `NAME`     → that single variable by exact name
# See src/gotm/extern/flexout/src/output_manager.F90:683-704.
# 注意：flexout 的 field manager 只注册了 temp/salt/hn/z/D 这几个水动力场
# （实测 NativeTest 全量输出 output.nc 中仅有这 5 个）。elev/u/v 由 GETM 原生
# *.2d.nc 输出，并未注册到 field manager —— 在 output.yaml 里显式请求会直接
# 致命退出：wrap_field: Requested output field "v" has not been registered
# with field manager. STOP 1（2026-09-23 滇池运行启动即崩溃实锤）。
_OUTPUT_HYDRO_VARS = ["temp", "salt", "hn", "z", "D"]
_OUTPUT_UNREGISTERED = {
    "elev": "水位 elev 由 GETM 原生 *.2d.nc 输出，不能写入 output.yaml",
    "u": "流速 u 由 GETM 原生 *.2d.nc 输出，不能写入 output.yaml",
    "v": "流速 v 由 GETM 原生 *.2d.nc 输出，不能写入 output.yaml",
}
_OUTPUT_HYDRO_2D = {"hn", "D", "bathymetry"}
_OUTPUT_KEY_MODULES = ("abiotic_water", "abiotic_sediment", "POM", "phytoplankton",
                       "zooplankton", "macrophytes", "fish", "benthos")


def _fabm_instances(case_path):
    """FABM instance names from fabm.yaml.

    Instance names are exactly the output categories usable as `source: NAME/*`.
    """
    p = Path(case_path) / "fabm.yaml"
    if not p.exists():
        return []
    out, in_block = [], False
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("instances:"):
            in_block = True
            continue
        if not in_block:
            continue
        m = re.match(r"^  ([A-Za-z_][A-Za-z_0-9]*):\s*$", line)
        if m:
            out.append({"name": m.group(1), "model": "", "long_name": ""})
            continue
        if out and line.startswith("    "):
            mm = re.match(r"^\s+(model|long_name)\s*:\s*(\S+)", line)
            if mm:
                out[-1][mm.group(1)] = mm.group(2)
            continue
        if line and not line.startswith(" "):
            break
    return out


def _parse_output_sources(variables_raw):
    """Extract `source:` entries from the raw `variables:` block."""
    return [m.group(1).strip().strip("'\"") for m in
            re.finditer(r"^\s*-\s*source\s*:\s*(.+?)\s*$", variables_raw or "", re.M)]


def _sources_to_yaml(sources):
    return "\n".join(f"      - source: {s}" for s in sources)


def _preset_sources(case_path, preset):
    """Variable selection presets: minimal / standard / all."""
    if preset == "all":
        return ["*"]
    if preset == "minimal":
        return list(_OUTPUT_HYDRO_VARS)
    inst = {m["name"] for m in _fabm_instances(case_path)}
    picked = [c for c in _OUTPUT_KEY_MODULES if c in inst]
    return list(_OUTPUT_HYDRO_VARS) + [f"{c}/*" for c in picked]


def _category_var_counts(case_path):
    """How many output variables each FABM category produced in the last run.

    Used only to make the size estimate concrete; falls back to a heuristic
    when no previous output file exists.
    """
    counts = {}
    try:
        of = find_output_files(Path(case_path))
        path = of.get("3d") or of.get("2d")
        if not path:
            return counts
        with nc_open(path) as ds:
            for name in ds.variables:
                if "_" in name:
                    cat = name.split("_")[0]
                    counts[cat] = counts.get(cat, 0) + 1
    except Exception:
        pass
    return counts


def _water_cells(case_path):
    b = Path(case_path) / "bathymetry.nc"
    if not b.exists():
        return 0
    try:
        with nc_open(b) as ds:
            if "bathymetry" not in ds.variables:
                return 0
            arr = np.ma.filled(np.ma.masked_invalid(
                np.asarray(ds.variables["bathymetry"][:], dtype="f8")), 0.0)
            return int((arr > 0).sum())
    except Exception:
        return 0


_TIME_UNIT_SEC = {"second": 1, "sec": 1, "minute": 60, "min": 60, "hour": 3600,
                  "day": 86400, "month": 2592000, "year": 31536000}


def _output_size_estimate(case_path, sources):
    """Rough estimate of the output file volume produced by `sources`."""
    info = {"available": False}
    try:
        inp = Path(case_path) / "getm.inp"
        if not inp.exists():
            return info
        cfg = parse_getm_inp(inp)
        tcfg = cfg.get("time", {})
        start = str(tcfg.get("start", "")).strip("'\"")
        stop = str(tcfg.get("stop", "")).strip("'\"")
        nlev = int(cfg.get("m3d", {}).get("M") or cfg.get("domain", {}).get("kdum") or 10)
        ncells = _water_cells(case_path)
        if not start or not stop or not ncells:
            return info
        t0 = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
        t1 = datetime.strptime(stop, "%Y-%m-%d %H:%M:%S")
        dur = max(0.0, (t1 - t0).total_seconds())
        parsed = _parse_output_yaml(Path(case_path) / "output.yaml")
        step = float(parsed["time_step"] or 1)
        unit = _TIME_UNIT_SEC.get(str(parsed["time_unit"]).lower(), 86400)
        interval = max(1.0, step * unit)
        ntime = int(dur / interval) + 1
        counts = _category_var_counts(case_path)
        n_inst = max(1, len(_fabm_instances(case_path)))
        total_known = sum(counts.values())
        n_vars, n_values_per_cell = 0, 0
        for s in sources:
            s = s.strip()
            if s == "*":
                k = total_known if total_known else 30 * n_inst
                n_vars += k
                n_values_per_cell += k * nlev
            elif s.endswith("/*"):
                cat = s[:-2]
                k = counts.get(cat, 30)
                n_vars += k
                n_values_per_cell += k * nlev
            else:
                n_vars += 1
                n_values_per_cell += 1 if s in _OUTPUT_HYDRO_2D else nlev
        nbytes = ntime * ncells * n_values_per_cell * 4  # NETCDF3 float32
        info.update({
            "available": True,
            "ntime": ntime, "ncells": ncells, "nlev": nlev,
            "n_vars": n_vars,
            "bytes": nbytes,
            "gb": round(nbytes / 1e9, 2),
            "mb": round(nbytes / 1e6, 1),
            "measured_counts": bool(counts),
        })
    except Exception:
        pass
    return info


@app.route("/api/config/output", methods=["GET", "POST"])
def config_output():
    """Read/write output.yaml.

    POST validates that sync_interval > 0; setting it to 0 throws 400 because
    a sync_interval of 0 causes FABM to drop all output time steps, which is
    what wiped out the Lake Luoma results.
    """
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    out_path = active_case_path / "output.yaml"
    if not out_path.exists():
        return jsonify({"error": "output.yaml 不存在"}), 404
    if request.method == "GET":
        parsed = _parse_output_yaml(out_path)
        sources = _parse_output_sources(parsed["variables_raw"]) or ["*"]
        return jsonify({
            "time_unit": parsed["time_unit"],
            "time_step": parsed["time_step"],
            "sync_interval": parsed["sync_interval"],
            "variables_raw": parsed["variables_raw"],
            # ── subscription ──
            "sources": sources,
            "modules": _fabm_instances(active_case_path),
            "hydro_vars": _OUTPUT_HYDRO_VARS,
            "has_wildcard": "*" in sources,
            "estimate": _output_size_estimate(active_case_path, sources),
        })
    else:
        data = request.json or {}
        parsed = _parse_output_yaml(out_path)
        sync_interval = data.get("sync_interval")
        # sync_interval is only mandatory when it is actually being changed —
        # a pure variable-subscription call must not be forced to resend it.
        if sync_interval is None and data.get("preset") is None and data.get("sources") is None:
            return jsonify({"error": "缺少 sync_interval 参数"}), 400
        if sync_interval is None:
            sync_interval = parsed["sync_interval"]
        if not isinstance(sync_interval, (int, float)) or sync_interval <= 0:
            return jsonify({
                "error": f"sync_interval 必须 > 0（当前为 {sync_interval}）。sync_interval=0 会导致 FABM 输出文件 time 维度为 0，所有模拟结果丢失。"
            }), 400
        parsed = _parse_output_yaml(out_path)
        time_unit = data.get("time_unit", parsed["time_unit"])
        time_step = data.get("time_step", parsed["time_step"])
        # Variable subscription: either an explicit source list, a preset, or
        # the raw block (kept verbatim so `source: *` is not mangled).
        sources = data.get("sources")
        preset = data.get("preset")
        if preset:
            sources = _preset_sources(active_case_path, preset)
        if sources is not None:
            if not isinstance(sources, list) or not sources:
                return jsonify({"error": "sources 必须是非空数组"}), 400
            sources = [str(s).strip() for s in sources if str(s).strip()]
            # 致命防护：显式请求 field manager 未注册的变量会让 GETM 启动即
            # STOP 1（wrap_field: Requested output field ... not registered）
            bad = [s for s in sources if s in _OUTPUT_UNREGISTERED]
            if bad:
                why = _OUTPUT_UNREGISTERED[bad[0]]
                return jsonify({
                    "error": (f"变量 {bad[0]} 不能写入 output.yaml：{why}。"
                              f"否则模型启动时会以 wrap_field ... not registered 致命退出。"
                              f"水动力可订阅变量仅有：{'、'.join(_OUTPUT_HYDRO_VARS)}。")
                }), 400
            variables_raw = _sources_to_yaml(sources)
        else:
            sources = _parse_output_sources(parsed["variables_raw"]) or ["*"]
            # Preserve variables block as-is (the `source: *` wildcard is invalid YAML alias syntax
            # but FABM accepts it; rewriting it via yaml.dump would break it)
            variables_raw = data.get("variables_raw") or parsed["variables_raw"]
        si_out = int(sync_interval) if float(sync_interval).is_integer() else sync_interval
        new_text = (
            f"output:\n"
            f"   time_unit: {time_unit}\n"
            f"   time_step: {time_step}\n"
            f"   sync_interval: {si_out}\n"
            f"   variables:\n"
        )
        if variables_raw:
            new_text += variables_raw + "\n"
        else:
            new_text += "      - source: *\n"
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_text)
        est = _output_size_estimate(active_case_path, sources)
        return jsonify({
            "success": True,
            "sync_interval": si_out,
            "sources": sources,
            "estimate": est,
            "warning": (f"预计输出约 {est['gb']} GB（{est['ntime']} 个时步 × {est['ncells']} 个水格 × "
                        f"{est['n_vars']} 个变量）。磁盘或后处理可能吃不消，建议改用“精简/标准”订阅。")
                       if est.get("available") and est.get("gb", 0) >= 2 else None,
        })

# ── Routes: Run Control ───────────────────────────────────────────────

@app.route("/api/run/estimate")
def run_estimate():
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    config = parse_getm_inp(active_case_path / "getm.inp")
    return jsonify(estimate_run_time(active_case_path, config))

@app.route("/api/run/check")
def run_check():
    """Pre-flight health check — everything that produced a silent failure this
    week (CFL divergence, empty output shells, missing forcing, 17.9 GB dumps).

    Returns {"checks": [{level, title, detail, fix}], "ok": bool, "blocking": n}
    where level ∈ error | warn | ok.
    """
    checks = []

    def add(level, title, detail, fix=None):
        checks.append({"level": level, "title": title, "detail": detail, "fix": fix})

    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    case_path = active_case_path
    inp_path = case_path / "getm.inp"
    if not inp_path.exists():
        return jsonify({"checks": [{"level": "error", "title": "缺少 getm.inp",
                                    "detail": "案例目录中没有 getm.inp，无法运行。",
                                    "fix": "在“运行设置”里保存一次参数即可生成。"}],
                        "ok": False, "blocking": 1})
    config = parse_getm_inp(inp_path)
    tcfg = config.get("time", {}) or {}

    # 1 ── bathymetry
    bathy = str((config.get("domain", {}) or {}).get("bathymetry", "bathymetry.nc")).strip("'\"")
    bp = case_path / bathy
    ncells = 0
    if not bp.exists():
        add("error", "缺少地形文件", f"getm.inp 指定 bathymetry={bathy}，但文件不存在。",
            "回到“前处理”重新生成地形。")
    else:
        ncells = _water_cells(case_path)
        if ncells == 0:
            add("error", "地形没有水域", f"{bathy} 中没有任何水深 > 0 的网格。",
                "检查水深插值/边界，或重新上传水深数据。")
        else:
            add("ok", "地形", f"{ncells} 个水格（{bathy}）")

    # 2 ── timestep / CFL
    dt = tcfg.get("timestep")
    dt_max, dt_cfl = _cfl_max_timestep(case_path)
    try:
        dt_f = float(dt)
    except (TypeError, ValueError):
        dt_f = None
    if dt_f is None:
        add("warn", "时间步长缺失", "getm.inp 中未找到 timestep。", "在“运行设置”里设置时间步长。")
    elif dt_max and dt_f > dt_max:
        add("error", "时间步长超过稳定上限",
            f"timestep={dt_f:g}s，CFL 临界约 {dt_cfl:.0f}s，本案例上限 {dt_max:g}s。"
            f"超限时模型会静默发散（全湖变干、输出全 NaN）。",
            f"把时间步长改为 60~{int(dt_cfl * 3)}s。")
    else:
        add("ok", "时间步长", f"{dt_f:g}s（CFL 临界约 {dt_cfl:.0f}s，上限 {dt_max:g}s）")
    if (config.get("domain", {}) or {}).get("check_cfl") is False:
        add("warn", "check_cfl 已关闭",
            "check_cfl=.false. 时 GETM 不会因 CFL 超限而中止，只会静默发散。",
            "调试期建议设为 .true.。")

    # 3 ── output config
    out_path = case_path / "output.yaml"
    if not out_path.exists():
        add("warn", "缺少 output.yaml", "没有输出配置，FABM 变量不会被写出。", "保存一次输出设置。")
    else:
        parsed = _parse_output_yaml(out_path)
        if not parsed["sync_interval"] or float(parsed["sync_interval"]) <= 0:
            add("error", "sync_interval = 0",
                "sync_interval=0 会让输出文件 time 维度为 0，跑完也读不到任何数据。",
                "把 sync_interval 设为 ≥ 1。")
        sources = _parse_output_sources(parsed["variables_raw"]) or ["*"]
        bad = [s for s in sources if s in _OUTPUT_UNREGISTERED]
        if bad:
            add("error", "输出订阅含未注册变量",
                f"output.yaml 请求了 {', '.join(bad)}，但 field manager 未注册它"
                f"（{_OUTPUT_UNREGISTERED[bad[0]]}）。模型启动时会以 "
                f"wrap_field ... not registered 致命退出（STOP 1）。",
                f"在“时间设置 → 输出变量”里去掉 {bad[0]}，或改用“标准/精简”预设。")
        est = _output_size_estimate(case_path, sources)
        if "*" in sources:
            add("warn", "输出全部变量",
                f"source: * 会写出模型注册的每一个变量。"
                + (f"预计约 {est['gb']} GB。" if est.get("available") else "")
                + "（滇池 362 天实测 17.9 GB）",
                "改用“标准”订阅：水动力 + 关键生态模块。")
        elif est.get("available"):
            gb = est.get("gb", 0)
            add("ok" if gb < 2 else "warn", "输出体积",
                f"预计 {gb} GB（{est['ntime']} 时步 × {est['ncells']} 水格 × {est['n_vars']} 变量）",
                None if gb < 2 else "减少订阅模块或加大 time_step 降采样。")

    # 4 ── forcing coverage
    try:
        for w in _ensure_forcing_coverage(case_path, config):
            add("warn", "驱动数据覆盖不足", w, "延长气象/入流数据，或缩短模拟时段。")
    except ValueError as e:
        add("error", "驱动文件损坏", str(e), "重新生成气象/入流输入。")

    # 5 ── stale / empty output from the previous run
    try:
        of = find_output_files(case_path)
        for kind, path in of.items():
            if not path or not Path(path).exists():
                continue
            nt = get_ntimesteps(path)
            if nt == 0:
                add("warn", "上次输出是空壳",
                    f"{Path(path).name} 存在但 time 维度为 0 条记录，"
                    f"占用 {Path(path).stat().st_size / 1e6:.1f} MB 却没有任何数据。",
                    "删除该文件后重跑；若重跑仍为 0，检查 sync_interval。")
    except Exception:
        pass

    # 6 ── disk space
    try:
        free = shutil.disk_usage(str(case_path)).free
        need = None
        if out_path.exists():
            srcs = _parse_output_sources(_parse_output_yaml(out_path)["variables_raw"]) or ["*"]
            e2 = _output_size_estimate(case_path, srcs)
            if e2.get("available"):
                need = e2["bytes"]
        if need and free < need * 1.2:
            add("error", "磁盘空间不足",
                f"预计输出 {need / 1e9:.1f} GB，当前可用 {free / 1e9:.1f} GB。",
                "减少输出变量或清理磁盘。")
        elif need:
            add("ok", "磁盘空间", f"预计输出 {need / 1e9:.2f} GB，可用 {free / 1e9:.1f} GB")
    except Exception:
        pass

    blocking = sum(1 for c in checks if c["level"] == "error")
    return jsonify({"checks": checks, "ok": blocking == 0, "blocking": blocking,
                    "n_warn": sum(1 for c in checks if c["level"] == "warn")})


@app.route("/api/run/start", methods=["POST"])
def run_start():
    global run_process, run_thread, run_status, run_logs, run_case_path
    if not active_case_path:
        return jsonify({"success": False, "error": "请先加载案例"}), 400
    if run_status == "running":
        return jsonify({"success": False, "error": "模型正在运行中"}), 400
    if not EXE_PATH.exists():
        return jsonify({"success": False, "error": f"可执行文件不存在: {EXE_PATH}"}), 400

    run_logs = []
    inp_path = active_case_path / "getm.inp"
    config = parse_getm_inp(inp_path) if inp_path.exists() else {}
    # Pre-flight: timestep sanity (CFL). A too-large timestep makes GETM
    # diverge silently (check_cfl=.false.): lake dries out, all-NaN output.
    _dt = config.get("time", {}).get("timestep") if isinstance(config, dict) else None
    _dt_max, _dt_cfl = _cfl_max_timestep(active_case_path)
    if _dt is not None and _dt_max:
        try:
            _dt = float(_dt)
        except (TypeError, ValueError):
            _dt = None
        if _dt and _dt > _dt_max:
            return jsonify({
                "success": False,
                "error": (f"拒绝运行：时间步长 {_dt:g}s 超过稳定上限 {_dt_max}s"
                          f"（CFL≈{_dt_cfl:.0f}s 的 15 倍）。请先在“运行设置”里把时间步长"
                          f"改小（建议 60~{int(_dt_cfl * 3)}s），否则模型数值发散、输出全为 NaN。"),
            }), 400
    # Pre-flight: forcing coverage (meteo/rivers must cover stop, else the
    # model dies with an EOF crash near the end of the run - Dianchi incident).
    try:
        for w in _ensure_forcing_coverage(active_case_path, config):
            run_logs.append(f"[WARN] {w}")
    except ValueError as e:
        return jsonify({"success": False, "error": f"驱动数据检查失败: {e}"}), 400
    # Pre-flight: when fabm.yaml enables the GHG modules the executable must
    # contain them, else FABM aborts at startup with an unknown-model fatal.
    if _ghg_case_enabled(active_case_path):
        try:
            _ghg_ensure_exe_for_run(run_logs)
        except ValueError as e:
            return jsonify({"success": False, "error": str(e)}), 400
    run_status = "running"
    run_case_path = active_case_path
    run_thread = threading.Thread(target=run_model_thread, args=(active_case_path, EXE_PATH), daemon=True)
    run_thread.start()
    return jsonify({"success": True})

@app.route("/api/run/status")
def run_status_api():
    elapsed = 0
    if run_start_time and run_status == "running":
        elapsed = time.time() - run_start_time

    # Parse progress from logs
    progress = 0
    current_step = 0
    for line in reversed(run_logs[-50:]):
        # 行首 n = NNN 才是步数；避免把 "len = 364"（气象时间维长度）误匹配成进度
        m = re.search(r"^\s*n\s*=\s*(\d+)", line)
        if m:
            current_step = int(m.group(1))
            break

    # Estimate total steps
    total_steps = 0
    if active_case_path:
        try:
            config = parse_getm_inp(active_case_path / "getm.inp")
            est = estimate_run_time(active_case_path, config)
            total_steps = est.get("nsteps", 0)
        except Exception:
            pass

    if total_steps > 0 and current_step > 0:
        progress = min(100, current_step / total_steps * 100)

    eta = 0
    if progress > 0 and elapsed > 0:
        eta = elapsed / progress * (100 - progress)

    return jsonify({
        "status": run_status,
        "logs": run_logs[-200:],
        "total_logs": len(run_logs),
        "elapsed": elapsed,
        "progress": progress,
        "current_step": current_step,
        "total_steps": total_steps,
        "eta_seconds": eta,
        "eta_minutes": eta / 60,
    })

@app.route("/api/run/stop", methods=["POST"])
def run_stop():
    global run_process, run_status
    if run_process and run_status == "running":
        run_process.terminate()
        try:
            run_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            run_process.kill()
        run_status = "stopped"
        run_logs.append("[INFO] 模型已被用户停止")
    return jsonify({"success": True})

# ── Routes: Results ───────────────────────────────────────────────────

@app.route("/api/geo/grid")
def geo_grid():
    """Grid geometry + bathymetry in geographic coordinates, for the map view.

    Returns ny×nx arrays of lon/lat/depth (null = land) so the browser can draw
    the model grid on top of a basemap and map a click back to (i, j).
    """
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    b = active_case_path / "bathymetry.nc"
    if not b.exists():
        return jsonify({"error": "bathymetry.nc 不存在（请先完成前处理）"}), 404
    try:
        with nc_open(b) as ds:
            if "bathymetry" not in ds.variables:
                return jsonify({"error": "bathymetry.nc 中没有 bathymetry 变量"}), 400
            depth = np.ma.filled(np.ma.masked_invalid(
                np.asarray(ds.variables["bathymetry"][:], dtype="f8")), np.nan)
            ny, nx = depth.shape
            lon = lat = None
            if "lonc" in ds.variables and "latc" in ds.variables:
                lon = np.ma.filled(np.ma.masked_invalid(
                    np.asarray(ds.variables["lonc"][:], dtype="f8")), np.nan)
                lat = np.ma.filled(np.ma.masked_invalid(
                    np.asarray(ds.variables["latc"][:], dtype="f8")), np.nan)
            x = np.asarray(ds.variables["x"][:], dtype="f8") if "x" in ds.variables else None
            y = np.asarray(ds.variables["y"][:], dtype="f8") if "y" in ds.variables else None
    except Exception as e:
        return jsonify({"error": f"读取 bathymetry.nc 失败: {e}"}), 500

    # Keep the payload sane for large grids
    stride = 1
    while (ny // stride) * (nx // stride) > 20000:
        stride += 1
    sl = (slice(None, None, stride), slice(None, None, stride))
    depth_s = depth[sl]
    land = ~(depth_s > 0)
    depth_out = np.where(land, np.nan, depth_s)
    dx = float(abs(x[1] - x[0])) if x is not None and len(x) > 1 else \
        (float(abs(y[1] - y[0])) if y is not None and len(y) > 1 else 0.0)
    out = {
        "nx": int(depth_s.shape[1]), "ny": int(depth_s.shape[0]),
        "nx_full": nx, "ny_full": ny, "stride": stride,
        "dx": dx,
        "depth": [[None if not np.isfinite(v) else round(float(v), 3) for v in row]
                  for row in depth_out],
        "has_lonlat": lon is not None,
    }
    if lon is not None:
        lon_s, lat_s = lon[sl], lat[sl]
        out["lon"] = [[None if not np.isfinite(v) else round(float(v), 6) for v in row]
                      for row in lon_s]
        out["lat"] = [[None if not np.isfinite(v) else round(float(v), 6) for v in row]
                      for row in lat_s]
        finite = np.isfinite(lon_s) & np.isfinite(lat_s)
        if finite.any():
            out["bounds"] = {"s": float(lat_s[finite].min()), "w": float(lon_s[finite].min()),
                             "n": float(lat_s[finite].max()), "e": float(lon_s[finite].max())}
    else:
        out["x"] = [float(v) for v in (x[::stride] if x is not None else [])]
        out["y"] = [float(v) for v in (y[::stride] if y is not None else [])]
        out["bounds"] = None
    return jsonify(out)


@app.route("/api/geo/field")
def geo_field():
    """A result field resampled onto the display grid (for map overlay).

    Same row/column ordering as /api/geo/grid (ny rows × nx cols).
    """
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    var = request.args.get("var", "temp")
    try:
        t = int(request.args.get("time", 0))
        level = int(request.args.get("level", -1))
    except ValueError:
        return jsonify({"error": "time/level 必须是整数"}), 400
    of = find_output_files(active_case_path)
    nc_path = of.get("3d") or of.get("2d")
    if not nc_path:
        return jsonify({"error": "没有可用的输出文件（请先运行模型）"}), 404
    try:
        with nc_open(nc_path) as ds:
            if var not in ds.variables:
                return jsonify({"error": f"变量 {var} 不存在"}), 404
            v = ds.variables[var]
            dims = list(v.dimensions)
            nt = len(ds.dimensions[dims[0]]) if dims and dims[0] in ds.dimensions else 0
            if nt == 0:
                return jsonify({"error": "输出文件没有任何时间记录"}), 404
            t = max(0, min(nt - 1, t))
            if v.ndim == 4:
                nz = v.shape[1]
                lev = nz - 1 if level < 0 else max(0, min(nz - 1, level))
                arr = v[t, lev, :, :]
            elif v.ndim == 3:
                arr = v[t, :, :]
            else:
                arr = v[:]
            a = np.ma.filled(np.ma.masked_invalid(np.asarray(arr, dtype="f8")), np.nan)
    except Exception as e:
        return jsonify({"error": f"读取字段失败: {e}"}), 500
    ny, nx = a.shape
    stride = 1
    while (ny // stride) * (nx // stride) > 20000:
        stride += 1
    a = a[::stride, ::stride]
    finite = np.isfinite(a)
    return jsonify({
        "var": var, "time": t, "level": level,
        "nx": int(a.shape[1]), "ny": int(a.shape[0]), "stride": stride,
        "values": [[None if not np.isfinite(v) else round(float(v), 5) for v in row]
                   for row in a],
        "min": float(a[finite].min()) if finite.any() else None,
        "max": float(a[finite].max()) if finite.any() else None,
    })


@app.route("/api/results/variables")
def results_variables():
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    if _output_locked():
        return jsonify({"error": "模型运行中，输出文件正在写入，暂不能读取"}), 409
    files = find_output_files(active_case_path)
    result = {"2d": [], "3d": []}
    if files["2d"]:
        result["2d"] = get_variable_list(files["2d"])
    if files["3d"]:
        result["3d"] = get_variable_list(files["3d"])
    result["timesteps_2d"] = get_ntimesteps(files["2d"]) if files["2d"] else 0
    result["timesteps_3d"] = get_ntimesteps(files["3d"]) if files["3d"] else 0
    # 真实日期标签（2d/3d 抽帧间隔通常 != 1 天，不能把帧序号当天数）
    result["time_labels_2d"] = _nc_time_labels(files["2d"]) if files["2d"] else []
    result["time_labels_3d"] = _nc_time_labels(files["3d"]) if files["3d"] else []
    return jsonify(result)

@app.route("/api/results/2d")
def results_2d():
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    if _output_locked():
        return jsonify({"error": "模型运行中，输出文件正在写入，暂不能读取"}), 409
    files = find_output_files(active_case_path)
    var_name = request.args.get("var", "temp")
    timestep = int(request.args.get("time", 0))
    level = int(request.args.get("level", 0))
    # Try 3D file first (has more vars), then 2D
    nc_path = files["3d"] or files["2d"]
    if not nc_path:
        return jsonify({"error": "没有输出文件"}), 404
    field = get_2d_field(nc_path, var_name, timestep, level)
    if field is None:
        return jsonify({"error": f"变量 {var_name} 不存在，或输出文件没有任何时间记录（上次运行可能异常中断或 sync_interval=0）"}), 404
    return jsonify(field)

@app.route("/api/results/timeseries")
def results_timeseries():
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    if _output_locked():
        return jsonify({"error": "模型运行中，输出文件正在写入，暂不能读取"}), 409
    files = find_output_files(active_case_path)
    var_name = request.args.get("var", "temp")
    i = request.args.get("i", type=int)
    j = request.args.get("j", type=int)
    region_str = request.args.get("region")
    lake_avg = request.args.get("lake_avg", "0") == "1"
    per_layer = request.args.get("per_layer", "0") == "1"
    tstride = request.args.get("tstride", type=int)

    nc_path = files["3d"] or files["2d"]
    if not nc_path:
        return jsonify({"error": "没有输出文件"}), 404

    region = None
    if region_str:
        parts = [int(x) for x in region_str.split(",")]
        if len(parts) == 4:
            region = tuple(parts)

    ts = get_timeseries(nc_path, var_name, i=i, j=j, region=region, lake_avg=lake_avg, per_layer=per_layer, tstride=tstride)
    if ts is None:
        return jsonify({"error": f"变量 {var_name} 不存在"}), 404
    if isinstance(ts, dict) and "error" in ts:
        return jsonify(ts), 400
    return jsonify(ts)

@app.route("/api/results/profile")
def results_profile():
    """Get vertical profile at a point."""
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    if _output_locked():
        return jsonify({"error": "模型运行中，输出文件正在写入，暂不能读取"}), 409
    files = find_output_files(active_case_path)
    var_name = request.args.get("var", "temp")
    timestep = int(request.args.get("time", 0))
    i = request.args.get("i", type=int)
    j = request.args.get("j", type=int)
    nc_path = files["3d"]
    if not nc_path:
        return jsonify({"error": "没有3D输出文件"}), 404
    with nc_open(nc_path) as ds:
        if var_name not in ds.variables:
            return jsonify({"error": "变量不存在"}), 404
        var = ds.variables[var_name]
        if var.ndim == 4 and var.shape[0] == 0:
            return jsonify({"error": "输出文件没有任何时间记录（上次运行可能异常中断或 sync_interval=0）"}), 404
        if var.ndim == 4:
            nt = var.shape[0]
            t = max(0, min(nt - 1, int(timestep))) if nt > 0 else 0
            if i is not None and j is not None:
                col = var[t, :, j, i]
                profile = (col.filled(np.nan) if isinstance(col, np.ma.MaskedArray) else np.asarray(col, dtype=float)).tolist()
            else:
                slab = var[t, :, :, :]
                slab = slab.filled(np.nan) if isinstance(slab, np.ma.MaskedArray) else np.asarray(slab, dtype=float)
                profile = np.nanmean(slab, axis=(1, 2)).tolist()
        else:
            profile = []
        sigma = ds.variables["sigma"][:].tolist() if "sigma" in ds.variables else list(range(len(profile)))
        return jsonify({
            "profile": profile,
            "sigma": sigma,
            "var_name": var_name,
            "units": getattr(var, "units", ""),
        })

# ── Routes: Calibration ───────────────────────────────────────────────

@app.route("/api/calibration/points", methods=["GET", "POST", "DELETE"])
def calibration_points_api():
    if request.method == "GET":
        return jsonify(calibration_points)
    elif request.method == "POST":
        data = request.json
        point = {
            "id": str(uuid.uuid4())[:8],
            "name": data.get("name", f"点位{len(calibration_points)+1}"),
            "i": data.get("i", 0),
            "j": data.get("j", 0),
            "variables": data.get("variables", []),
            "created_at": datetime.now().isoformat(),
        }
        calibration_points.append(point)
        save_calibration()
        return jsonify({"success": True, "point": point})
    else:
        pid = request.args.get("id")
        calibration_points[:] = [p for p in calibration_points if p["id"] != pid]
        save_calibration()
        return jsonify({"success": True})

@app.route("/api/calibration/data", methods=["GET", "POST"])
def calibration_data_api():
    if request.method == "GET":
        pid = request.args.get("point_id")
        var = request.args.get("variable")
        if pid and var:
            return jsonify(calibration_data.get(pid, {}).get(var, []))
        return jsonify(calibration_data)
    else:
        data = request.json
        pid = data.get("point_id")
        var = data.get("variable")
        values = data.get("values", [])
        if pid not in calibration_data:
            calibration_data[pid] = {}
        calibration_data[pid][var] = values
        save_calibration()
        return jsonify({"success": True})

# ── Calibration file upload helpers ───────────────────────────────────

def _normalize_calib_column(name):
    """Map a header string to canonical key (time/value/variable) or None."""
    if name is None:
        return None
    s = str(name).strip().lower()
    if s in ("time", "date", "datetime", "时间", "日期"):
        return "time"
    if s in ("value", "val", "数值", "值", "obs", "observed"):
        return "value"
    if s in ("variable", "var", "变量"):
        return "variable"
    return None

def _parse_csv_calibration(stream):
    """Parse a CSV stream, return list of dict rows with keys time/value/variable."""
    stream.seek(0)
    text = stream.read().decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise ValueError("CSV 文件没有表头")
    fieldmap = {}
    for fname in reader.fieldnames:
        key = _normalize_calib_column(fname)
        if key:
            fieldmap[fname] = key
    if "time" not in fieldmap.values() or "value" not in fieldmap.values():
        raise ValueError("CSV 必须包含 time 和 value 列（允许 'date' / 'datetime' / '时间' 作为 time，'obs' 作为 value）")
    rows = []
    for raw in reader:
        row = {}
        for k, v in raw.items():
            if k in fieldmap:
                row[fieldmap[k]] = v
        if row.get("time") in (None, "") or row.get("value") in (None, ""):
            continue
        try:
            float(row["value"])
        except (ValueError, TypeError):
            continue
        rows.append(row)
    return rows

def _parse_xlsx_calibration(file_storage):
    """Parse an XLSX file, return list of dict rows with keys time/value/variable."""
    try:
        from openpyxl import load_workbook
    except ImportError as e:
        raise ValueError("openpyxl 未安装，无法读取 xlsx") from e

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        tmp.write(file_storage.read())
        tmp_path = tmp.name
    try:
        wb = load_workbook(tmp_path, read_only=True, data_only=True)
        ws = wb.active
        rows_iter = ws.iter_rows(values_only=True)
        try:
            header = next(rows_iter)
        except StopIteration as e:
            raise ValueError("XLSX 文件为空") from e
        fieldmap = {}
        for idx, col in enumerate(header):
            key = _normalize_calib_column(col)
            if key and key not in fieldmap:
                fieldmap[key] = idx
        if "time" not in fieldmap or "value" not in fieldmap:
            raise ValueError("XLSX 必须包含 time 和 value 列")
        rows = []
        for r in rows_iter:
            row = {}
            for key, idx in fieldmap.items():
                val = r[idx] if idx < len(r) else None
                if val is not None and hasattr(val, "isoformat"):
                    val = val.isoformat(sep=" ")
                row[key] = val
            if row.get("time") in (None, "") or row.get("value") in (None, ""):
                continue
            try:
                float(row["value"])
            except (ValueError, TypeError):
                continue
            rows.append(row)
        return rows
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

@app.route("/api/calibration/upload", methods=["POST"])
def calibration_upload():
    """Upload calibration data from an xlsx/csv file.

    Form fields:
      - file: xlsx or csv file (required)
      - point_id: existing calibration point id (required)
      - variable: optional default variable name (default 'temp');
                  superseded by a 'variable' column in the file when present.

    File must contain `time` and `value` columns; an optional `variable`
    column allows multiple variables in one file. Numeric `value` entries
    are required; rows with missing or non-numeric values are skipped.
    """
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    if "file" not in request.files:
        return jsonify({"error": "未提供文件"}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "文件名为空"}), 400
    point_id = request.form.get("point_id")
    if not point_id:
        return jsonify({"error": "缺少 point_id"}), 400
    point = next((p for p in calibration_points if p["id"] == point_id), None)
    if not point:
        return jsonify({"error": f"率定点位 {point_id} 不存在"}), 404
    default_var = request.form.get("variable", "temp").strip() or "temp"
    filename = f.filename.lower()
    try:
        if filename.endswith(".csv"):
            rows = _parse_csv_calibration(f.stream)
        elif filename.endswith(".xlsx") or filename.endswith(".xls"):
            rows = _parse_xlsx_calibration(f)
        else:
            return jsonify({"error": "不支持的文件格式（仅 .csv, .xlsx）"}), 400
    except ValueError as e:
        return jsonify({"error": f"解析失败: {e}"}), 400
    except Exception as e:
        return jsonify({"error": f"读取文件失败: {e}"}), 500
    if not rows:
        return jsonify({"error": "文件中没有有效数据行"}), 400
    if point_id not in calibration_data:
        calibration_data[point_id] = {}
    stored = defaultdict(int)
    for row in rows:
        var = row.get("variable") or default_var
        if not isinstance(var, str):
            var = str(var)
        var = var.strip() or default_var
        calibration_data[point_id].setdefault(var, []).append({
            "time": str(row["time"]),
            "value": float(row["value"]),
        })
        stored[var] += 1
    save_calibration()
    return jsonify({
        "success": True,
        "point_id": point_id,
        "stored": dict(stored),
        "total_rows": len(rows),
    })

@app.route("/api/calibration/comparison")
def calibration_comparison():
    """Get simulated vs observed comparison for a calibration point.

    Returns simulated and observed time series plus paired (sim, obs) values
    matched by nearest timestamp within a tolerance window, suitable for
    scatter plotting with a 1:1 reference line.
    """
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    if _output_locked():
        return jsonify({"error": "模型运行中，输出文件正在写入，暂不能读取"}), 409
    pid = request.args.get("point_id")
    var = request.args.get("variable")
    point = next((p for p in calibration_points if p["id"] == pid), None)
    if not point:
        return jsonify({"error": "率定点位不存在"}), 404

    files = find_output_files(active_case_path)
    nc_path = files["3d"] or files["2d"]
    if not nc_path:
        return jsonify({"error": "没有输出文件"}), 404

    # Get simulated time series
    sim = get_timeseries(nc_path, var, i=point["i"], j=point["j"])
    obs = calibration_data.get(pid, {}).get(var, [])

    # Pair observed and simulated by nearest timestamp.
    scatter_pairs, axis_range = _pair_obs_sim(obs, sim)
    return jsonify({
        "point": point,
        "variable": var,
        "simulated": sim,
        "observed": obs,
        "scatter_pairs": scatter_pairs,
        "axis_range": axis_range,
    })

def _parse_iso_time(s):
    """Best-effort ISO-8601 / YYYY-MM-DD[ HH:MM:SS] parser returning datetime or None."""
    if s is None:
        return None
    if isinstance(s, datetime):
        return s
    s = str(s).strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M",
                "%Y-%m-%d", "%Y/%m/%d %H:%M:%S", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    # Last resort: numeric epoch (hours or seconds since some origin)
    try:
        v = float(s)
        return datetime(2000, 1, 1) + timedelta(seconds=v)
    except (ValueError, TypeError):
        return None

def _pair_obs_sim(obs_list, sim_dict, max_lag_hours=24):
    """Pair observed and simulated by nearest time within `max_lag_hours`.

    Returns (pairs, axis_range) where pairs is a list of {time, obs, sim} and
    axis_range is the symmetric min/max for scatter plot bounds (covers the
    1:1 reference line).
    """
    if not obs_list or not sim_dict:
        return [], {"min": 0, "max": 1}
    sim_times_raw = sim_dict.get("times", [])
    sim_vals = sim_dict.get("values", [])
    if not sim_times_raw or len(sim_times_raw) != len(sim_vals):
        return [], {"min": 0, "max": 1}
    sim_dt = [(_parse_iso_time(t) if isinstance(t, str) else None) for t in sim_times_raw]
    pairs = []
    all_vals = []
    for o in obs_list:
        ot = _parse_iso_time(o.get("time"))
        ov = o.get("value")
        try:
            ov = float(ov)
        except (ValueError, TypeError):
            continue
        if ot is None:
            continue
        best_idx = -1
        best_lag = None
        for i, sdt in enumerate(sim_dt):
            if sdt is None:
                continue
            lag = abs((sdt - ot).total_seconds())
            if best_lag is None or lag < best_lag:
                best_lag = lag
                best_idx = i
        if best_idx < 0 or best_lag is None:
            continue
        if best_lag > max_lag_hours * 3600:
            continue
        sv = sim_vals[best_idx]
        if sv is None or (isinstance(sv, float) and np.isnan(sv)):
            continue
        pairs.append({
            "time": sim_times_raw[best_idx],
            "obs": ov,
            "sim": float(sv),
        })
        all_vals.append(ov)
        all_vals.append(float(sv))
    if not all_vals:
        return [], {"min": 0, "max": 1}
    vmin = min(all_vals)
    vmax = max(all_vals)
    if vmin == vmax:
        vmin -= 1
        vmax += 1
    # Slightly pad for nicer plotting
    pad = (vmax - vmin) * 0.05
    return pairs, {"min": vmin - pad, "max": vmax + pad}

@app.route("/api/calibration/auto/config", methods=["GET", "POST"])
def calibration_auto_config():
    config_path = DATA_DIR / "auto_calib_config.json"
    if request.method == "GET":
        return jsonify(load_json(config_path, {
            "method": "parsac",
            "parameters": [],
            "n_iterations": 100,
            "objective_function": "rmse",
            "status": "idle",
        }))
    else:
        save_json(config_path, request.json)
        return jsonify({"success": True})

@app.route("/api/calibration/auto/start", methods=["POST"])
def calibration_auto_start():
    """Start a real calibration job in a background thread.

    Request body:
      method: parsac | pest | bayesian | sensitivity
      iterations: int (max iterations)
      objective: rmse | nse | r2 | mae
      params: list of {module, param, min, max}

    Returns {success, job_id, message}.
    """
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    data = request.json or {}
    method = data.get("method", "parsac")
    max_iter = int(data.get("iterations", 100))
    objective = data.get("objective", "rmse")
    params = data.get("params", [])
    if not params:
        return jsonify({"error": "请至少选择一个率定参数"}), 400
    # Validate parameter structure
    for p in params:
        if not all(k in p for k in ("module", "param", "min", "max")):
            return jsonify({"error": f"参数缺少 module/param/min/max: {p}"}), 400
        if p["min"] >= p["max"]:
            return jsonify({"error": f"{p['module']}.{p['param']}: min 必须 < max"}), 400
    try:
        from calibration import start_calibration_job
    except ImportError as e:
        return jsonify({"error": f"率定模块加载失败: {e}"}), 500
    try:
        job_id = start_calibration_job(method, params, objective, max_iter, active_case_path)
    except Exception as e:
        return jsonify({"error": f"启动失败: {e}"}), 500
    # Persist last config for reference
    save_json(DATA_DIR / "auto_calib_config.json", {
        "method": method,
        "parameters": params,
        "n_iterations": max_iter,
        "objective_function": objective,
        "job_id": job_id,
        "started_at": datetime.now().isoformat(),
    })
    return jsonify({
        "success": True,
        "job_id": job_id,
        "message": f"已启动 {method} 率定（最大 {max_iter} 次迭代），后台运行中",
    })

@app.route("/api/calibration/auto/status")
def calibration_auto_status():
    """Get status of a calibration job. ?job_id=xxx"""
    job_id = request.args.get("job_id")
    if not job_id:
        return jsonify({"error": "缺少 job_id"}), 400
    try:
        from calibration import get_calibration_job
    except ImportError as e:
        return jsonify({"error": f"率定模块加载失败: {e}"}), 500
    job = get_calibration_job(job_id)
    if not job:
        return jsonify({"error": f"任务 {job_id} 不存在"}), 404
    return jsonify(job.to_dict())

@app.route("/api/calibration/auto/stop", methods=["POST"])
def calibration_auto_stop():
    """Stop a running calibration job."""
    data = request.json or {}
    job_id = data.get("job_id")
    if not job_id:
        return jsonify({"error": "缺少 job_id"}), 400
    try:
        from calibration import get_calibration_job
    except ImportError as e:
        return jsonify({"error": f"率定模块加载失败: {e}"}), 500
    job = get_calibration_job(job_id)
    if not job:
        return jsonify({"error": f"任务 {job_id} 不存在"}), 404
    job.stop()
    return jsonify({"success": True, "job_id": job_id, "status": job.status})

@app.route("/api/calibration/auto/apply", methods=["POST"])
def calibration_auto_apply():
    """Apply best parameters from a completed job to the active fabm.yaml."""
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    data = request.json or {}
    job_id = data.get("job_id")
    if not job_id:
        return jsonify({"error": "缺少 job_id"}), 400
    try:
        from calibration import get_calibration_job
    except ImportError as e:
        return jsonify({"error": f"率定模块加载失败: {e}"}), 500
    job = get_calibration_job(job_id)
    if not job:
        return jsonify({"error": f"任务 {job_id} 不存在"}), 404
    if not job.result or not job.result.get("best_params"):
        return jsonify({"error": "任务尚无可应用的结果"}), 400
    fabm_path = active_case_path / "fabm.yaml"
    try:
        update_fabm_parameter_batch(fabm_path, job.result["best_params"])
    except Exception as e:
        return jsonify({"error": f"应用参数失败: {e}"}), 500
    global cached_fabm_info
    cached_fabm_info = parse_fabm_yaml(fabm_path)
    return jsonify({
        "success": True,
        "applied": job.result["best_params"],
        "objective": job.result.get("best_objective"),
    })

# ── Routes: State Variables Dashboard ─────────────────────────────────

@app.route("/api/dashboard/summary")
def dashboard_summary():
    """Get summary of key state variables for dashboard."""
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    # 模型运行中禁止读输出文件：模型进程在写、API 线程在读时 HDF5 并发
    # 访问会触发访问冲突（0xC0000005）直接杀死整个服务进程。
    if _output_locked():
        return jsonify({"error": "模型运行中，输出文件正在写入，暂不能读取"}), 409
    files = find_output_files(active_case_path)
    nc_path = files["3d"] or files["2d"]
    if not nc_path:
        return jsonify({"error": "没有输出文件"}), 404

    # WET 实际变量名（带模块前缀，由 fabm 输出）。诊断汇总变量如 wet_chla、wet_totN/P/C。
    key_vars = [
        "temp", "abiotic_water_sO2W", "abiotic_water_sNO3W", "abiotic_water_sNH4W",
        "abiotic_water_sPO4W", "abiotic_water_sSiO2W",
        "wet_chla", "POM_sDW", "DOM_sDW", "humus_sDW",
        "wet_totN", "wet_totP", "wet_totC",
    ]
    summary = {}
    with nc_open(nc_path) as ds:
        nt = get_ntimesteps(nc_path)
        for vname in key_vars:
            if vname in ds.variables:
                var = ds.variables[vname]
                # 崩溃/中断的运行会留下"已创建但从未写入"的变量（time 长度 0），
                # 读取会 IndexError（2026-09-20 事故），跳过即可。
                if var.shape[0] == 0:
                    continue

                def _fill(a):
                    return a.filled(np.nan) if isinstance(a, np.ma.MaskedArray) else np.asarray(a, dtype=float)

                # 只读最新时步（hyperslab）——整变量读取在滇池级案例上是 GB 级 IO
                if var.ndim == 4:
                    # GETM sigma: index 0 = 底层, -1 = 表层
                    field = _fill(var[-1, -1, :, :])
                elif var.ndim == 3:
                    field = _fill(var[-1, :, :])
                else:
                    continue
                summary[vname] = {
                    "long_name": getattr(var, "long_name", vname),
                    "units": getattr(var, "units", ""),
                    "min": float(np.nanmin(field)) if not np.all(np.isnan(field)) else None,
                    "max": float(np.nanmax(field)) if not np.all(np.isnan(field)) else None,
                    "mean": float(np.nanmean(field)) if not np.all(np.isnan(field)) else None,
                    "ntimesteps": nt,
                }
    return jsonify(summary)

def _point_in_polygon(x, y, poly):
    """Ray-casting point-in-polygon test. poly is a list of (x, y) tuples."""
    n = len(poly)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi):
            inside = not inside
        j = i
    return inside

@app.route("/api/results/3d_surface")
def results_3d_surface():
    """Return downsampled 3D volume for Plotly isosurface / point-cloud rendering.

    Strides the 3D array to ~`target` cells per axis to prevent browser OOM.
    `target` (查询参数，默认 30) 由前端质量档位控制：低=16 / 中=22 / 高=30。
    """
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    if _output_locked():
        return jsonify({"error": "模型运行中，输出文件正在写入，暂不能读取"}), 409
    files = find_output_files(active_case_path)
    var_name = request.args.get("var", "temp")
    timestep = int(request.args.get("time", 0))
    target = max(8, min(40, int(request.args.get("target", 30))))
    nc_path = files["3d"]
    if not nc_path:
        return jsonify({"error": "没有3D输出文件"}), 404

    with nc_open(nc_path) as ds:
        if var_name not in ds.variables:
            return jsonify({"error": f"变量 {var_name} 不存在"}), 404
        var = ds.variables[var_name]
        if var.ndim != 4:
            return jsonify({"error": f"变量 {var_name} 不是4D（time,z,y,x）"}), 400
        nt = var.shape[0]
        if nt == 0:
            return jsonify({"error": "输出文件没有任何时间记录（上次运行可能异常中断或 sync_interval=0）"}), 404
        t = max(0, min(nt - 1, int(timestep))) if nt > 0 else 0
        # 只读该时步的 (z,y,x) 切片——单时步约百 KB 级；整变量读取是数百 MB
        slab = var[t]
        if isinstance(slab, np.ma.MaskedArray):
            slab = slab.filled(np.nan)
        else:
            slab = np.asarray(slab, dtype=float)
        nzt, nyt, nxt = slab.shape[0], slab.shape[1], slab.shape[2]
        stride_z = max(1, nzt // target)
        stride_y = max(1, nyt // target)
        stride_x = max(1, nxt // target)
        vol = slab[::stride_z, ::stride_y, ::stride_x]
        # Replace NaN with None for JSON (Plotly treats null as transparent)
        vol_list = np.where(np.isnan(vol), None, vol).tolist()

        # ── 立体水体渲染所需的几何信息 ───────────────────────────────────
        # sigma：垂向坐标。GETM 常用 [-1,0]（-1=底 / 0=面），也有 [0,1] 约定，
        # 前端按实际符号自动判别，这里原样下发。
        if "sigma" in ds.variables:
            sigma = [float(v) for v in ds.variables["sigma"][:]]
            if len(sigma) > nzt:                      # 界面数 = 层数+1，取层中心
                mid = []
                for k in range(nzt):
                    a = sigma[k]
                    b = sigma[k + 1] if (k + 1) < len(sigma) else (2 * sigma[k] - sigma[max(0, k - 1)] if k > 0 else sigma[k])
                    mid.append(0.5 * (a + b))
                sigma = mid
            elif len(sigma) < nzt:
                sigma = sigma + [sigma[-1]] * (nzt - len(sigma))
        else:
            sigma = [2 * k / max(1, nzt - 1) - 1 for k in range(nzt)]

        # 水平坐标：真实米制（保持长宽比与湖泊真实形状），缺省退回格点序号
        if "xc" in ds.variables and "yc" in ds.variables:
            xc_all = np.asarray(ds.variables["xc"][:], dtype=float)
            yc_all = np.asarray(ds.variables["yc"][:], dtype=float)
            xc = xc_all[::stride_x].tolist()
            yc = yc_all[::stride_y].tolist()
        else:
            xc = [float(i) for i in range(vol.shape[2])]
            yc = [float(j) for j in range(vol.shape[1])]

        # 湖底地形：与 vol 同步长降采样，陆地格为 None
        # 注意：GETM 输出里陆地格的 bathymetry 原生值是 -10.0（不是 NaN），
        # 必须用 masked.filled(nan) 转换，否则陆地会被当成 10m 深的洞画进湖底。
        bottom = None
        if "bathymetry" in ds.variables:
            try:
                _b = ds.variables["bathymetry"][:]
                if isinstance(_b, np.ma.MaskedArray):
                    b_all = np.asarray(_b.filled(np.nan), dtype=float)
                else:
                    b_all = np.asarray(_b, dtype=float)
                b_sub = b_all[::stride_y, ::stride_x]
                bottom = np.where(np.isnan(b_sub), None, b_sub).tolist()
                if (not bottom) or len(bottom) != vol.shape[1] or (not bottom[0]) or len(bottom[0]) != vol.shape[2]:
                    bottom = None
            except Exception:
                bottom = None

        return jsonify({
            "data": vol_list,
            "shape": list(vol.shape),
            "x": list(range(vol.shape[2])),
            "y": list(range(vol.shape[1])),
            "z": list(range(vol.shape[0])),
            "xc": xc,
            "yc": yc,
            "sigma": sigma,
            "bottom": bottom,
            "timestep": t,
            "min": float(np.nanmin(vol)) if not np.all(np.isnan(vol)) else 0,
            "max": float(np.nanmax(vol)) if not np.all(np.isnan(vol)) else 0,
            "var_name": var_name,
            "long_name": getattr(var, "long_name", var_name),
            "units": getattr(var, "units", ""),
        })

@app.route("/api/results/state_vars_surface")
def results_state_vars_surface():
    """Return surface fields for 6 key state variables (mini-heatmap dashboard).

    Returns {var_name: {data, shape, min, max, mean, long_name, units}} for the
    last timestep's surface layer of temp, O2, NO3, PO4, chla, POM.
    WET 输出变量名带模块前缀（如 abiotic_water_sO2W），最末层为表层
    （GETM sigma 约定：index 0=底，最后一层=面）。
    """
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    if _output_locked():
        return jsonify({"error": "模型运行中，输出文件正在写入，暂不能读取"}), 409
    files = find_output_files(active_case_path)
    nc_path = files["3d"] or files["2d"]
    if not nc_path:
        return jsonify({"error": "没有输出文件"}), 404

    # 显示名 -> WET 实际变量名映射
    key_vars = [
        ("温度", "temp"),
        ("溶解氧", "abiotic_water_sO2W"),
        ("硝酸盐", "abiotic_water_sNO3W"),
        ("磷酸盐", "abiotic_water_sPO4W"),
        ("叶绿素a", "wet_chla"),
        ("颗粒有机物D", "POM_sDW"),
    ]
    result = {}
    with nc_open(nc_path) as ds:
        nt = get_ntimesteps(nc_path)
        t_idx = -1 if nt > 0 else 0
        for display_name, vname in key_vars:
            if vname in ds.variables:
                var = ds.variables[vname]
                if var.ndim not in (3, 4) or var.shape[0] == 0:
                    continue

                def _fill(a):
                    return a.filled(np.nan) if isinstance(a, np.ma.MaskedArray) else np.asarray(a, dtype=float)

                # 只读最新时步表层（hyperslab）——滇池级案例整变量读取为 GB 级 IO
                if var.ndim == 4:
                    # GETM sigma: index 0 = 底层, -1 = 表层
                    field = _fill(var[t_idx, -1, :, :])
                else:
                    field = _fill(var[t_idx, :, :])
                result[vname] = {
                    "display_name": display_name,
                    "data": np.where(np.isnan(field), None, field).tolist(),
                    "shape": list(field.shape),
                    "min": float(np.nanmin(field)) if not np.all(np.isnan(field)) else None,
                    "max": float(np.nanmax(field)) if not np.all(np.isnan(field)) else None,
                    "mean": float(np.nanmean(field)) if not np.all(np.isnan(field)) else None,
                    "long_name": getattr(var, "long_name", vname),
                    "units": getattr(var, "units", ""),
                }
    return jsonify(result)

@app.route("/api/results/timeseries_polygon", methods=["POST"])
def results_timeseries_polygon():
    """Time series averaged over a polygon region.

    Body: {"var": "temp", "polygon": [[i1,j1], [i2,j2], ...], "layer": -1}
    Cells whose center is inside the polygon are averaged at each timestep.
    GETM sigma 约定：0=底层, -1=表层；若变量为 2D（无 sigma），layer 被忽略。
    """
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    if _output_locked():
        return jsonify({"error": "模型运行中，输出文件正在写入，暂不能读取"}), 409
    data = request.json or {}
    var_name = data.get("var", "temp")
    polygon = data.get("polygon", [])
    layer = data.get("layer", -1)
    if len(polygon) < 3:
        return jsonify({"error": "polygon 至少需要 3 个点"}), 400
    files = find_output_files(active_case_path)
    nc_path = files["3d"] or files["2d"]
    if not nc_path:
        return jsonify({"error": "没有输出文件"}), 404

    with nc_open(nc_path) as ds:
        if var_name not in ds.variables:
            return jsonify({"error": f"变量 {var_name} 不存在"}), 404
        var = ds.variables[var_name]
        is_3d = var.ndim == 4
        dims = list(var.dimensions)
        time_dim = next((d for d in dims if "time" in d.lower()), dims[0])
        ntime = len(ds.dimensions[time_dim]) if time_dim in ds.dimensions else 0
        if ntime == 0:
            return jsonify({"error": "输出文件没有任何时间记录（上次运行可能异常中断或 sync_interval=0）"}), 404
        # 网格形状直接取维度长度，不读数据
        if is_3d:
            ny, nx = len(ds.dimensions[dims[2]]), len(ds.dimensions[dims[3]])
        else:
            ny, nx = len(ds.dimensions[dims[1]]), len(ds.dimensions[dims[2]])
        mask = np.zeros((ny, nx), dtype=bool)
        poly = [(float(p[0]), float(p[1])) for p in polygon]
        for j in range(ny):
            for i in range(nx):
                if _point_in_polygon(i + 0.5, j + 0.5, poly):
                    mask[j, i] = True
        if not mask.any():
            return jsonify({"error": "polygon 不覆盖任何单元格"}), 400
        times = []
        if time_dim in ds.variables:
            tvals = ds.variables[time_dim][:]
            tunits = getattr(ds.variables[time_dim], "units", "")
            try:
                times = nc.num2date(tvals, tunits).tolist()
                times = [t.strftime("%Y-%m-%d %H:%M:%S") if hasattr(t, "strftime") else str(t) for t in times]
            except Exception:
                times = [float(t) for t in tvals]
        else:
            times = list(range(ntime))
        # GETM sigma: 0=底, -1=面。只读多边形包围盒的 (nt, h, w) 切片。
        rows = np.where(mask.any(axis=1))[0]
        cols = np.where(mask.any(axis=0))[0]
        j1, j2, i1, i2 = int(rows[0]), int(rows[-1]) + 1, int(cols[0]), int(cols[-1]) + 1
        local = mask[j1:j2, i1:i2]

        def _fill(a):
            return a.filled(np.nan) if isinstance(a, np.ma.MaskedArray) else np.asarray(a, dtype=float)

        lev = None
        if is_3d:
            nlev = var.shape[1]
            lev = layer if layer >= 0 else nlev + layer
            lev = max(0, min(nlev - 1, lev))
            sub = _fill(var[:, lev, j1:j2, i1:i2])
            series = [float(np.nanmean(sub[t][local])) if np.isfinite(sub[t][local]).any() else None for t in range(ntime)]
        else:
            sub = _fill(var[:, j1:j2, i1:i2])
            series = [float(np.nanmean(sub[t][local])) if np.isfinite(sub[t][local]).any() else None for t in range(ntime)]
        return jsonify({
            "times": times,
            "values": series,
            "var_name": var_name,
            "long_name": getattr(var, "long_name", var_name),
            "units": getattr(var, "units", ""),
            "n_cells": int(mask.sum()),
            "layer": int(lev) if is_3d else None,
        })

@app.route("/api/results/timeseries_cell")
def results_timeseries_cell():
    """Single-cell time series. Query: ?var=temp&i=10&j=5&layer=-1"""
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    if _output_locked():
        return jsonify({"error": "模型运行中，输出文件正在写入，暂不能读取"}), 409
    var_name = request.args.get("var", "temp")
    try:
        i = int(request.args.get("i", 0))
        j = int(request.args.get("j", 0))
        layer = int(request.args.get("layer", -1))
    except ValueError:
        return jsonify({"error": "i/j/layer 必须是整数"}), 400
    files = find_output_files(active_case_path)
    nc_path = files["3d"] or files["2d"]
    if not nc_path:
        return jsonify({"error": "没有输出文件"}), 404

    with nc_open(nc_path) as ds:
        if var_name not in ds.variables:
            return jsonify({"error": f"变量 {var_name} 不存在"}), 404
        var = ds.variables[var_name]
        is_3d = var.ndim == 4
        dims = list(var.dimensions)
        time_dim = next((d for d in dims if "time" in d.lower()), dims[0])
        ntime = len(ds.dimensions[time_dim]) if time_dim in ds.dimensions else 0
        if ntime == 0:
            return jsonify({"error": "输出文件没有任何时间记录（上次运行可能异常中断或 sync_interval=0）"}), 404
        if is_3d:
            ny, nx = len(ds.dimensions[dims[2]]), len(ds.dimensions[dims[3]])
        else:
            ny, nx = len(ds.dimensions[dims[1]]), len(ds.dimensions[dims[2]])
        if i < 0 or i >= nx or j < 0 or j >= ny:
            return jsonify({"error": f"i/j 越界：i∈[0,{nx-1}], j∈[0,{ny-1}]"}), 400
        times = []
        if time_dim in ds.variables:
            tvals = ds.variables[time_dim][:]
            tunits = getattr(ds.variables[time_dim], "units", "")
            try:
                times = nc.num2date(tvals, tunits).tolist()
                times = [t.strftime("%Y-%m-%d %H:%M:%S") if hasattr(t, "strftime") else str(t) for t in times]
            except Exception:
                times = [float(t) for t in tvals]
        else:
            times = list(range(ntime))

        def _fill(a):
            return a.filled(np.nan) if isinstance(a, np.ma.MaskedArray) else np.asarray(a, dtype=float)

        lev = None
        if is_3d:
            nlev = var.shape[1]
            lev = layer if layer >= 0 else nlev + layer
            lev = max(0, min(nlev - 1, lev))
            col = _fill(var[:, lev, j, i])
            series = [float(v) if np.isfinite(v) else None for v in col]
        else:
            col = _fill(var[:, j, i])
            series = [float(v) if np.isfinite(v) else None for v in col]
        return jsonify({
            "times": times,
            "values": series,
            "var_name": var_name,
            "long_name": getattr(var, "long_name", var_name),
            "units": getattr(var, "units", ""),
            "i": i, "j": j,
            "layer": int(lev) if is_3d else None,
            "lon": float(ds.variables["lonc"][j, i]) if "lonc" in ds.variables else None,
            "lat": float(ds.variables["latc"][j, i]) if "latc" in ds.variables else None,
        })


# ═══════════════════════════════════════════════════════════════════════
# Pre-processing: shapefile upload → grid → bathymetry.nc
# ═══════════════════════════════════════════════════════════════════════
# All endpoints under /api/preprocess/ let a user build a new lake case from
# scratch: upload a polygon lake boundary and a depth shapefile (point or
# polygon geometry), generate a Cartesian grid sized by the user, interpolate
# depth onto water cells, and finally write bathymetry.nc into a new case
# directory. pyshp handles shapefile I/O; scipy.griddata does the depth
# interpolation; the netCDF layout mirrors preprocessor/generate_bathymetry.py.

import math as _math

_SHP_TEMP_DIR = APP_DIR / "_shp_uploads"
_SHP_TEMP_DIR.mkdir(exist_ok=True)


def _save_uploaded_shapefile(file_objs, prefix):
    """Persist uploaded shapefile components (.shp/.shx/.dbf/.prj) to a
    temporary folder so pyshp can read them as a set.

    Returns (dir_path, base_name_without_ext, prj_text_or_None,
    missing_components list). A shapefile is only complete when .shp/.shx/.dbf
    are all present; without .dbf pyshp cannot read any attribute (depth!).
    """
    work_dir = _SHP_TEMP_DIR / f"{prefix}_{uuid.uuid4().hex[:8]}"
    work_dir.mkdir(exist_ok=True)
    saved_names = []
    prj_text = None
    for f in file_objs:
        if not f.filename:
            continue
        lower = f.filename.lower()
        if not (lower.endswith(".shp") or lower.endswith(".shx")
                or lower.endswith(".dbf") or lower.endswith(".prj")):
            continue
        target = work_dir / Path(f.filename).name
        f.save(str(target))
        saved_names.append(target.name)
        if lower.endswith(".prj"):
            try:
                prj_text = target.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                prj_text = None
    shp_files = [n for n in saved_names if n.lower().endswith(".shp")]
    if not shp_files:
        raise ValueError("缺少 .shp 主文件")
    missing = []
    for ext in (".shx", ".dbf"):
        if not any(n.lower().endswith(ext) for n in saved_names):
            missing.append(ext)
    return str(work_dir), shp_files[0], prj_text, missing


def _parse_prj_crs(prj_text):
    """Coarse classification of a .prj WKT string.

    Returns dict with keys: crs_type ('utm' | 'geographic' | 'unknown'),
    utm_zone (int or None), central_meridian (float or None).
    """
    if not prj_text:
        return {"crs_type": "unknown", "utm_zone": None, "central_meridian": None}
    t = prj_text
    is_utm = ("UTM" in t) or ("Transverse_Mercator" in t) or ("Gauss_Kruger" in t)
    is_geog = (("GEOGCS" in t) or ("GEOGCRS" in t)) and "PROJCS" not in t and "PROJCRS" not in t
    is_projcs = ("PROJCS" in t) or ("PROJCRS" in t)
    cm = None
    m = re.search(r"central_meridian[^\d-]*(-?\d+\.?\d*)", t)
    if m:
        try:
            cm = float(m.group(1))
        except ValueError:
            cm = None
    zone = None
    if cm is not None:
        # UTM zone from central meridian: zone = (cm + 183) / 6
        zone = int(round((cm + 183.0) / 6.0))
    if is_utm:
        return {"crs_type": "utm", "utm_zone": zone, "central_meridian": cm, "wkt": t}
    if is_geog:
        return {"crs_type": "geographic", "utm_zone": None, "central_meridian": cm, "wkt": t}
    if is_projcs:
        # Projected CRS that is not Transverse Mercator: treat coordinates as
        # already metric and pass them through untouched.
        return {"crs_type": "projected", "utm_zone": None, "central_meridian": cm, "wkt": t}
    return {"crs_type": "unknown", "utm_zone": zone, "central_meridian": cm}


def _utm_zone_from_lon(lon):
    """Return UTM zone number (1-60) for a given longitude (degrees east)."""
    return int(_math.floor((lon + 180.0) / 6.0)) + 1


def _lonlat_to_utm_xy(lon, lat, zone=None):
    """Simplified lon/lat → UTM (x,y) in metres.

    Uses the local Transverse Mercator approximation around the zone central
    meridian. Accuracy is ~1 m per degree of latitude, sufficient for lake
    grids (cells ≥ 10 m). If zone is None, it is derived from lon.
    """
    if zone is None:
        zone = _utm_zone_from_lon(lon)
    cm = (zone - 1) * 6.0 - 180.0 + 3.0  # central meridian of zone
    cos_lat = _math.cos(_math.radians(lat))
    x = 500000.0 + (lon - cm) * 111320.0 * cos_lat
    y = lat * 110574.0  # approximate metres from equator
    return x, y


def _coords_look_geographic(coords):
    """True when all coords fall inside lon/lat ranges (|x|<=360, |y|<=90)."""
    return all(abs(c[0]) <= 360.0 and abs(c[1]) <= 90.0 for c in coords)


def _convert_boundary_to_utm(coords, crs_info):
    """Return UTM-space copy of coords. If already UTM, pass through."""
    if crs_info["crs_type"] in ("utm", "projected"):
        # Metric coordinates (declared projection or values far outside
        # lon/lat ranges) — use as-is, do NOT run the lon/lat conversion.
        return coords, crs_info
    if crs_info["crs_type"] == "unknown" and not _coords_look_geographic(coords):
        new_info = dict(crs_info)
        new_info["crs_type"] = "projected"
        return coords, new_info
    # geographic or unknown-but-plausibly-degrees → derive zone from centroid lon
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    lon0 = sum(xs) / len(xs)
    lat0 = sum(ys) / len(ys)
    zone = crs_info.get("utm_zone") or _utm_zone_from_lon(lon0)
    out = [_lonlat_to_utm_xy(c[0], c[1], zone) for c in coords]
    new_info = dict(crs_info)
    new_info["crs_type"] = "utm"
    new_info["utm_zone"] = zone
    new_info["central_meridian"] = (zone - 1) * 6.0 - 180.0 + 3.0
    new_info["origin_lat"] = lat0
    new_info["origin_lon"] = lon0
    return out, new_info


@app.route("/api/preprocess/help")
def preprocess_help():
    """Static guidance on expected shapefile formats."""
    return jsonify({
        "boundary": {
            "geometry": "Polygon",
            "required_files": [".shp", ".shx", ".dbf"],
            "optional_files": [".prj"],
            "description": "湖泊外边界多边形，第一个 polygon 的外环即湖岸线",
            "crs": "推荐 UTM（带 .prj）；WGS84 经纬度也支持，后端自动转 UTM",
        },
        "bathymetry_point": {
            "geometry": "Point",
            "required_fields": "任意一个数值字段表示水深(m)，例如 depth / ELEV / Z",
            "description": "散点测深，每个点带 (x, y, depth)。后端用 scipy.griddata 插值到网格",
        },
        "bathymetry_polygon": {
            "geometry": "Polygon",
            "required_fields": "每个多边形需带一个数值字段表示该区域水深(m)",
            "description": "等深区多边形，每个多边形 depth 属性即为该格水深。网格中心落在哪个多边形就取该 depth",
        },
        "depth_sign": "正值=水深(m)。陆地/无效水域请填 -9999 或不包含",
        "crs_must_match": "边界与水深 shapefile 必须使用同一坐标系",
    })


@app.route("/api/preprocess/case/create", methods=["POST"])
def preprocess_case_create():
    """Create a new empty case directory and load it as the active case."""
    data = request.json or {}
    case_name = (data.get("case_name") or "").strip()
    if not case_name:
        return jsonify({"error": "案例名不能为空"}), 400
    if not re.match(r"^[A-Za-z0-9_\-\u4e00-\u9fa5 ]+$", case_name):
        return jsonify({"error": "案例名仅允许字母、数字、下划线、空格、中文"}), 400
    case_path = CASE_DIR / case_name
    if case_path.exists():
        return jsonify({"error": f"案例 {case_name} 已存在"}), 400
    case_path.mkdir(parents=True)
    _ensure_case_dirs(case_path)
    # Reuse the standard load_case logic by issuing an internal call shape
    global active_case, active_case_path, cached_getm_config, cached_fabm_info
    active_case = case_name
    active_case_path = case_path
    cached_getm_config = None
    cached_fabm_info = None
    return jsonify({
        "success": True,
        "case_name": case_name,
        "case_path": str(case_path),
    })


@app.route("/api/preprocess/boundary/upload", methods=["POST"])
def preprocess_boundary_upload():
    """Upload a polygon shapefile defining the lake outline.

    Multipart form: files = [.shp, .shx, .dbf, (.prj)]
    Returns cached boundary_id + bbox + crs info + preview coords.
    """
    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "未上传文件"}), 400
    try:
        work_dir, shp_name, prj_text, missing = _save_uploaded_shapefile(files, "boundary")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    warnings = []
    if missing:
        warnings.append("shapefile 组件不完整（缺少 " + "、".join(missing) +
                        "）。请回到文件夹中把 .shp/.shx/.dbf/.prj 全部选中后一起上传。")
    crs_info = _parse_prj_crs(prj_text)
    try:
        reader = shapefile.Reader(os.path.join(work_dir, shp_name))
    except Exception as e:
        return jsonify({"error": f"读取 shapefile 失败: {e}"}), 500
    if reader.shapeType != shapefile.POLYGON and reader.shapeType != shapefile.POLYGONZ:
        return jsonify({"error": f"边界 shapefile 必须是 Polygon，当前 shapeType={reader.shapeType}"}), 400
    # Collect the outer ring (first part) of EVERY polygon feature, so that
    # multi-part lakes (e.g. 滇池外海 + 草海) are kept in full. Inner rings
    # (holes) start at parts[1] and are skipped.
    rings = []
    for shp in reader.shapes():
        pts = shp.points
        parts = list(shp.parts) + [len(pts)]
        if not pts or not parts:
            continue
        outer = pts[parts[0]:parts[1]]
        if len(outer) >= 4:
            rings.append([(p[0], p[1]) for p in outer])
    if not rings:
        return jsonify({"error": "shapefile 中没有有效 polygon"}), 400
    # 用户显式声明的源坐标系：先把所有环重投影到 WGS84 经纬度，
    # 再走下方原有 lon/lat→UTM 管线，使边界进入标准 UTM 框架。
    crs_preset = (request.form.get("crs_preset") or "auto").strip()
    crs_epsg = (request.form.get("crs_epsg") or "").strip()
    conversion_note = None
    if crs_preset not in ("", "auto"):
        src_crs = crs_utils.build_crs(crs_preset, crs_epsg)
        if src_crs is None:
            return jsonify({"error": "无法识别所选坐标系（自定义 EPSG 代码无效）"}), 400
        tr = crs_utils.make_transformer(src_crs, crs_utils.WGS84)
        try:
            rings = [[tr.transform(p[0], p[1]) for p in ring] for ring in rings]
        except Exception as e:
            return jsonify({"error": f"坐标转换失败: {e}（请确认所选坐标系与数据匹配）"}), 400
        crs_info = {"crs_type": "geographic", "utm_zone": None, "central_meridian": None}
        conversion_note = f"已从 {crs_utils.preset_label(crs_preset, crs_epsg)} 转换到标准 UTM"
    # Convert every ring to UTM/metric space
    rings_utm = []
    crs_info2 = crs_info
    for ring in rings:
        conv, crs_info2 = _convert_boundary_to_utm(ring, crs_info)
        rings_utm.append(conv)
    all_pts = [pt for ring in rings_utm for pt in ring]
    xs = [c[0] for c in all_pts]
    ys = [c[1] for c in all_pts]
    bbox = [min(xs), min(ys), max(xs), max(ys)]
    # Preview: subsample each ring (max ~400 pts per ring)
    previews = []
    for ring in rings_utm:
        step = max(1, len(ring) // 400)
        previews.append(ring[::step])
    largest = max(rings_utm, key=len)
    boundary_id = _pp_cache_id("bnd")
    _preprocess_cache["boundary"][boundary_id] = {
        "coords": largest,          # largest ring (kept for compatibility)
        "rings": rings_utm,         # ALL outer rings for mask generation
        "bbox": bbox,
        "crs_info": crs_info2,
        "orig_crs_type": crs_info["crs_type"],
    }
    return jsonify({
        "boundary_id": boundary_id,
        "n_points": len(all_pts),
        "n_polygons": len(rings_utm),
        "bbox": bbox,
        "crs_type": crs_info2["crs_type"],
        "utm_zone": crs_info2.get("utm_zone"),
        "coords_preview": previews[0] if len(previews) == 1 else previews,
        "rings_preview": previews,
        "orig_crs_type": crs_info["crs_type"],
        "warnings": warnings,
        "converted": conversion_note is not None,
        "conversion": conversion_note,
    })


@app.route("/api/preprocess/bathymetry/upload", methods=["POST"])
def preprocess_bathymetry_upload():
    """Upload a point or polygon shapefile with a depth attribute.

    Multipart form:
      files = [.shp, .shx, .dbf, (.prj)]
      depth_field = field name in DBF holding the depth value (m)
    """
    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "未上传文件"}), 400
    depth_field = (request.form.get("depth_field") or "").strip()
    try:
        work_dir, shp_name, prj_text, missing = _save_uploaded_shapefile(files, "bathy")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    if ".dbf" in missing:
        return jsonify({
            "error": "缺少 .dbf 属性表文件——水深数值存放在 .dbf 中，仅上传 .shp 无法读取。"
                     "请在文件夹中把 .shp/.shx/.dbf/.prj 全部选中后一起上传。",
        }), 400
    crs_info = _parse_prj_crs(prj_text)
    try:
        reader = shapefile.Reader(os.path.join(work_dir, shp_name))
    except Exception as e:
        return jsonify({"error": f"读取 shapefile 失败: {e}"}), 500
    try:
        field_names = [f[0] for f in reader.fields[1:]]  # first is deletion flag
    except Exception as e:
        return jsonify({"error": f"读取属性表 (.dbf) 失败: {e}"}), 400
    if depth_field and depth_field not in field_names:
        return jsonify({
            "error": f"字段 {depth_field} 不存在，可用字段: {field_names}",
            "fields": field_names,
        }), 400
    if not depth_field:
        # Heuristic: pick first numeric-looking field
        candidates = [n for n in field_names if n.lower() in
                      ("depth", "elev", "z", "h", "height", "水深", "高程", "深度")]
        if candidates:
            depth_field = candidates[0]
        elif field_names:
            depth_field = field_names[0]
        else:
            return jsonify({"error": "shapefile 没有任何属性字段"}), 400
    is_point = reader.shapeType in (shapefile.POINT, shapefile.POINTZ, shapefile.POINTM)
    is_poly = reader.shapeType in (shapefile.POLYGON, shapefile.POLYGONZ, shapefile.POLYGONM)
    if not (is_point or is_poly):
        return jsonify({"error": f"水深 shapefile 必须是 Point 或 Polygon，当前 shapeType={reader.shapeType}"}), 400
    # Determine reference CRS — prefer boundary if already cached, else use own
    boundary_cache = next(iter(_preprocess_cache["boundary"].values()), None)
    if boundary_cache:
        target_crs = boundary_cache["crs_info"]
    else:
        target_crs = crs_info
    # If the CRS is unknown, classify by the actual coordinate values:
    # metric-looking coordinates (e.g. |x|>360) must NOT be run through the
    # lon/lat→UTM conversion.
    sample = None
    if is_point:
        for shp in reader.shapes():
            if shp.points:
                sample = [(shp.points[0][0], shp.points[0][1])]
                break
    else:
        for shp in reader.shapes():
            if shp.points:
                sample = [(p[0], p[1]) for p in shp.points[:20]]
                break
    if target_crs.get("crs_type") == "unknown" and sample and not _coords_look_geographic(sample):
        target_crs = dict(target_crs)
        target_crs["crs_type"] = "projected"
    # ── 坐标系转换/对齐 ──
    #  源 CRS：用户显式声明(crs_preset) > 数据自带 .prj > 经纬度特征自动识别。
    #  目标框架优先级：
    #   a) 边界带 .prj（标准 CRS，如 Albers/UTM）→ pyproj 精确重投影
    #   b) 边界为标准 UTM → pyproj 精确重投影到该 UTM 带
    #   c) 边界为地方/未知投影框架 → 按包围盒中心平移拟合
    #   d) 尚未上传边界 → 转换到数据自身所在 UTM 带
    #  auto（未声明）时：若数据范围与边界完全不重叠且能确定源 CRS，
    #  自动转换——避免"不同坐标系未转换→最近邻回退→全场常数水深"的陷阱。
    crs_preset = (request.form.get("crs_preset") or "auto").strip()
    crs_epsg = (request.form.get("crs_epsg") or "").strip()
    is_auto = crs_preset in ("", "auto")
    align_mode = None       # "reproject" | "translate"
    convert_xy = None
    conversion_note = None
    final_crs = target_crs
    # 转换前的原始数据范围（用于不重叠检测与平移拟合）
    raw_pts = []
    for shp in reader.shapes():
        if is_point:
            if shp.points:
                raw_pts.append(shp.points[0])
        else:
            raw_pts.extend(shp.points)
    raw_bbox = None
    if raw_pts:
        rxs = [p[0] for p in raw_pts]
        rys = [p[1] for p in raw_pts]
        raw_bbox = (min(rxs), min(rys), max(rxs), max(rys))
    # 构造源 CRS
    src_crs = None
    src_label = None
    if not is_auto:
        src_crs = crs_utils.build_crs(crs_preset, crs_epsg)
        if src_crs is None:
            return jsonify({"error": "无法识别所选坐标系（自定义 EPSG 代码无效）"}), 400
        src_label = crs_utils.preset_label(crs_preset, crs_epsg)
    elif crs_info.get("wkt"):
        src_crs = crs_utils.crs_from_wkt(crs_info["wkt"])
        src_label = "数据 .prj 声明的坐标系"
    elif sample and _coords_look_geographic(sample):
        src_crs = crs_utils.WGS84
        src_label = "自动识别的经纬度坐标"
    # auto 模式：范围与边界完全不重叠 → 判定坐标系不一致，自动转换
    auto_mismatch = False
    if (is_auto and boundary_cache and src_crs is not None and raw_bbox is not None):
        cb = boundary_cache["bbox"]
        if (raw_bbox[2] < cb[0] or raw_bbox[0] > cb[2]
                or raw_bbox[3] < cb[1] or raw_bbox[1] > cb[3]):
            auto_mismatch = True
    if src_crs is not None and (not is_auto or auto_mismatch):
        bnd_crs = boundary_cache["crs_info"] if boundary_cache else None
        bnd_wkt = (bnd_crs or {}).get("wkt")
        auto_prefix = "检测到高程与边界坐标系不一致，已自动" if auto_mismatch else "已"
        if boundary_cache and bnd_wkt:
            dst_crs = crs_utils.crs_from_wkt(bnd_wkt)
            if dst_crs is not None:
                tr = crs_utils.make_transformer(src_crs, dst_crs)
                convert_xy = tr.transform
                align_mode = "reproject"
                final_crs = dict(bnd_crs)
                conversion_note = f"{auto_prefix}从 {src_label} 精确重投影到边界坐标系"
        if convert_xy is None and boundary_cache and bnd_crs.get("crs_type") == "utm":
            zone = bnd_crs["utm_zone"]
            tr = crs_utils.make_transformer(src_crs, crs_utils.utm_crs(zone))
            convert_xy = tr.transform
            align_mode = "reproject"
            final_crs = {"crs_type": "utm", "utm_zone": zone,
                         "central_meridian": (zone - 1) * 6.0 - 180.0 + 3.0}
            conversion_note = f"{auto_prefix}从 {src_label} 重投影到边界坐标系 (UTM {zone}N)"
        if convert_xy is None and boundary_cache:
            if raw_bbox is None:
                return jsonify({"error": "shapefile 中没有坐标点"}), 400
            off_x, off_y = crs_utils.fit_translation_offset(
                raw_bbox, boundary_cache["bbox"])
            convert_xy = lambda x, y: (x + off_x, y + off_y)
            align_mode = "translate"
            final_crs = {"crs_type": "projected", "utm_zone": None,
                         "central_meridian": None}
            conversion_note = (f"{auto_prefix}按包围盒中心平移对齐到边界地方坐标系 "
                               f"(Δx={off_x:.0f}m, Δy={off_y:.0f}m)")
        if convert_xy is None and not boundary_cache:
            if not sample:
                return jsonify({"error": "shapefile 中没有坐标点"}), 400
            tr_ll = crs_utils.make_transformer(src_crs, crs_utils.WGS84)
            lon0, lat0 = tr_ll.transform(sample[0][0], sample[0][1])
            zone = _utm_zone_from_lon(lon0)
            tr = crs_utils.make_transformer(src_crs, crs_utils.utm_crs(zone))
            convert_xy = tr.transform
            align_mode = "reproject"
            final_crs = {"crs_type": "utm", "utm_zone": zone,
                         "central_meridian": (zone - 1) * 6.0 - 180.0 + 3.0}
            conversion_note = f"已从 {src_label} 转换到 UTM {zone}N"
    points = []
    polygons = []
    depths = []
    records_iter = reader.records()
    shapes_iter = reader.shapes()
    for shp, rec in zip(shapes_iter, records_iter):
        try:
            d = float(rec[depth_field])
        except (TypeError, ValueError):
            continue
        if is_point:
            pts = shp.points
            if not pts:
                continue
            x, y = pts[0]
            if convert_xy is not None:
                ux, uy = convert_xy(x, y)
            elif target_crs["crs_type"] == "geographic":
                ux, uy = _lonlat_to_utm_xy(x, y, target_crs.get("utm_zone"))
            else:
                ux, uy = x, y
            points.append((ux, uy))
            depths.append(d)
        else:  # polygon
            pts = shp.points
            if not pts:
                continue
            if convert_xy is not None:
                utm_pts = [convert_xy(p[0], p[1]) for p in pts]
            elif target_crs["crs_type"] == "geographic":
                utm_pts = [_lonlat_to_utm_xy(p[0], p[1], target_crs.get("utm_zone")) for p in pts]
            else:
                utm_pts = [(p[0], p[1]) for p in pts]
            polygons.append(utm_pts)
            depths.append(d)
    if not depths:
        return jsonify({"error": "没有有效的水深数据行（请检查 depth_field 是否为数值）"}), 400
    # Warn when the bathy extent lies completely outside the boundary extent AND
    # no conversion was possible — almost always means the two shapefiles use
    # different CRS and neither has a usable .prj / declaration.
    warnings = []
    if boundary_cache and convert_xy is None:
        if points:
            bx = [p[0] for p in points]; by = [p[1] for p in points]
        else:
            flat = [pt for poly in polygons for pt in poly]
            bx = [p[0] for p in flat]; by = [p[1] for p in flat]
        if bx and by:
            bb = (min(bx), min(by), max(bx), max(by))
            cb = boundary_cache["bbox"]
            if bb[2] < cb[0] or bb[0] > cb[2] or bb[3] < cb[1] or bb[1] > cb[3]:
                warnings.append(
                    "高程数据范围与湖泊边界完全不重叠——两者坐标系不一致且无法自动转换"
                    "（该高程文件缺少 .prj）。请将上方'数据坐标系'选择为该文件的真实坐标系"
                    "后重新上传，系统将自动转换对齐")
    # 转换对齐质量：采样点落入边界多边形的比例
    inside_ratio = None
    if align_mode is not None and boundary_cache:
        rings_b = boundary_cache.get("rings") or [boundary_cache["coords"]]
        probe = points[:400] if is_point else \
            [pt for poly in polygons[:25] for pt in poly[:20]]
        if probe:
            n_in = sum(1 for px, py in probe
                       if any(_point_in_polygon(px, py, r) for r in rings_b))
            inside_ratio = n_in / len(probe)
    bathy_id = _pp_cache_id("bthy")
    geom_type = "point" if is_point else "polygon"
    _preprocess_cache["bathymetry"][bathy_id] = {
        "geom_type": geom_type,
        "points": points,
        "polygons": polygons,
        "depths": depths,
        "depth_field": depth_field,
        "crs_info": final_crs,
    }
    return jsonify({
        "bathy_id": bathy_id,
        "geom_type": geom_type,
        "n_features": len(depths),
        "depth_range": [float(min(depths)), float(max(depths))],
        "fields": field_names,
        "depth_field": depth_field,
        "crs_type": final_crs["crs_type"],
        "warnings": warnings,
        "converted": align_mode is not None,
        "conversion": conversion_note,
        "inside_ratio": inside_ratio,
        "preview_points": points[:200] if is_point else [],
        "preview_polygons": polygons[:50] if not is_point else [],
        "preview_depths": depths[:200] if is_point else depths[:50],
    })


@app.route("/api/preprocess/bathymetry/upload_xyz", methods=["POST"])
def preprocess_bathymetry_upload_xyz():
    """ASCII bathymetry import: x,y,depth (or lon,lat,depth) as CSV/TAB/space text.

    Why this exists: GOTM (1D, QWET) reads plain-text inputs such as
    hypsograph.dat / meteo_file.dat, so users reasonably expect .dat to work
    here too. GETM's own topo reader only implements the NetCDF branch —
    `case (ASCII) call getm_error(... "not yet supported")` in
    src/getm/src/input/read_topo_file.F90 — so bathymetry.nc is unavoidable at
    the model boundary. The GUI therefore accepts plain text and produces that
    NetCDF for you.
    """
    f = request.files.get("file")
    if f is None:
        return jsonify({"error": "缺少文件"}), 400
    raw = f.read().decode("utf-8", errors="replace")
    lines = [ln.strip() for ln in raw.splitlines()]
    lines = [ln for ln in lines if ln and not ln.startswith(("#", "!", "//"))]
    if not lines:
        return jsonify({"error": "文件为空或全是注释"}), 400

    def split_row(line):
        if "\t" in line:
            parts = line.split("\t")
        elif "," in line:
            parts = line.split(",")
        elif ";" in line:
            parts = line.split(";")
        else:
            parts = line.split()
        return [p.strip() for p in parts]

    cells = [split_row(ln) for ln in lines]
    idx = {}
    if all(_to_float(c) is None for c in cells[0]):  # header row
        for i, h in enumerate(cells[0]):
            hl = h.lower().strip()
            if hl in ("x", "lon", "lng", "long", "longitude", "经度", "东经"):
                idx["x"] = i
            elif hl in ("y", "lat", "latitude", "纬度", "北纬"):
                idx["y"] = i
            elif hl in ("depth", "z", "h", "depth_m", "水深", "深度", "elev", "elevation"):
                idx["d"] = i
        cells = cells[1:]
    idx.setdefault("x", 0)
    idx.setdefault("y", 1)
    idx.setdefault("d", 2)
    if len(set(idx.values())) < 3:
        return jsonify({"error": "无法识别 X/Y/深度 三列，请检查表头或列顺序"}), 400

    points, depths, bad = [], [], 0
    for c in cells:
        if len(c) <= max(idx.values()):
            bad += 1
            continue
        x, y, d = _to_float(c[idx["x"]]), _to_float(c[idx["y"]]), _to_float(c[idx["d"]])
        if x is None or y is None or d is None:
            bad += 1
            continue
        points.append([x, y])
        depths.append(d)
    if len(points) < 3:
        return jsonify({"error": f"有效数据点不足 3 个（解析失败 {bad} 行）"}), 400

    # Sign convention: bathymetry is positive downward. Data given as elevation
    # (all negative, e.g. -12.4 m) is flipped automatically.
    if max(depths) <= 0:
        depths = [-v for v in depths]
        sign_note = "检测到全部为负值，已按“高程（向上为正）”自动取反为水深"
    else:
        sign_note = None

    crs_mode = (request.form.get("crs") or "auto").strip().lower()
    boundary_cache = next(iter(_preprocess_cache["boundary"].values()), None)
    target_crs = boundary_cache["crs_info"] if boundary_cache else \
        {"crs_type": "unknown", "utm_zone": None}
    is_geo = _coords_look_geographic(points) if crs_mode == "auto" else (crs_mode == "geographic")
    conversion_note = None
    if is_geo:
        lon0 = sum(p[0] for p in points) / len(points)
        lat0 = sum(p[1] for p in points) / len(points)
        zone = target_crs.get("utm_zone") or _utm_zone_from_lon(lon0)
        points = [list(_lonlat_to_utm_xy(p[0], p[1], zone)) for p in points]
        final_crs = {"crs_type": "utm", "utm_zone": zone,
                     "central_meridian": (zone - 1) * 6.0 - 180.0 + 3.0,
                     "origin_lat": lat0, "origin_lon": lon0}
        conversion_note = f"经纬度 → UTM {zone} 带（自动，中心 {lon0:.3f}°E {lat0:.3f}°N）"
    else:
        final_crs = dict(target_crs)
        if final_crs.get("crs_type") == "unknown":
            final_crs["crs_type"] = "projected"

    bathy_id = _pp_cache_id("bthy")
    _preprocess_cache["bathymetry"][bathy_id] = {
        "geom_type": "point",
        "points": points,
        "polygons": [],
        "depths": depths,
        "depth_field": "depth",
        "crs_info": final_crs,
        "source": "xyz",
    }
    warnings = [w for w in (sign_note, conversion_note) if w]
    return jsonify({
        "bathy_id": bathy_id,
        "geom_type": "point",
        "n_features": len(depths),
        "depth_range": [float(min(depths)), float(max(depths))],
        "fields": [],
        "depth_field": "depth",
        "crs_type": final_crs["crs_type"],
        "warnings": warnings,
        "converted": is_geo,
        "conversion": conversion_note,
        "n_bad_rows": bad,
        "preview_points": points[:200],
        "preview_polygons": [],
        "preview_depths": depths[:200],
    })


@app.route("/api/preprocess/hypsograph", methods=["POST"])
def preprocess_hypsograph():
    """Build a circular lake (boundary + depth points) from a depth-area curve.

    Input = QWET/GOTM `hypsograph.dat` layout: one optional header line
    (`n_levels n_cols`), then rows of `z  area`, where z is the height above
    the deepest point and area (m2) is the lake area at that height.
    Optional form fields: center_lon, center_lat (geographic anchor).
    """
    f = request.files.get("file")
    if f is None:
        return jsonify({"error": "缺少文件"}), 400
    raw = f.read().decode("utf-8", errors="replace")
    rows = []
    for ln in raw.splitlines():
        ln = ln.strip()
        if not ln or ln.startswith(("#", "!", "//")):
            continue
        parts = ln.replace("\t", " ").replace(",", " ").split()
        vals = [_to_float(p) for p in parts]
        vals = [v for v in vals if v is not None]
        if len(vals) >= 2:
            rows.append((vals[0], vals[1]))
    if len(rows) >= 2 and float(rows[0][0]).is_integer() and \
            int(rows[0][0]) == len(rows) - 1 and rows[0][0] > 1:
        rows = rows[1:]  # `n_levels n_cols` header
    if len(rows) < 2:
        return jsonify({"error": "深度-面积曲线至少需要 2 行有效数据"}), 400

    zs = [r[0] for r in rows]
    areas = [r[1] for r in rows]
    z_max = max(zs)
    # Convert (height above bottom, area at that height) → (depth, radius)
    rings = []
    for z, a in sorted(zip(zs, areas)):
        depth = z_max - z
        radius = _math.sqrt(max(a, 0.0) / _math.pi)
        rings.append((radius, depth))
    surface_area = max(areas)
    lake_radius = _math.sqrt(surface_area / _math.pi)
    max_depth = z_max

    # Geographic anchor (optional)
    clon, clat = _to_float(request.form.get("center_lon")), _to_float(request.form.get("center_lat"))
    warnings = []
    if clon is not None and clat is not None:
        zone = _utm_zone_from_lon(clon)
        cx, cy = _lonlat_to_utm_xy(clon, clat, zone)
        crs_info = {"crs_type": "utm", "utm_zone": zone,
                    "central_meridian": (zone - 1) * 6.0 - 180.0 + 3.0,
                    "origin_lat": clat, "origin_lon": clon}
    else:
        cx, cy = 0.0, 0.0
        crs_info = {"crs_type": "projected", "utm_zone": None}
        warnings.append("未指定中心经纬度：生成的湖泊位于局部平面坐标，"
                        "地图视图无法定位（可在前处理里补填中心经纬度后重新生成）")

    n_ang = 48
    pts, deps = [[cx, cy]], [max_depth]
    for radius, depth in rings:
        for k in range(n_ang):
            ang = 2.0 * _math.pi * k / n_ang
            pts.append([cx + radius * _math.cos(ang), cy + radius * _math.sin(ang)])
            deps.append(depth)
    # Shoreline ring (depth 0) just outside the lake, keeps interpolation sane
    for k in range(n_ang):
        ang = 2.0 * _math.pi * k / n_ang
        pts.append([cx + lake_radius * 1.05 * _math.cos(ang),
                    cy + lake_radius * 1.05 * _math.sin(ang)])
        deps.append(0.0)

    # Boundary = circle at the surface outline
    n_b = 128
    circle = [[cx + lake_radius * _math.cos(2 * _math.pi * k / n_b),
               cy + lake_radius * _math.sin(2 * _math.pi * k / n_b)] for k in range(n_b)]
    circle.append(circle[0])
    bbox = [cx - lake_radius, cy - lake_radius, cx + lake_radius, cy + lake_radius]
    boundary_id = _pp_cache_id("bnd")
    _preprocess_cache["boundary"][boundary_id] = {
        "coords": circle, "rings": [circle], "bbox": bbox,
        "crs_info": crs_info, "orig_crs_type": crs_info["crs_type"],
    }
    bathy_id = _pp_cache_id("bthy")
    _preprocess_cache["bathymetry"][bathy_id] = {
        "geom_type": "point", "points": pts, "polygons": [], "depths": deps,
        "depth_field": "hypsograph", "crs_info": crs_info, "source": "hypsograph",
    }
    return jsonify({
        "boundary_id": boundary_id,
        "bathy_id": bathy_id,
        "n_levels": len(rings),
        "n_points": len(pts),
        "max_depth_m": round(max_depth, 2),
        "surface_area_m2": surface_area,
        "lake_radius_m": round(lake_radius, 1),
        "crs_type": crs_info["crs_type"],
        "warnings": warnings,
        "preview_points": pts[:200],
        "preview_depths": deps[:200],
    })


@app.route("/api/preprocess/grid/generate", methods=["POST"])
def preprocess_grid_generate():
    """Generate a Cartesian grid covering the cached boundary.

    Body: {boundary_id, dx, dy, x0?, y0?, nx?, ny?}
    Cells whose center is inside the boundary polygon are marked water.
    """
    data = request.json or {}
    boundary_id = data.get("boundary_id")
    if not boundary_id or boundary_id not in _preprocess_cache["boundary"]:
        return jsonify({"error": "无效或未上传的 boundary_id"}), 400
    bnd = _preprocess_cache["boundary"][boundary_id]
    try:
        dx = float(data.get("dx", 100))
        dy = float(data.get("dy", 100))
    except (TypeError, ValueError):
        return jsonify({"error": "dx/dy 必须是数字"}), 400
    if dx <= 0 or dy <= 0:
        return jsonify({"error": "dx/dy 必须大于 0"}), 400
    bbox = bnd["bbox"]
    x0 = data.get("x0")
    y0 = data.get("y0")
    nx = data.get("nx")
    ny = data.get("ny")
    if x0 is None:
        x0 = bbox[0] - dx * 0.5  # pad by half a cell so boundary fits
    if y0 is None:
        y0 = bbox[1] - dy * 0.5
    x0 = float(x0)
    y0 = float(y0)
    if nx is None:
        nx = int(_math.ceil((bbox[2] - x0) / dx)) + 1
    if ny is None:
        ny = int(_math.ceil((bbox[3] - y0) / dy)) + 1
    nx, ny = int(nx), int(ny)
    if nx <= 0 or ny <= 0:
        return jsonify({"error": "nx/ny 必须大于 0"}), 400
    if nx * ny > 200000:
        return jsonify({"error": f"网格过大 ({nx}x{ny}={nx*ny} cells)，请增大 dx/dy"}), 400
    rings = bnd.get("rings") or [bnd["coords"]]
    xc = x0 + (np.arange(nx) + 0.5) * dx
    yc = y0 + (np.arange(ny) + 0.5) * dy
    mask = np.zeros((ny, nx), dtype=bool)
    for j in range(ny):
        for i in range(nx):
            for poly in rings:
                if _point_in_polygon(xc[i], yc[j], poly):
                    mask[j, i] = True
                    break
    n_water = int(mask.sum())
    grid_id = _pp_cache_id("grid")
    _preprocess_cache["grid"][grid_id] = {
        "boundary_id": boundary_id,
        "nx": nx, "ny": ny, "dx": dx, "dy": dy,
        "x0": x0, "y0": y0,
        "xc": xc.tolist(), "yc": yc.tolist(),
        "mask": mask.tolist(),
        "n_water": n_water,
        "crs_info": bnd["crs_info"],
    }
    return jsonify({
        "grid_id": grid_id,
        "nx": nx, "ny": ny, "dx": dx, "dy": dy,
        "x0": x0, "y0": y0,
        "n_water_cells": n_water,
        "n_total_cells": nx * ny,
        "water_ratio": round(n_water / (nx * ny), 4),
        "lake_area_m2": n_water * dx * dy,
        "mask": mask.tolist(),
        "xc": xc.tolist(),
        "yc": yc.tolist(),
    })


@app.route("/api/preprocess/bathymetry/interpolate", methods=["POST"])
def preprocess_bathymetry_interpolate():
    """Interpolate cached depth data onto water cells of a cached grid.

    Body: {grid_id, bathy_id, method: 'nearest'|'linear'|'polygon'}
    Returns 2D depth array (land=-9999).
    """
    data = request.json or {}
    grid_id = data.get("grid_id")
    bathy_id = data.get("bathy_id")
    method = (data.get("method") or "linear").lower()
    if not grid_id or grid_id not in _preprocess_cache["grid"]:
        return jsonify({"error": "无效 grid_id"}), 400
    if not bathy_id or bathy_id not in _preprocess_cache["bathymetry"]:
        return jsonify({"error": "无效 bathy_id"}), 400
    grid = _preprocess_cache["grid"][grid_id]
    bthy = _preprocess_cache["bathymetry"][bathy_id]
    nx, ny = grid["nx"], grid["ny"]
    mask = np.array(grid["mask"], dtype=bool)
    xc = np.array(grid["xc"])
    yc = np.array(grid["yc"])
    bathy = np.full((ny, nx), -9999.0, dtype=float)
    geom = bthy["geom_type"]
    if geom == "point":
        pts = np.array(bthy["points"], dtype=float)
        vals = np.array(bthy["depths"], dtype=float)
        if pts.size == 0:
            return jsonify({"error": "水深 shapefile 没有点数据"}), 400
        # Build query points for water cells only
        water_idx = np.argwhere(mask)  # rows of (j, i)
        if len(water_idx) == 0:
            return jsonify({"error": "网格没有水域单元（请检查边界或网格大小）"}), 400
        query = np.array([[xc[i], yc[j]] for j, i in water_idx], dtype=float)
        interp_method = method if method in ("linear", "nearest") else "linear"
        try:
            res = griddata(pts, vals, query, method=interp_method)
        except Exception as e:
            return jsonify({"error": f"插值失败: {e}"}), 500
        # Fill NaNs (out of convex hull for 'linear') with nearest
        nans = np.isnan(res)
        if nans.all():
            # Guard: when the data cloud lies far from the grid (frame mismatch),
            # the nearest-neighbour fallback silently returns ONE single data
            # point's value for every cell (a constant field like 0.08 everywhere).
            # Refuse with an actionable message instead.
            dists, _ = cKDTree(pts).query(query, k=1)
            grid_diag = float(np.hypot(xc[-1] - xc[0], yc[-1] - yc[0]))
            if float(dists.min()) > grid_diag:
                return jsonify({
                    "error": "高程数据点与网格完全不重叠（最近距离 %.0f m）——"
                             "两者坐标系不一致且未自动转换。请回到'底部高程'步骤，"
                             "将'数据坐标系'选为该文件的真实坐标系后重新上传，"
                             "再重新插值" % float(dists.min()),
                }), 400
        if nans.any():
            try:
                nn = griddata(pts, vals, query[nans], method="nearest")
                res[nans] = nn
            except Exception:
                res[nans] = float(np.nanmean(vals))
        for k, (j, i) in enumerate(water_idx):
            bathy[j, i] = float(res[k])
    else:  # polygon: each water cell center → which polygon it falls in
        polys = bthy["polygons"]
        depths = bthy["depths"]
        if not polys:
            return jsonify({"error": "水深 shapefile 没有面数据"}), 400
        # Spatially index polygons by their bbox to cut work
        poly_bboxes = []
        for p in polys:
            xs = [pt[0] for pt in p]
            ys = [pt[1] for pt in p]
            poly_bboxes.append((min(xs), min(ys), max(xs), max(ys)))
        for j in range(ny):
            for i in range(nx):
                if not mask[j, i]:
                    continue
                x, y = xc[i], yc[j]
                matched = None
                for k, bb in enumerate(poly_bboxes):
                    if bb[0] <= x <= bb[2] and bb[1] <= y <= bb[3]:
                        if _point_in_polygon(x, y, polys[k]):
                            matched = k
                            break
                if matched is not None:
                    bathy[j, i] = float(depths[matched])
        # If any water cell unmatched, fill with nearest non-zero depth
        if mask.any() and (bathy[mask] <= 0).any():
            fill_value = float(np.median([d for d in depths if d > 0])) if any(d > 0 for d in depths) else 1.0
            for j in range(ny):
                for i in range(nx):
                    if mask[j, i] and bathy[j, i] <= 0:
                        bathy[j, i] = fill_value
    # Cache interpolated result
    grid["depth_array"] = bathy.tolist()
    water_vals = bathy[mask]
    return jsonify({
        "depth_array": bathy.tolist(),
        "n_water_cells": int(mask.sum()),
        "depth_min": float(np.min(water_vals)),
        "depth_max": float(np.max(water_vals)),
        "depth_mean": float(np.mean(water_vals)),
        "nx": nx, "ny": ny,
    })


@_with_nc_lock
def _write_bathymetry_nc_standalone(path, nx, ny, dx, dy, x0, y0,
                                    bathymetry, lat0, lon0, lake_name="Lake",
                                    transformer=None):
    """Write bathymetry.nc in GETM format. Mirrors preprocessor/generate_bathymetry.py.

    x/y = metric cell centers; latc/lonc = geographic degrees.
    When `transformer` (pyproj src->WGS84) is given, cell centers are reprojected
    EXACTLY (correct for Albers/GK/any projected CRS). Otherwise the legacy
    simplified inverse-UTM approximation is used (only sane for true UTM grids).
    bathymetry positive=depth, -9999=land.
    """
    ds = nc.Dataset(path, "w", format="NETCDF4")
    ds.createDimension("x", nx)
    ds.createDimension("y", ny)
    ds.createDimension("xq", nx + 1)
    ds.createDimension("yq", ny + 1)
    grid_type_var = ds.createVariable("grid_type", "i4")
    grid_type_var[:] = 1  # Cartesian
    x_var = ds.createVariable("x", "f8", ("x",))
    x_var.units = "m"
    x_var.long_name = "x coordinate of cell centers"
    x_var[:] = x0 + (np.arange(nx) + 0.5) * dx
    y_var = ds.createVariable("y", "f8", ("y",))
    y_var.units = "m"
    y_var.long_name = "y coordinate of cell centers"
    y_var[:] = y0 + (np.arange(ny) + 0.5) * dy
    lat_var = ds.createVariable("latc", "f8", ("y", "x"))
    lat_var.units = "degrees_north"
    lat_var.long_name = "latitude of cell centers"
    lon_var = ds.createVariable("lonc", "f8", ("y", "x"))
    lon_var.units = "degrees_east"
    lon_var.long_name = "longitude of cell centers"
    # Inverse projection to recover lat/lon at cell centers.
    y_arr = y0 + (np.arange(ny) + 0.5) * dy
    x_arr = x0 + (np.arange(nx) + 0.5) * dx
    if transformer is not None:
        # Exact pyproj reproject of every cell center (Albers/GK/UTM all correct)
        xg, yg = np.meshgrid(x_arr, y_arr)
        try:
            lon2d, lat2d = transformer.transform(xg, yg)
            lon_var[:] = np.asarray(lon2d, dtype="f8")
            lat_var[:] = np.asarray(lat2d, dtype="f8")
        except Exception as e:
            raise ValueError(f"pyproj 网格坐标转换失败: {e}")
    else:
        # Legacy simplified inverse UTM (only approximate for true UTM grids)
        zone = _utm_zone_from_lon(lon0)
        cm = (zone - 1) * 6.0 - 180.0 + 3.0
        for j in range(ny):
            lat_j = y_arr[j] / 110574.0
            lat_var[j, :] = lat_j
            cos_lat = _math.cos(_math.radians(lat_j))
            for i in range(nx):
                lon_i = cm + (x_arr[i] - 500000.0) / (111320.0 * cos_lat)
                lon_var[j, i] = lon_i
    bath_var = ds.createVariable("bathymetry", "f8", ("y", "x"))
    bath_var.units = "m"
    bath_var.long_name = "water depth"
    bath_var.standard_name = "sea_floor_depth"
    bath_var.coordinates = "lonc latc"
    bath_var[:] = bathymetry
    ds.title = f"{lake_name} bathymetry"
    ds.source = "Generated by 3DWET preprocess (shapefile → grid → interpolate)"
    ds.history = f"Created {datetime.now()}"
    ds.Conventions = "CF-1.0"
    ds.close()


@app.route("/api/preprocess/save", methods=["POST"])
def preprocess_save():
    """Save the cached grid + interpolated depth as bathymetry.nc in a case.

    Body: {case_name, grid_id, lake_name?, rivers?: [{i, j, name}]}
    Requires the grid to have a depth_array cached (from interpolate step).
    River marks are persisted to rivers_setup.json for the input-data page.
    """
    data = request.json or {}
    case_name = (data.get("case_name") or "").strip()
    grid_id = data.get("grid_id")
    lake_name = (data.get("lake_name") or case_name or "Lake").strip()
    rivers = data.get("rivers") or []
    if not case_name:
        return jsonify({"error": "缺少 case_name"}), 400
    if not grid_id or grid_id not in _preprocess_cache["grid"]:
        return jsonify({"error": "无效 grid_id"}), 400
    grid = _preprocess_cache["grid"][grid_id]
    if "depth_array" not in grid:
        return jsonify({"error": "请先执行水深插值步骤"}), 400
    case_path = CASE_DIR / case_name
    case_path.mkdir(parents=True, exist_ok=True)
    bathy = np.array(grid["depth_array"], dtype=float)
    crs = grid.get("crs_info", {})
    bnd = _preprocess_cache["boundary"].get(grid.get("boundary_id"))
    # Exact geographic coordinates: when the boundary carried a .prj WKT
    # (Albers / GK / UTM ...), reproject cell centers with pyproj.
    transformer = None
    geo_note = None
    wkt = (bnd or {}).get("crs_info", {}).get("wkt")
    if wkt:
        try:
            src_crs = crs_utils.crs_from_wkt(wkt)
            if src_crs is not None:
                transformer = crs_utils.make_transformer(src_crs, crs_utils.WGS84)
                geo_note = "经纬度由 .prj WKT 精确重投影"
        except Exception:
            transformer = None
    if bnd and transformer is None and "origin_lat" in bnd["crs_info"]:
        lat0 = bnd["crs_info"]["origin_lat"]
        lon0 = bnd["crs_info"]["origin_lon"]
    elif bnd:
        # Reverse-engineer from y0 / utm_zone
        y0 = grid["y0"]
        lat0 = y0 / 110574.0
        zone = bnd["crs_info"].get("utm_zone") or _utm_zone_from_lon(120.0)
        lon0 = (zone - 1) * 6.0 - 180.0 + 3.0
    else:
        lat0, lon0 = 30.0, 120.0
    out_path = case_path / "bathymetry.nc"
    try:
        _write_bathymetry_nc_standalone(
            str(out_path),
            grid["nx"], grid["ny"],
            grid["dx"], grid["dy"],
            grid["x0"], grid["y0"],
            bathy, lat0, lon0, lake_name, transformer=transformer
        )
    except Exception as e:
        return jsonify({"error": f"写入 bathymetry.nc 失败: {e}"}), 500
    # Persist river marks + grid meta so the input-data page and case builder
    # can regenerate riverinfo.dat / rivers.nc / coordinates later.
    try:
        meta = {
            "case_name": case_name,
            "lake_name": lake_name,
            "grid": {
                "nx": grid["nx"], "ny": grid["ny"],
                "dx": grid["dx"], "dy": grid["dy"],
                "x0": grid["x0"], "y0": grid["y0"],
            },
            "rivers": rivers,
            "boundary_wkt": wkt,
        }
        with open(case_path / "rivers_setup.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
    except Exception as e:
        return jsonify({"error": f"写入 rivers_setup.json 失败: {e}"}), 500
    # Activate the new case so the user can continue configuring it
    global active_case, active_case_path, cached_getm_config, cached_fabm_info
    active_case = case_name
    active_case_path = case_path
    cached_getm_config = None
    cached_fabm_info = None
    return jsonify({
        "success": True,
        "case_name": case_name,
        "path": str(out_path),
        "n_water_cells": grid["n_water"],
        "lake_area_m2": grid["n_water"] * grid["dx"] * grid["dy"],
        "n_rivers": len(rivers),
        "geo_note": geo_note,
    })


@app.route("/api/preprocess/preview")
def preprocess_preview():
    """Return lightweight preview payload for a given cache id."""
    bid = request.args.get("boundary_id")
    gid = request.args.get("grid_id")
    out = {}
    if bid and bid in _preprocess_cache["boundary"]:
        b = _preprocess_cache["boundary"][bid]
        coords = b["coords"]
        step = max(1, len(coords) // 400)
        out["boundary"] = {
            "coords": coords[::step],
            "bbox": b["bbox"],
            "crs_type": b["crs_info"]["crs_type"],
        }
    if gid and gid in _preprocess_cache["grid"]:
        g = _preprocess_cache["grid"][gid]
        out["grid"] = {
            "nx": g["nx"], "ny": g["ny"],
            "dx": g["dx"], "dy": g["dy"],
            "x0": g["x0"], "y0": g["y0"],
            "mask": g["mask"],
            "depth_array": g.get("depth_array"),
        }
    return jsonify(out)


# ══════════════════════════════════════════════════════════════════════
# Routes: Input Data (meteo / rivers time series → netCDF) & Case Build
# ══════════════════════════════════════════════════════════════════════

# Trophic-state presets mapped onto the Luoma fabm.yaml instance names.
# Fish modules are absent from the current WET fabm.yaml and are skipped.
_PRESET_MODULE_MAP = {
    "sNH4W": ("abiotic_water", "sNH4W"),
    "sNO3W": ("abiotic_water", "sNO3W"),
    "sPO4W": ("abiotic_water", "sPO4W"),
    "sO2W": ("abiotic_water", "sO2W"),
    "sSiO2W": ("abiotic_water", "sSiO2W"),
    "diatoms_sDW": ("diatoms", "sDW"),
    "greens_sDW": ("greens", "sDW"),
    "cyanobacteria_sDW": ("cyanobacteria", "sDW"),
    "cladocerans_sD": ("cladocerans", "sD"),
    "copepods_sD": ("copepods", "sD"),
    "zoobenthos_sD": ("zoobenthos", "sD"),
    "POM_sDW": ("POM", "sDW"),
    "DOM_sDW": ("DOM", "sDW"),
}

TROPHIC_PRESETS = {
    "mesotrophic": {
        "label": "中营养（水草清水态）",
        "sNH4W": 0.10, "sNO3W": 0.30, "sPO4W": 0.02, "sO2W": 8.0, "sSiO2W": 2.0,
        "diatoms_sDW": 0.10, "greens_sDW": 0.08, "cyanobacteria_sDW": 0.05,
        "cladocerans_sD": 0.15, "copepods_sD": 0.15,
        "zoobenthos_sD": 0.25, "POM_sDW": 2.0, "DOM_sDW": 5.0,
        "macro_sD": 15.0,
    },
    "eutrophic": {
        "label": "富营养（藻类浊水态）",
        "sNH4W": 0.30, "sNO3W": 1.00, "sPO4W": 0.06, "sO2W": 10.0, "sSiO2W": 3.5,
        "diatoms_sDW": 0.30, "greens_sDW": 0.20, "cyanobacteria_sDW": 0.30,
        "cladocerans_sD": 0.30, "copepods_sD": 0.30,
        "zoobenthos_sD": 0.40, "POM_sDW": 5.0, "DOM_sDW": 10.0,
        "macro_sD": 8.0,
    },
    "hypereutrophic": {
        "label": "重富营养（蓝藻水华频发）",
        "sNH4W": 0.80, "sNO3W": 2.00, "sPO4W": 0.15, "sO2W": 12.0, "sSiO2W": 5.0,
        "diatoms_sDW": 0.50, "greens_sDW": 0.30, "cyanobacteria_sDW": 0.80,
        "cladocerans_sD": 0.40, "copepods_sD": 0.35,
        "zoobenthos_sD": 0.50, "POM_sDW": 8.0, "DOM_sDW": 15.0,
        "macro_sD": 4.0,
    },
}

_METEO_ALIASES = {
    "date": ["date", "time", "datetime", "日期", "时间"],
    "u10": ["u10", "u", "uwind", "wind_u", "风速u", "纬向风"],
    "v10": ["v10", "v", "vwind", "wind_v", "风速v", "经向风"],
    "slp": ["slp", "pressure", "pres", "sp", "气压", "海平面气压"],
    "t2": ["t2", "tair", "air_temp", "temp", "temperature", "气温", "温度"],
    "rh": ["rh", "hur", "humidity", "相对湿度"],
    "tcc": ["tcc", "cloud", "clt", "云量", "总云量"],
    "precip": ["precip", "precipitation", "pr", "rain", "降雨", "降水", "降水量"],
    "evap": ["evap", "evaporation", "蒸散", "蒸发", "蒸发量"],
}
_RIVER_ALIASES = {
    "date": ["date", "time", "datetime", "日期", "时间"],
    "Q": ["q", "discharge", "flow", "流量"],
    "temp": ["temp", "t", "water_temp", "wt", "水温", "温度"],
    "nh4": ["nh4", "nh4-n", "nh4n", "ammonium", "氨氮"],
    "no3": ["no3", "no3-n", "no3n", "nitrate", "硝氮", "硝酸盐"],
    "po4": ["po4", "po4-p", "po4p", "phosphate", "磷酸盐", "活性磷"],
}


def _map_columns(header, aliases):
    """Map CSV header names onto canonical keys via alias lists.

    Returns (mapping {canonical: column_index}, missing_required list).
    """
    norm = [h.strip().lower().replace(" ", "") for h in header]
    mapping = {}
    for key, names in aliases.items():
        for n in names:
            if n in norm:
                mapping[key] = norm.index(n)
                break
    return mapping


def _parse_date(s):
    """Parse a date/datetime string; returns datetime or None."""
    s = str(s).strip().replace("T", " ")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d",
                "%Y/%m/%d %H:%M:%S", "%Y/%m/%d %H:%M", "%Y/%m/%d",
                "%Y%m%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(s.split(".")[0].strip(), fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def _to_float(s):
    try:
        v = float(str(s).replace(",", ""))
        return v
    except (TypeError, ValueError):
        return None


def _read_csv_rows(file_storage):
    """Read an uploaded CSV into (header, rows). Handles BOM and gbk."""
    raw = file_storage.read()
    for enc in ("utf-8-sig", "utf-8", "gbk"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = raw.decode("utf-8", errors="replace")
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if len(lines) < 2:
        return None, []
    header = next(csv.reader([lines[0]]))
    rows = list(csv.reader(lines[1:]))
    return header, rows


def _case_meta_path():
    return active_case_path / "rivers_setup.json" if active_case_path else None


def _load_case_meta():
    p = _case_meta_path()
    if p and p.exists():
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


@app.route("/api/input/rivers")
def input_rivers_info():
    """River marks (from preprocess) + per-river CSV draft status."""
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    meta = _load_case_meta() or {"rivers": [], "grid": None}
    draft_dir = active_case_path / "river_drafts"
    rivers = []
    for r in meta.get("rivers", []):
        name = str(r.get("name", "")).strip()
        draft_p = draft_dir / f"{name}.json" if name else None
        has_draft = bool(draft_p and draft_p.exists())
        n_rows = 0
        if has_draft:
            try:
                with open(draft_p, "r", encoding="utf-8") as f:
                    n_rows = len(json.load(f).get("dates", []))
            except Exception:
                n_rows = 0
        rivers.append({
            "i": int(r.get("i", 0)), "j": int(r.get("j", 0)),
            "name": name, "has_draft": has_draft, "n_rows": n_rows,
        })
    return jsonify({
        "rivers": rivers,
        "grid": meta.get("grid"),
        "has_rivers_nc": (active_case_path / "rivers.nc").exists(),
        "has_riverinfo": (active_case_path / "riverinfo.dat").exists(),
    })


@app.route("/api/input/rivers/series")
def input_rivers_series():
    """Time series of one river from rivers.nc, for input-data visualization.

    Query: ?name=PANLONGJIANG
    Returns {times, series: {flow/temp/nh4/no3/po4: {values, units, long_name}}}.
    """
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    name = (request.args.get("name") or "").strip()
    if not name:
        return jsonify({"error": "缺少 name 参数"}), 400
    p = active_case_path / "rivers.nc"
    if not p.exists():
        return jsonify({"error": "rivers.nc 不存在，请先在输入数据页生成"}), 404
    try:
        with nc_open(p) as ds:
            if name not in ds.variables:
                return jsonify({"error": f"河流 {name} 不在 rivers.nc 中"}), 404

            def _fill(a):
                return a.filled(np.nan) if isinstance(a, np.ma.MaskedArray) else np.asarray(a, dtype=float)

            times = []
            if "time" in ds.variables:
                tvals = ds.variables["time"][:]
                tunits = getattr(ds.variables["time"], "units", "")
                try:
                    times = nc.num2date(tvals, tunits).tolist()
                    times = [t.strftime("%Y-%m-%d %H:%M") if hasattr(t, "strftime") else str(t) for t in times]
                except Exception:
                    times = [float(t) for t in tvals]
            else:
                return jsonify({"error": "rivers.nc 缺少时间维度"}), 400

            series = {}
            # 流量 + 常见水质列（<name>_temp/_nh4/_no3/_po4 等，存在才返回）
            for vn in ds.variables:
                if vn == "time" or not vn.startswith(name):
                    continue
                var = ds.variables[vn]
                if var.ndim != 1 or var.shape[0] != len(times):
                    continue
                vals = _fill(var[:])
                key = "flow" if vn == name else vn[len(name) + 1:].lower()
                if key in series:
                    key = vn
                series[key] = {
                    "values": [float(v) if np.isfinite(v) else None for v in vals],
                    "units": getattr(var, "units", ""),
                    "long_name": getattr(var, "long_name", vn),
                    "nc_var": vn,
                }
        if not series:
            return jsonify({"error": f"rivers.nc 中没有 {name} 的数据列"}), 404
        return jsonify({"name": name, "times": times, "series": series})
    except Exception as e:
        return jsonify({"error": f"读取 rivers.nc 失败: {e}"}), 500


@app.route("/api/input/rivers/add", methods=["POST"])
def input_rivers_add():
    """Manually add a river mark {i, j, name} to rivers_setup.json."""
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    data = request.json or {}
    name = str(data.get("name", "")).strip()
    try:
        i, j = int(data.get("i")), int(data.get("j"))
    except (TypeError, ValueError):
        return jsonify({"error": "i/j 必须是整数"}), 400
    if not name or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,23}", name):
        return jsonify({"error": "河流名须为英文/数字/下划线（netCDF 变量名要求），如 PANLONGJING"}), 400
    meta = _load_case_meta() or {"rivers": [], "grid": None, "lake_name": active_case}
    rivers = meta.setdefault("rivers", [])
    if any(r["name"].lower() == name.lower() for r in rivers):
        return jsonify({"error": f"河流 {name} 已存在"}), 400
    rivers.append({"i": i, "j": j, "name": name})
    # 格点校验（滇池孤立格点堆积事故）：陆地格点直接拒绝，孤立水域提示
    a_errors, a_warnings = _river_cell_problems([{"i": i, "j": j, "name": name}], active_case_path)
    if a_errors:
        rivers.pop()
        return jsonify({"error": a_errors[0]}), 400
    if a_warnings:
        with open(_case_meta_path(), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        return jsonify({"success": True, "warning": a_warnings[0]})
    with open(_case_meta_path(), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    return jsonify({"success": True})


@app.route("/api/input/rivers/delete", methods=["POST"])
def input_rivers_delete():
    """Remove a river mark (and its draft) by name."""
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    name = (request.json or {}).get("name", "")
    meta = _load_case_meta()
    if not meta:
        return jsonify({"error": "无 rivers_setup.json"}), 400
    meta["rivers"] = [r for r in meta.get("rivers", []) if r.get("name") != name]
    with open(_case_meta_path(), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    draft = active_case_path / "river_drafts" / f"{name}.json"
    if draft.exists():
        draft.unlink()
    return jsonify({"success": True})


@app.route("/api/input/rivers/upload", methods=["POST"])
def input_rivers_upload():
    """Upload one river's CSV time series → river_drafts/{NAME}.json.

    Multipart: river_name + file. Columns: date,Q,temp,nh4,no3,po4 (aliases OK).
    Q: m3/s (positive = inflow, negative = outflow); nutrients g/m3.
    """
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    name = (request.form.get("river_name") or "").strip()
    if not name:
        return jsonify({"error": "缺少 river_name"}), 400
    f = request.files.get("file")
    if f is None:
        return jsonify({"error": "缺少 CSV 文件"}), 400
    header, rows = _read_csv_rows(f)
    if header is None:
        return jsonify({"error": "CSV 为空或只有表头"}), 400
    m = _map_columns(header, _RIVER_ALIASES)
    missing = [k for k in ("date", "Q") if k not in m]
    if missing:
        return jsonify({"error": f"CSV 缺少必需列: {', '.join(missing)}（识别到的列: {', '.join(header)}）"}), 400
    dates, series = [], {k: [] for k in ("Q", "temp", "nh4", "no3", "po4")}
    bad = 0
    for row in rows:
        if len(row) <= max(m.values()):
            continue
        d = _parse_date(row[m["date"]])
        if d is None:
            bad += 1
            continue
        dates.append(d.strftime("%Y-%m-%d"))
        for k in series:
            v = _to_float(row[m[k]]) if k in m else None
            series[k].append(v)
    if len(dates) < 2:
        return jsonify({"error": "有效数据行不足 2 行（日期列无法解析）"}), 400
    # Default-fill optional columns
    for k, default in (("temp", 15.0), ("nh4", 0.05), ("no3", 0.5), ("po4", 0.02)):
        if all(v is None for v in series[k]):
            series[k] = [default] * len(dates)
        else:
            series[k] = [v if v is not None else _last_valid(series[k], idx) for idx, v in enumerate(series[k])]
    draft_dir = active_case_path / "river_drafts"
    draft_dir.mkdir(exist_ok=True)
    payload = {"dates": dates, **series}
    with open(draft_dir / f"{name}.json", "w", encoding="utf-8") as fo:
        json.dump(payload, fo, ensure_ascii=False)
    q = [v for v in series["Q"] if v is not None]
    return jsonify({
        "success": True, "river": name, "n_rows": len(dates),
        "date_range": [dates[0], dates[-1]],
        "q_min": min(q), "q_max": max(q), "q_mean": sum(q) / len(q),
        "n_outflow_days": sum(1 for v in q if v < 0),
        "n_bad_rows": bad,
        "unmapped_cols": [h for h in header if h.strip().lower().replace(" ", "") not in
                          [a for al in _RIVER_ALIASES.values() for a in al]],
    })


def _last_valid(arr, idx):
    for k in range(idx, -1, -1):
        if arr[k] is not None:
            return arr[k]
    return 0.0


@app.route("/api/input/rivers/save", methods=["POST"])
def input_rivers_save():
    """Write riverinfo.dat + rivers.nc from river marks + drafts."""
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    meta = _load_case_meta()
    rivers = (meta or {}).get("rivers", [])
    if not rivers:
        return jsonify({"error": "没有河流标记（请先在前处理标记河流或在此页添加）"}), 400
    draft_dir = active_case_path / "river_drafts"
    missing = [r["name"] for r in rivers if not (draft_dir / f"{r['name']}.json").exists()]
    if missing:
        return jsonify({"error": "以下河流尚未上传流量数据: " + ", ".join(missing)}), 400
    # 格点校验：入湖点必须是水域且不孤立（滇池盘龙江孤立格点堆积事故）
    r_errors, r_warnings = _river_cell_problems(rivers, active_case_path)
    if r_errors:
        return jsonify({"error": "河流格点校验失败: " + "；".join(r_errors)}), 400
    # Union of all dates across rivers (sorted); forward-fill each river onto it
    all_dates = sorted({d for r in rivers
                        for d in json.load(open(draft_dir / f"{r['name']}.json", encoding="utf-8"))["dates"]})
    if not all_dates:
        return jsonify({"error": "河流数据为空"}), 400
    start = _current_case_start(all_dates[0])
    base = datetime.strptime(all_dates[0], "%Y-%m-%d")
    tvals = [(datetime.strptime(d, "%Y-%m-%d") - base).total_seconds() for d in all_dates]
    _NC_LOCK.acquire()
    try:
        ds = nc.Dataset(str(active_case_path / "rivers.nc"), "w", format="NETCDF4")
        # GETM's init_river_input_ncdf looks up the unlimited dimension and
        # queries it directly; a fixed-length time dim makes unlimdimid=-1 and
        # the model dies with "NetCDF: Invalid dimension ID or name".
        ds.createDimension("time", None)
        tv = ds.createVariable("time", "f8", ("time",))
        tv.units = f"seconds since {start}"
        tv.long_name = "time"
        tv[:] = np.array(tvals, dtype="f8")
        for r in rivers:
            name = r["name"].upper()
            with open(draft_dir / f"{r['name']}.json", encoding="utf-8") as f:
                d = json.load(f)
            idx = {dt: k for k, dt in enumerate(d["dates"])}
            def series(key):
                out, last = [], None
                for dt in all_dates:
                    k = idx.get(dt)
                    if k is not None:
                        last = d[key][k]
                    out.append(last if last is not None else 0.0)
                # backward-fill leading Nones
                first = next((v for v in out if v is not None), 0.0)
                return [first if v is None else v for v in out]
            spec = [("Q", "", "discharge", "m3/s", "f8"),
                    ("temp", "_temp", "temperature", "degC", "f8"),
                    ("nh4", "_nh4", "ammonium", "g/m3", "f8"),
                    ("no3", "_no3", "nitrate", "g/m3", "f8"),
                    ("po4", "_po4", "phosphate", "g/m3", "f8")]
            for key, suf, lname, unit, dtype in spec:
                v = ds.createVariable(name + suf, dtype, ("time",))
                v.units = unit
                v.long_name = f"{name} {lname}"
                v[:] = np.array(series(key), dtype=dtype)
    finally:
        try:
            ds.close()
        except Exception:
            pass
        _NC_LOCK.release()
    lines = [str(len(rivers))]
    for r in rivers:
        lines.append(f"{int(r['i'])} {int(r['j'])} {r['name'].upper()} -1 -1")
    (active_case_path / "riverinfo.dat").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return jsonify({"success": True, "n_rivers": len(rivers), "n_times": len(all_dates),
                    "date_range": [all_dates[0], all_dates[-1]], "start": start})


def _current_case_start(default_str):
    """Start datetime for time units: getm.inp start if present, else default."""
    inp = active_case_path / "getm.inp" if active_case_path else None
    if inp and inp.exists():
        try:
            cfg = parse_getm_inp(inp)
            s = cfg.get("time", {}).get("start")
            if s:
                d = _parse_date(str(s).strip("'"))
                if d:
                    return d.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass
    d = _parse_date(default_str)
    return d.strftime("%Y-%m-%d 00:00:00") if d else default_str


@app.route("/api/input/meteo/upload", methods=["POST"])
def input_meteo_upload():
    """Upload meteo CSV → meteo_draft.json. Columns (aliases OK):
    date,u10,v10,slp,t2,rh,tcc,precip,evap.
    Units: u10/v10 m/s, slp hPa, t2 degC, rh/tcc 0-1 (or %), precip/evap mm/day.
    """
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    f = request.files.get("file")
    if f is None:
        return jsonify({"error": "缺少 CSV 文件"}), 400
    header, rows = _read_csv_rows(f)
    if header is None:
        return jsonify({"error": "CSV 为空或只有表头"}), 400
    m = _map_columns(header, _METEO_ALIASES)
    missing = [k for k in ("date", "u10", "v10", "t2") if k not in m]
    if missing:
        return jsonify({"error": f"CSV 缺少必需列: {', '.join(missing)}（识别到的列: {', '.join(header)}）"}), 400
    keys = ["u10", "v10", "slp", "t2", "rh", "tcc", "precip", "evap"]
    dates, series = [], {k: [] for k in keys}
    bad = 0
    for row in rows:
        if len(row) <= max(m.values()):
            continue
        d = _parse_date(row[m["date"]])
        if d is None:
            bad += 1
            continue
        dates.append(d.strftime("%Y-%m-%d"))
        for k in keys:
            series[k].append(_to_float(row[m[k]]) if k in m else None)
    if len(dates) < 2:
        return jsonify({"error": "有效数据行不足 2 行（日期列无法解析）"}), 400
    stats = {}
    for k in keys:
        vals = [v for v in series[k] if v is not None]
        if not vals:  # column entirely missing → sensible defaults
            default = {"u10": 2.0, "v10": 1.0, "slp": 1013.0, "t2": 15.0,
                       "rh": 0.7, "tcc": 0.5, "precip": 0.0, "evap": 0.0}[k]
            series[k] = [default] * len(dates)
            stats[k] = {"default": default}
        else:
            series[k] = [_last_valid(series[k], i) if v is None else v for i, v in enumerate(series[k])]
            stats[k] = {"min": min(vals), "mean": sum(vals) / len(vals), "max": max(vals)}
    payload = {"dates": dates, **series}
    with open(active_case_path / "meteo_draft.json", "w", encoding="utf-8") as fo:
        json.dump(payload, fo, ensure_ascii=False)
    return jsonify({
        "success": True, "n_rows": len(dates),
        "date_range": [dates[0], dates[-1]],
        "stats": stats, "n_bad_rows": bad,
        "unmapped_cols": [h for h in header if h.strip().lower().replace(" ", "") not in
                          [a for al in _METEO_ALIASES.values() for a in al]],
    })


@app.route("/api/input/meteo/draft")
def input_meteo_draft():
    """Return the cached meteo draft (for table preview/edit)."""
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    p = active_case_path / "meteo_draft.json"
    if not p.exists():
        return jsonify({"exists": False})
    with open(p, "r", encoding="utf-8") as f:
        d = json.load(f)
    return jsonify({"exists": True, "dates": d["dates"],
                    **{k: d[k] for k in ("u10", "v10", "slp", "t2", "rh", "tcc", "precip", "evap")}})


@app.route("/api/input/meteo/save", methods=["POST"])
def input_meteo_save():
    """Write meteo.nc (+ meteo_input.txt) from draft or from posted edited rows.

    Body: optional {rows: [{date,u10,v10,slp,t2,rh,tcc,precip,evap}, ...]}
    Broadcasts the single-station series onto the case grid (on_grid mode).
    """
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    bathy_p = active_case_path / "bathymetry.nc"
    if not bathy_p.exists():
        return jsonify({"error": "缺少 bathymetry.nc（请先完成前处理）"}), 400
    draft_p = active_case_path / "meteo_draft.json"
    data = request.json or {}
    rows = data.get("rows")
    if rows:
        dates = [r["date"] for r in rows]
        series = {k: [float(r.get(k) or 0.0) for r in rows]
                  for k in ("u10", "v10", "slp", "t2", "rh", "tcc", "precip", "evap")}
    elif draft_p.exists():
        with open(draft_p, "r", encoding="utf-8") as f:
            d = json.load(f)
        dates = d["dates"]
        series = {k: d[k] for k in ("u10", "v10", "slp", "t2", "rh", "tcc", "precip", "evap")}
    else:
        return jsonify({"error": "无气象草稿数据（请先上传 CSV）"}), 400
    if len(dates) < 2:
        return jsonify({"error": "有效数据不足 2 行"}), 400
    # Auto-extend to model stop (+1 day) by repeating the last daily record.
    # 滇池事故：CSV 比 getm.inp stop 早结束 → 模型在 99.999% 处 meteo EOF 崩溃。
    n_ext = 0
    _inp = active_case_path / "getm.inp"
    if _inp.exists():
        try:
            _stop = _parse_date(parse_getm_inp(_inp).get("time", {}).get("stop", ""))
        except Exception:
            _stop = None
        if _stop is not None:
            _need_end = _stop + timedelta(days=1)
            _last = _parse_date(dates[-1])
            if _last is not None and _last < _need_end:
                _ext, _d = [], _last + timedelta(days=1)
                while _d <= _need_end:
                    _ext.append(_d)
                    _d += timedelta(days=1)
                if _ext:
                    n_ext = len(_ext)
                    for k in ("u10", "v10", "slp", "t2", "rh", "tcc", "precip", "evap"):
                        series[k] = list(series[k]) + [series[k][-1]] * n_ext
                    dates = list(dates) + [d.strftime("%Y-%m-%d") for d in _ext]
    # Unit normalisation
    def col(key):
        return np.array(series[key], dtype=float)
    u10, v10 = col("u10"), col("v10")
    slp = col("slp")
    if np.nanmean(slp) < 5000.0:      # hPa → Pa
        slp = slp * 100.0
    t2 = col("t2")
    rh = col("rh")
    if np.nanmean(rh) > 1.5:          # % → fraction
        rh = rh / 100.0
    tcc = col("tcc")
    if np.nanmean(tcc) > 1.5:
        tcc = tcc / 100.0
    precip = col("precip") / 86400.0 / 1000.0   # mm/day → m/s
    # GETM fwf = precip + evap；蒸发必须是负值（long_name 已注明 negative =
    # water loss）。滇池事故：evap 写成正号 → 全年 974mm 蒸发被当成入流。
    # 用 abs() 强制符号，用户 CSV 里无论给正负值都归一为负。
    evap = -np.abs(col("evap")) / 86400.0 / 1000.0
    start = _current_case_start(dates[0])
    base = _parse_date(dates[0])
    tvals = np.array([(_parse_date(d) - base).total_seconds() for d in dates], dtype="f8")
    # Grid geometry from bathymetry.nc
    with nc_open(bathy_p) as bds:
        lon2d = np.array(bds.variables["lonc"][:])
        lat2d = np.array(bds.variables["latc"][:])
    ny, nx = lon2d.shape
    lon1d = lon2d[ny // 2, :]
    lat1d = lat2d[:, nx // 2]
    _NC_LOCK.acquire()
    try:
        ds = nc.Dataset(str(active_case_path / "meteo.nc"), "w", format="NETCDF4")
        ds.createDimension("lon", nx)
        ds.createDimension("lat", ny)
        ds.createDimension("time", len(dates))
        lv = ds.createVariable("lon", "f8", ("lon",))
        lv.units = "degrees_east"; lv.long_name = "longitude"; lv[:] = lon1d
        lv2 = ds.createVariable("lat", "f8", ("lat",))
        lv2.units = "degrees_north"; lv2.long_name = "latitude"; lv2[:] = lat1d
        tv = ds.createVariable("time", "f8", ("time",))
        tv.units = f"seconds since {start}"; tv.long_name = "time"; tv[:] = tvals
        def put(name, arr, dtype, unit, lname):
            v = ds.createVariable(name, dtype, ("time", "lat", "lon"))
            v.units = unit; v.long_name = lname
            v[:] = np.repeat(arr[:, None, None], ny * nx, axis=1).reshape(len(dates), ny, nx)
        put("u10", u10.astype("f4"), "f4", "m s-1", "10m wind u-component")
        put("v10", v10.astype("f4"), "f4", "m s-1", "10m wind v-component")
        put("slp", slp.astype("f4"), "f4", "Pa", "sea level pressure")
        put("t2", t2.astype("f4"), "f4", "degC", "2m air temperature")
        put("rh", rh.astype("f4"), "f4", "1", "relative humidity")
        put("tcc", tcc.astype("f4"), "f4", "1", "total cloud cover")
        put("precip", precip, "f8", "m s-1", "precipitation rate")
        put("evap", evap, "f8", "m s-1", "evaporation rate (negative = water loss)")
    finally:
        try:
            ds.close()
        except Exception:
            pass
        _NC_LOCK.release()
    (active_case_path / "meteo_input.txt").write_text("meteo.nc\n", encoding="utf-8")
    return jsonify({"success": True, "n_times": len(dates), "grid": f"{nx}x{ny}", "start": start,
                    "extended_days": n_ext})


# ── Case skeleton builder ─────────────────────────────────────────────

def _fix_case_geo(case_path):
    """Detect a wrong latc/lonc in bathymetry.nc (legacy simplified inverse-UTM
    applied to Albers/GK coordinates) and reproject exactly using the boundary
    .prj WKT persisted in _shp_uploads. Returns a note or None."""
    bathy_p = case_path / "bathymetry.nc"
    if not bathy_p.exists():
        return None
    with nc_open(bathy_p) as ds:
        if "latc" not in ds.variables or "x" not in ds.variables:
            return None
        lat = np.array(ds.variables["latc"][:])
        lon = np.array(ds.variables["lonc"][:])
        x = np.array(ds.variables["x"][:])
        y = np.array(ds.variables["y"][:])
    # Health check: legacy approx implies lat ≈ y/110574 within ~0.2 deg
    if abs(float(np.mean(lat)) - float(np.mean(y)) / 110574.0) < 0.2 and \
       100000.0 < float(np.mean(x)) < 900000.0:
        return None  # looks like a legit UTM grid
    # Find a matching .prj among persisted uploads
    for prj in sorted(_SHP_TEMP_DIR.glob("boundary_*/*.prj")):
        try:
            wkt_text = prj.read_text(encoding="utf-8", errors="ignore")
            src_crs = crs_utils.crs_from_wkt(wkt_text)
            if src_crs is None:
                continue
            tr = crs_utils.make_transformer(src_crs, crs_utils.WGS84)
            xg, yg = np.meshgrid(x, y)
            lon2, lat2 = tr.transform(xg, yg)
            if not (70.0 < np.nanmean(lon2) < 140.0 and 15.0 < np.nanmean(lat2) < 55.0):
                continue
            with nc_open(bathy_p, "a") as ds:
                ds.variables["latc"][:] = np.asarray(lat2, dtype="f8")
                ds.variables["lonc"][:] = np.asarray(lon2, dtype="f8")
            return (f"检测到 bathymetry.nc 经纬度与投影坐标不一致（旧版近似转换），"
                    f"已用边界 .prj ({src_crs.name}) 精确重投影修正")
        except Exception:
            continue
    return None


def _gen_fabm_init(case_path, preset):
    """Write fabm_init.nc with macrophytes fields scaled by depth.
    Returns the filename actually written: falls back to fabm_init_v2.nc
    when a crashed model run still holds a lock on fabm_init.nc."""
    bathy_p = case_path / "bathymetry.nc"
    with nc_open(bathy_p) as bds:
        x = np.array(bds.variables["x"][:])
        y = np.array(bds.variables["y"][:])
        lonc = np.array(bds.variables["lonc"][:])
        latc = np.array(bds.variables["latc"][:])
        depth = np.array(bds.variables["bathymetry"][:])
    sD_max = float(preset.get("macro_sD", 10.0))
    sD = np.zeros_like(depth)
    water = depth > 0
    shallow = water & (depth <= 4.0)
    mid = water & (depth > 4.0) & (depth < 8.0)
    sD[shallow] = sD_max
    sD[mid] = sD_max * (8.0 - depth[mid]) / 4.0
    _NC_LOCK.acquire()
    ds = None
    out = case_path / "fabm_init.nc"
    try:
        try:
            ds = nc.Dataset(str(out), "w", format="NETCDF4")
        except PermissionError:
            out = case_path / "fabm_init_v2.nc"
            ds = nc.Dataset(str(out), "w", format="NETCDF4")
        ny, nx = depth.shape
        ds.createDimension("x", nx); ds.createDimension("y", ny)
        xv = ds.createVariable("x", "f8", ("x",)); xv.units = "m"; xv[:] = x
        yv = ds.createVariable("y", "f8", ("y",)); yv.units = "m"; yv[:] = y
        lv = ds.createVariable("lonc", "f8", ("y", "x")); lv.units = "degrees_east"; lv[:] = lonc
        lt = ds.createVariable("latc", "f8", ("y", "x")); lt.units = "degrees_north"; lt[:] = latc
        for name, arr, unit, lname in (
                ("macrophytes_sD", sD, "gDW/m2", "macrophyte dry weight"),
                ("macrophytes_sN", sD * 0.02, "gN/m2", "macrophyte N"),
                ("macrophytes_sP", sD * 0.002, "gP/m2", "macrophyte P"),
                ("macrophytes_sC", sD * 0.40, "gC/m2", "macrophyte C")):
            # GETM's get_2d_field_ncdf_by_name reads plain 2D variables whose
            # Fortran field(i,j) maps to netCDF dims (y,x). A time dimension
            # here makes the rank mismatch and corrupts memory (crash after
            # init), so macrophytes must stay strictly 2D.
            v = ds.createVariable(name, "f8", ("y", "x"))
            v.units = unit; v.long_name = lname
            v[:] = arr
    finally:
        if ds is not None:
            try:
                ds.close()
            except Exception:
                pass
        _NC_LOCK.release()
    return out.name


def _build_getm_inp(case_path, case_name, start, stop, timestep, has_meteo, has_rivers, nlev):
    runid = re.sub(r"[^A-Za-z0-9_]", "_", case_name.upper())[:24] + "_WET"
    # river_method: 0=无河流, 1=恒定流量(全年只用首条记录!), 2=线性时间插值。
    # 滇池事故：method=1 导致盘龙江/海口河全年用 1月2日的流量。必须用 2。
    river_method = 2 if has_rivers else 0
    metforcing = ".true." if has_meteo else ".false."
    content = f"""! {case_name} - GETM-FABM-WET configuration (auto-built)
&param
   dryrun = '.false.'
   runid = '{runid}'
   title = '{case_name} GETM-FABM-WET'
   parallel = '.false.'
   runtype = 4
   hotstart = '.false.'
   use_epoch = '.false.'
   save_initial = '.false.'
/

&time
   timestep = {timestep}
   timefmt = 2
   start = '{start}'
   stop = '{stop}'
/

&domain
   vert_cord = 1
   maxdepth = 30.0
   bathy_format = 2
   bathymetry = 'bathymetry.nc'
   f_plane = '.true.'
   il = 1
   ih = 1
   jl = 1
   jh = 1
   crit_depth = 1.5
   min_depth = 0.5
   kdum = {nlev}
   z0_method = 0
   z0_const = 0.001
   check_cfl = '.false.'
/

&meteo
   metforcing = {metforcing}
   on_grid = '.true.'
   calc_met = '.true.'
   met_method = 2
   meteo_file = 'meteo_input.txt'
   fwf_method = 2
   tx = 0.0
   ty = 0.0
   swr_const = -100.0
   shf_const = 0.0
/

&rivers
   river_method = {river_method}
/

&m2d
   elev_method = 1
   elev_const = 0.0
   MM = 35
   vel2d_adv_split = 1
   vel2d_adv_hor = 1
   Am = 1.0
   An_method = 0
   An_const = 0.001
/

&m3d
   M = {nlev}
   cnpar = 1.0
   cord_relax = 0.1
   adv_ver_iterations = 1
   vel3d_adv_split = 1
   vel3d_adv_hor = 1
   vel3d_adv_ver = 1
   turb_adv_split = 1
   turb_adv_hor = 1
   turb_adv_ver = 1
   calc_temp = '.true.'
   calc_salt = '.false.'
   avmback = 1e-05
   avhback = 1e-06
   ip_method = 2
   ip_ramp = -1
   vel_check = 1
   min_vel = -10.0
   max_vel = 10.0
   bdy3d = '.false.'
   bdyfmt_3d = 1
   bdy3d_ramp = 0
   bdyfile_3d = ' '
   bdy3d_tmrlx = '.false.'
   bdy3d_tmrlx_ucut = 0.0
   bdy3d_tmrlx_max = 0.0
   bdy3d_tmrlx_min = 0.0
/

&temp
   temp_method = 1
   temp_const = 15.0
   temp_adv_split = 1
   temp_adv_hor = 1
   temp_adv_ver = 1
   temp_AH = -1.0
   attenuation_method = 0
   A_const = 0.6
   g1_const = 0.5
   g2_const = 20.0
   swr_bot_refl_frac = 0.0
   swr_min_bot_frac = 0.0
   temp_check = 0
   min_temp = -2.0
   max_temp = 40.0
/

&eqstate
   eqstate_method = 1
   T0 = 15.0
   S0 = 0.0
   p0 = 0.0
   dtr0 = 0.0002
   dsr0 = 0.0008
/

&io_spec
   out_fmt = 2
   hotin_fmt = 2
   hotout_fmt = 2
   save_metrics = '.false.'
   save_masks = '.false.'
   save_2d = '.true.'
   save_3d = '.true.'
   save_vel = '.true.'
   destag = '.false.'
   save_strho = '.true.'
   save_s = '.false.'
   save_t = '.true.'
   save_rho = '.false.'
   save_rad = '.false.'
   save_turb = '.true.'
   save_tke = '.true.'
   save_eps = '.true.'
   save_num = '.true.'
   save_nuh = '.true.'
   save_ss_nn = '.false.'
   save_taub = '.false.'
   first_2d = 1
   step_2d = 8640
   sync_2d = 8640
   first_3d = 1
   step_3d = 8640
   sync_3d = 8640
   save_meteo = '.false.'
   save_numerical_analyses = '.false.'
/

&getm_fabm
   fabm_config = 'fabm.yaml'
   fabm = '.true.'
/

&diagnostics
   diagnostics = '.false.'
/
"""
    # Fill real domain extents from bathymetry.nc
    with nc_open(case_path / "bathymetry.nc") as ds:
        nx = len(ds.dimensions["x"])
        ny = len(ds.dimensions["y"])
    content = content.replace("   ih = 1\n", f"   ih = {nx}\n")
    content = content.replace("   jh = 1\n", f"   jh = {ny}\n")
    (case_path / "getm.inp").write_text(content, encoding="utf-8")


@app.route("/api/case/build", methods=["POST"])
def case_build():
    global cached_getm_config, cached_fabm_info
    """One-click build of the complete case skeleton from bathymetry.nc.

    Body: {preset: 'mesotrophic'|'eutrophic'|'hypereutrophic',
           start: 'YYYY-MM-DD HH:MM:SS', stop: ..., timestep?: 15,
           nlev?: 10}
    Generates: getm.inp, getm_fabm.inp, gotm_fabm.yaml, gotmturb.nml,
    output.yaml, fabm.yaml (Luoma template + preset), fabm_init.nc,
    meteo_input.txt; and meteo.nc / rivers.nc when drafts exist.
    """
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    data = request.json or {}
    preset_key = data.get("preset", "eutrophic")
    preset = TROPHIC_PRESETS.get(preset_key)
    if preset is None:
        return jsonify({"error": f"未知预设 {preset_key}"}), 400
    start = (data.get("start") or "").strip()
    stop = (data.get("stop") or "").strip()
    if not start or not stop:
        return jsonify({"error": "请提供开始/结束时间"}), 400
    d0, d1 = _parse_date(start), _parse_date(stop)
    if d0 is None or d1 is None or d1 <= d0:
        return jsonify({"error": "时间格式错误或结束时间早于开始时间"}), 400
    timestep = int(data.get("timestep") or 15)
    nlev = int(data.get("nlev") or 10)
    # Engine selection made on the module page (before/without a case).
    # Falls back to the persisted draft, then to eco-on / ghg-off.
    engines = data.get("engines") or {}
    if not engines:
        engines = _load_module_selection()
    eco_selected = bool(engines.get("eco", True))
    fish_selected = bool(engines.get("fish", True)) and eco_selected
    ghg_selected = bool(engines.get("ghg", False))
    case_path = active_case_path
    if not (case_path / "bathymetry.nc").exists():
        return jsonify({"error": "缺少 bathymetry.nc（请先完成前处理）"}), 400
    _ensure_case_dirs(case_path)
    warnings = []
    notes = []
    # 0) repair legacy wrong coordinates
    geo_note = _fix_case_geo(case_path)
    if geo_note:
        notes.append(geo_note)
    # 1) meteo: promote draft if needed
    has_meteo = (case_path / "meteo_draft.json").exists() or (case_path / "meteo.nc").exists()
    if (case_path / "meteo_draft.json").exists() and not (case_path / "meteo.nc").exists():
        r1 = input_meteo_save()
        if r1.status_code != 200 or not r1.get_json().get("success"):
            return jsonify({"error": "生成 meteo.nc 失败"}), 500
    if not has_meteo:
        warnings.append("未配置气象数据：getm.inp 已设 metforcing=.false.（温度/风将使用常数，建议上传气象 CSV）")
    # 2) rivers: promote drafts
    meta = _load_case_meta() or {}
    has_rivers = bool(meta.get("rivers")) and (case_path / "river_drafts").exists() and \
        any((case_path / "river_drafts").glob("*.json"))
    if has_rivers:
        r2 = input_rivers_save()
        if r2.status_code != 200 or not r2.get_json().get("success"):
            warnings.append("河流数据不全，已按无河流配置（river_method=0）")
            has_rivers = False
    # 3) getm.inp
    _build_getm_inp(case_path, active_case, d0.strftime("%Y-%m-%d %H:%M:%S"),
                    d1.strftime("%Y-%m-%d %H:%M:%S"), timestep, has_meteo, has_rivers, nlev)
    # 4) fabm.yaml from the validated Luoma template + preset params
    template = BASE_DIR / "case" / "Lake Luoma" / "fabm.yaml"
    if not template.exists():
        return jsonify({"error": f"缺少模板 {template}"}), 500
    shutil.copy2(template, case_path / "fabm.yaml")
    params = []
    for key, val in preset.items():
        if key in ("label", "macro_sD"):
            continue
        mod, par = _PRESET_MODULE_MAP[key]
        params.append({"module": mod, "param": par, "value": float(val)})
    applied = update_fabm_parameter_batch(case_path / "fabm.yaml", params)
    # 4b) engine selection from the module page
    if not eco_selected:
        try:
            cfg = parse_getm_inp(case_path / "getm.inp")
            cfg.setdefault("getm_fabm", {})["fabm"] = ".false."
            write_getm_inp(case_path / "getm.inp", cfg)
        except Exception as e:
            warnings.append(f"写入 fabm=.false. 失败: {e}")
    # 4a) 鱼类（食物网顶层）——模板 fabm.yaml 本身不含鱼，按需注入/清除
    if (case_path / "fabm.yaml").exists():
        try:
            ok, fWarns = fish_support.toggle_fish_modules(
                case_path / "fabm.yaml", fish_selected)
            warnings.extend(fWarns)
            if not ok:
                eco_selected = eco_selected  # keep going;生态部分仍然可用
        except Exception as e:
            warnings.append(f"配置鱼类模块失败: {e}")
    if ghg_selected and (case_path / "fabm.yaml").exists():
        try:
            ok, gWarns = toggle_ghg_modules(case_path / "fabm.yaml", True)
            if not ok:
                warnings.extend(gWarns)
            else:
                cached_fabm_info = parse_fabm_yaml(case_path / "fabm.yaml")
                if _ghg_exe_is_stale() and _ghg_start_build():
                    warnings.append("温室气体模块已写入配置，正在后台编译，完成后自动部署新程序")
        except Exception as e:
            warnings.append(f"启用温室气体模块失败: {e}")
    notes.append(
        f"模块组合：水动力{'✓' if True else '✗'} · "
        f"水质生态{'✓' if eco_selected else '✗'} · "
        f"鱼类{'✓' if fish_selected else '✗'} · "
        f"温室气体{'✓' if ghg_selected else '✗'}")
    # 5) fabm_init.nc (may fall back to fabm_init_v2.nc when locked by a zombie process)
    init_name = _gen_fabm_init(case_path, preset)
    # 6) static config files
    (case_path / "getm_fabm.inp").write_text(
        "&getm_fabm_nml\n"
        " fabm_init_method   =  2,\n"
        f" fabm_init_file    =  '{init_name}',\n"
        " fabm_init_format  =  2,\n"
        " fabm_field_no     =  1,\n"
        " fabm_adv_hor      =  4,\n"
        " fabm_adv_ver      =  4,\n"
        " fabm_adv_split    =  1,\n"
        " fabm_AH           = -1.,\n"
        "/\n", encoding="utf-8")
    (case_path / "gotm_fabm.yaml").write_text(
        "fabm:\n"
        "  use: true\n"
        "  freshwater_impact: true\n"
        "  repair_state: true\n"
        "  feedbacks:\n"
        "    shade: true\n"
        "    albedo: true\n"
        "    surface_drag: true\n"
        "  numerics:\n"
        "    ode_method: 10\n"
        "    split_factor: 1\n"
        "    w_adv_discr: 6\n"
        "    cnpar: 1.0\n", encoding="utf-8")
    gotmturb = (BASE_DIR / "case" / "Lake Luoma" / "gotmturb.nml")
    if gotmturb.exists():
        shutil.copy2(gotmturb, case_path / "gotmturb.nml")
    (case_path / "output.yaml").write_text(
        "output:\n"
        "   time_unit: day\n"
        "   time_step: 1\n"
        "   sync_interval: 1\n"
        "   variables:\n"
        "      - source: *\n", encoding="utf-8")
    if not (case_path / "meteo_input.txt").exists():
        (case_path / "meteo_input.txt").write_text("meteo.nc\n", encoding="utf-8")
    # Refresh caches so the case list / config pages see the new files
    cached_getm_config = None
    cached_fabm_info = None
    notes.append(f"生态初值预设: {preset['label']}（{applied} 个参数已写入 fabm.yaml）")
    if not has_rivers:
        notes.append("未配置河流：river_method=0（之后在输入数据页配置河流会自动生效需重新构建）")
    # remember the trophic preset + module combo for the initial-conditions page
    try:
        sidecar = case_path / INIT_COND_FILE
        prev = {}
        if sidecar.exists():
            try:
                with open(sidecar, "r", encoding="utf-8") as f:
                    prev = json.load(f) or {}
            except Exception:
                prev = {}
        prev["trophic"] = preset_key
        prev["engines"] = {"hydro": True, "eco": eco_selected, "fish": fish_selected, "ghg": ghg_selected}
        with open(sidecar, "w", encoding="utf-8") as f:
            json.dump(prev, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    files = sorted(p.name for p in case_path.iterdir() if p.is_file())
    return jsonify({
        "success": True, "case_name": active_case,
        "preset": preset_key, "preset_label": preset["label"],
        "params_applied": applied, "warnings": warnings, "notes": notes,
        "engines": {"hydro": True, "eco": eco_selected, "fish": fish_selected, "ghg": ghg_selected},
        "files": files,
    })


# ── Local shell helpers: folder picker & Explorer ─────────────────────

PICKER_SCRIPT = APP_DIR / "pick_folder.ps1"
PICKER_RESULT = APP_DIR / ".picker_result.json"

_PICK_TK_LOCK = threading.Lock()
_PICK_TK_ROOT = None


class _TkUnavailable(Exception):
    """tkinter cannot create a window in this process/session."""


def _tk_pick_dir(start=""):
    """Show the native Windows folder dialog from *this* process.

    Runs tkinter directly (no child process), which is far more reliable than
    launching a hidden ``powershell.exe``: a WinForms dialog owned by a hidden
    window frequently never becomes visible.
    Returns the chosen path, or "" when the user cancels.
    """
    import tkinter as tk
    from tkinter import filedialog

    global _PICK_TK_ROOT
    with _PICK_TK_LOCK:
        try:
            if _PICK_TK_ROOT is None or not _PICK_TK_ROOT.winfo_exists():
                _PICK_TK_ROOT = tk.Tk()
            root = _PICK_TK_ROOT
        except Exception as e:  # TclError / ImportError / no display
            raise _TkUnavailable(str(e))
    # 保持主窗口 withdrawn：只让系统文件夹对话框自己显示，避免闪出一个 Tk 空窗口
    try:
        root.attributes("-topmost", True)
        root.lift()
        root.update()
    except Exception:
        pass
    kw = {"parent": root, "mustexist": False}
    if start and os.path.isdir(start):
        kw["initialdir"] = start
    try:
        path = filedialog.askdirectory(**kw)
    except Exception as e:
        raise _TkUnavailable(str(e))
    try:
        root.withdraw()
    except Exception:
        pass
    return path or ""


def _ps_pick_dir(start=""):
    """Fallback: folder dialog in a helper PowerShell process."""
    cmd = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
           "-Sta", "-File", str(PICKER_SCRIPT)]
    if start:
        cmd += ["-StartDir", start]
    subprocess.Popen(cmd, cwd=str(APP_DIR),
                     stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)
    # Block until the helper process writes and exits.
    for _ in range(600):
        time.sleep(0.5)
        if PICKER_RESULT.exists():
            break
    if not PICKER_RESULT.exists():
        return ""
    return PICKER_RESULT.read_text(encoding="utf-8", errors="replace").strip()


_PICK_LOG = APP_DIR / ".picker_debug.log"


def _pick_log(msg):
    try:
        with _PICK_LOG.open("a", encoding="utf-8") as fh:
            fh.write(f"{datetime.now():%H:%M:%S} {msg}\n")
    except Exception:
        pass


def _run_folder_picker(start):
    """Backend of the picker: write the result for the frontend to poll."""
    path, err, engine = "", "", "tkinter"
    _pick_log(f"picker start, start_dir={start!r}")
    try:
        path = _tk_pick_dir(start)
    except _TkUnavailable as e:
        _pick_log(f"tkinter unavailable: {e}")
        err = f"本机无法弹出系统窗口（{e}），已改用备用方式"
        engine = "powershell(回退)"
        try:
            path = _ps_pick_dir(start)
        except Exception as e2:
            _pick_log(f"powershell fallback failed: {e2}")
            err = f"启动文件夹选择窗口失败: {e2}"
    except Exception as e:  # noqa: BLE001
        _pick_log(f"picker crashed: {e!r}")
        err = f"文件夹选择窗口异常: {e}"
        engine = "none"
    _pick_log(f"picker done engine={engine} path={path!r} err={err!r}")
    try:
        PICKER_RESULT.write_text(
            json.dumps({"path": path, "error": err, "engine": engine,
                        "done": True}, ensure_ascii=False),
            encoding="utf-8")
    except Exception:
        pass


@app.route("/api/system/pick_folder", methods=["POST"])
def system_pick_folder():
    """Open a native Windows folder-picker dialog and return immediately.

    The dialog is shown by this very process (tkinter) inside a worker thread,
    the chosen path is written to app/.picker_result.json and picked up by the
    frontend via GET /api/system/pick_folder_result (poll loop in the browser).
    """
    data = request.json or {}
    start = str(data.get("start_dir") or "").strip().strip('"')
    try:
        PICKER_RESULT.unlink(missing_ok=True)
    except OSError:
        pass
    threading.Thread(target=_run_folder_picker, args=(start,),
                     daemon=True).start()
    return jsonify({"launched": True, "start_dir": start or None})


@app.route("/api/system/pick_folder_result")
def system_pick_folder_result():
    if not PICKER_RESULT.exists():
        return jsonify({"path": None, "done": False})
    try:
        txt = PICKER_RESULT.read_text(encoding="utf-8", errors="replace").strip()
    except Exception:
        return jsonify({"path": None, "done": False})
    try:
        PICKER_RESULT.unlink(missing_ok=True)
    except OSError:
        pass
    return jsonify({"path": txt or None, "done": True})


@app.route("/api/system/list_dir")
def system_list_dir():
    """List the sub-directories of `path` — a popup-free way of picking a case
    folder when the OS folder dialog cannot be shown (e.g. the browser runs
    the page inside an embedded webview)."""
    raw = str(request.args.get("path") or "").strip()
    if not raw:
        raw = str(Path.home())
    p = Path(raw)
    if not p.exists():
        return jsonify({"error": f"路径不存在: {raw}"}), 404
    if not p.is_dir():
        return jsonify({"error": f"不是目录: {raw}"}), 400
    entries = []
    try:
        for e in p.iterdir():
            name = e.name
            if name.startswith("."):
                continue
            try:
                entries.append({"name": name, "path": str(e), "is_dir": e.is_dir()})
            except OSError:
                continue
    except PermissionError:
        return jsonify({"error": f"没有权限访问: {raw}"}), 403
    entries.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
    parent = str(p.parent)
    if parent == str(p) or not parent:
        parent = ""
    return jsonify({"path": str(p), "parent": parent, "entries": entries})


@app.route("/api/system/explore", methods=["POST"])
def system_explore():
    """Reveal a directory (or file) in Windows Explorer with it selected."""
    data = request.json or {}
    raw = str(data.get("path") or "").strip().strip('"')
    if not raw:
        return jsonify({"error": "缺少 path"}), 400
    p = Path(raw)
    if not p.exists():
        return jsonify({"error": f"路径不存在: {p}"}), 404
    try:
        if p.is_dir():
            subprocess.Popen(["explorer", str(p)])
        else:
            subprocess.Popen(["explorer", "/select,", str(p)])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"success": True})


# ── Engine switches (hydrodynamics / water quality / GHG) ─────────────

@app.route("/api/config/engines")
def config_engines():
    """Big-grain model engine switches."""
    eco_enabled = None
    if active_case_path and (active_case_path / "getm.inp").exists():
        try:
            cfg = parse_getm_inp(active_case_path / "getm.inp")
            raw = cfg.get("getm_fabm", {}).get("fabm", ".true.")
            # parse_getm_inp already converts '.true.' to Python bool
            if isinstance(raw, bool):
                eco_enabled = raw
            else:
                eco_enabled = str(raw).strip().strip("'").lower() == ".true."
        except Exception:
            eco_enabled = None
    ghg_enabled = bool(active_case_path) and _ghg_case_enabled(active_case_path)
    return jsonify({
        "hydro": {"enabled": True, "fixed": True,
                  "label": "水动力（GETM 三维流动）",
                  "desc": "模型核心引擎，始终启用"},
        "eco": {"enabled": eco_enabled,
                "label": "水质生态（FABM-WET 食物网）",
                "desc": "浮游植物/浮游动物/鱼类/沉水植物/营养盐循环；关闭后仅运行物理水动力"},
        "ghg": {"enabled": ghg_enabled,
                "available": True,
                "label": "温室气体（CO₂/CH₄）",
                "desc": "无机碳（DIC/碱度/pH/CO₂ 空气-水交换）+ 甲烷（产生/氧化/冒泡/排放）；启用后闭合碳循环，程序未含模块时自动编译",
                "exe_has_ghg": not _ghg_exe_is_stale(),
                "building": ghg_build_state["running"],
                "build_ok": ghg_build_state["ok"]},
    })


@app.route("/api/config/engines", methods=["POST"])
def config_engines_set():
    """Toggle the eco (water-quality) engine: rewrites &getm_fabm/fabm in getm.inp."""
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    inp_path = active_case_path / "getm.inp"
    if not inp_path.exists():
        return jsonify({"error": "getm.inp 不存在（请先构建案例）"}), 400
    data = request.json or {}
    if "eco" not in data:
        return jsonify({"error": "缺少 eco 参数"}), 400
    eco = bool(data["eco"])
    config = parse_getm_inp(inp_path)
    if "getm_fabm" not in config:
        config["getm_fabm"] = {}
    config["getm_fabm"]["fabm"] = ".true." if eco else ".false."
    write_getm_inp(inp_path, config)
    return jsonify({"success": True, "eco": eco})


# ── Module selection (works with or without an active case) ───────────

MODULE_SELECTION_FILE = APP_DIR / ".module_selection.json"
MODULE_SELECTION_DEFAULT = {"hydro": True, "eco": True, "fish": True, "ghg": False}

ENGINE_CATALOG = {
    "hydro": {
        "key": "hydro", "label": "水动力", "icon": "🌊",
        "long_name": "水动力（GETM 三维流动）",
        "desc": "湖泊三维水动力内核：投影正交曲线网格、sigma 垂向坐标、外模/内模分离求解水位与三维流场。任何案例都必须启用，无法关闭。",
        "fixed": True,
    },
    "eco": {
        "key": "eco", "label": "水质生态", "icon": "🦠",
        "long_name": "水质生态（FABM-WET 食物网）",
        "desc": "浮游植物（蓝藻/硅藻/绿藻）、浮游动物、底栖动物、沉水植物、碎屑与营养盐循环。关闭后仅运行物理水动力，生态变量不再计算。",
        "fixed": False,
    },
    "fish": {
        "key": "fish", "label": "鱼类", "icon": "🐟",
        "long_name": "鱼类（食物网顶层捕食者）",
        "desc": "三个湿重/干重状态量实例：JuFish 浮游食性幼鱼（捕食浮游动物）、AdFish 底栖食性成鱼（捕食底栖动物、扰动沉积物）、PiscFish 食鱼性鱼（捕食前两者）。"
                "缺了它食物网就只有「藻→浮游动物→底栖动物」而缺少顶层下行控制（top-down control），生物操纵/鱼类控藻情景无法模拟。"
                "模块已编译在程序中，只是历史配置被摘除，启用无需重新编译。",
        "fixed": False,
    },
    "ghg": {
        "key": "ghg", "label": "温室气体", "icon": "🌫️",
        "long_name": "温室气体（CO₂ / CH₄）",
        "desc": "无机碳（DIC/碱度/pH/pCO₂ 与空气-水 CO₂ 通量）+ 甲烷（产生/氧化/冒泡/排放）。启用后闭合碳循环，若当前执行程序未含该模块会自动编译。",
        "fixed": False,
    },
}

# 鱼类模块默认随生态模块一起开启：食物网缺顶层捕食者是不完整的
MODULE_ENGINE_KEYS = ("hydro", "eco", "fish", "ghg")


def _load_module_selection():
    """Module toggles kept outside any case so they can be set before a case
    exists (used by the pre-process 'new model' and the module page)."""
    sel = dict(MODULE_SELECTION_DEFAULT)
    try:
        if MODULE_SELECTION_FILE.exists():
            with open(MODULE_SELECTION_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
            if isinstance(d, dict):
                for k in MODULE_ENGINE_KEYS:
                    if isinstance(d.get(k), bool):
                        sel[k] = d[k]
    except Exception:
        pass
    return sel


def _save_module_selection(sel):
    try:
        MODULE_SELECTION_FILE.write_text(
            json.dumps({k: bool(sel.get(k, False)) for k in MODULE_ENGINE_KEYS},
                       ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    except Exception:
        return False


def _case_eco_enabled(case_path):
    """True/False from getm.inp, or None when getm.inp/fabm switch is absent."""
    inp = case_path / "getm.inp"
    if not inp.exists():
        return None
    try:
        cfg = parse_getm_inp(inp)
        raw = cfg.get("getm_fabm", {}).get("fabm", None)
        if raw is None:
            return None
        if isinstance(raw, bool):
            return raw
        return str(raw).strip().strip("'").lower() == ".true."
    except Exception:
        return None


@app.route("/api/config/modules", methods=["GET"])
def config_modules_get():
    """Full module/engine catalogue.

    Works with **no case loaded**: falls back to the persisted draft
    selection (app/.module_selection.json) so the user can decide which
    engines a new model will use before creating it.
    """
    sel = _load_module_selection()
    has_case = bool(active_case_path)
    source = "draft"
    if has_case:
        eco_real = _case_eco_enabled(active_case_path)
        if eco_real is not None:
            sel["eco"] = eco_real
            source = "case"
        if (active_case_path / "fabm.yaml").exists():
            sel["ghg"] = _ghg_case_enabled(active_case_path)
            sel["fish"] = _fish_case_enabled(active_case_path)
            source = "case"
    engines = []
    for key in MODULE_ENGINE_KEYS:
        info = dict(ENGINE_CATALOG[key])
        info["enabled"] = bool(sel.get(key, False))
        info["available"] = True
        if key == "hydro":
            info["enabled"] = True
            info["fixed"] = True
        if key == "fish":
            # fish requires a food web to feed on
            eco_on = bool(sel.get("eco", True))
            info["available"] = eco_on
            if not eco_on:
                info["enabled"] = False
            info["exe_has_fish"] = True  # always compiled into the exe
        if key == "ghg":
            info["available"] = True
            info["exe_has_ghg"] = not _ghg_exe_is_stale()
            info["building"] = ghg_build_state["running"]
        engines.append(info)
    payload = {
        "has_case": has_case,
        "source": source,
        "selection": {k: bool(sel.get(k, False)) for k in MODULE_ENGINE_KEYS},
        "engines": engines,
    }
    if has_case and (active_case_path / "fabm.yaml").exists():
        try:
            info = parse_fabm_yaml(active_case_path / "fabm.yaml")
            payload["modules"] = info.get("modules", [])
            payload["categories"] = info.get("categories", {})
        except Exception:
            pass
    return jsonify(payload)


@app.route("/api/config/modules", methods=["POST"])
def config_modules_set():
    """Apply the engine selection.

    The draft is always saved (so a future new model inherits it); when a
    case is active the choice is additionally written into that case
    (getm.inp + fabm.yaml, GHG triggers a rebuild when needed).
    """
    global cached_fabm_info
    data = request.json or {}
    # Start from the *currently effective* selection, not the factory default,
    # so toggling one engine never silently flips the others (which used to
    # strip the GHG modules out of a loaded case's fabm.yaml).
    sel = dict(_load_module_selection())
    if active_case_path:
        eco_real = _case_eco_enabled(active_case_path)
        if eco_real is not None:
            sel["eco"] = eco_real
        try:
            sel["ghg"] = bool(_ghg_case_enabled(active_case_path))
            sel["fish"] = bool(_fish_case_enabled(active_case_path))
        except Exception:
            pass
    for k in MODULE_ENGINE_KEYS:
        if k in data:
            sel[k] = bool(data[k])
    if "hydro" in data and data["hydro"]:
        sel["hydro"] = True  # hydrodynamics is mandatory
    # Fish sits on top of the food web: no ecology module -> no fish
    if not sel.get("eco", True):
        sel["fish"] = False
    _save_module_selection(sel)

    result = {"success": True, "saved_draft": True, "selection": sel,
              "warnings": [], "applied": [], "applied_to": None}
    if not active_case_path:
        result["source"] = "draft"
        return jsonify(result)

    result["applied_to"] = active_case
    inp = active_case_path / "getm.inp"
    if sel["eco"] and inp.exists():
        try:
            config = parse_getm_inp(inp)
            if "getm_fabm" not in config:
                config["getm_fabm"] = {}
            config["getm_fabm"]["fabm"] = ".true." if sel["eco"] else ".false."
            write_getm_inp(inp, config)
            result["applied"].append("getm.inp: getm_fabm/fabm")
        except Exception as e:
            result["warnings"].append(f"写入 getm.inp 失败: {e}")
    fabm_path = active_case_path / "fabm.yaml"
    if fabm_path.exists() and sel.get("fish") is not None and sel.get("eco", True):
        try:
            ok, warns = fish_support.toggle_fish_modules(fabm_path, bool(sel["fish"]))
            result["warnings"].extend(warns)
            if not ok:
                result["success"] = False
            else:
                result["applied"].append(
                    "fabm.yaml: " + "/".join(fish_support.FISH_INSTANCES)
                    + ("（已启用）" if sel["fish"] else "（已移除）"))
                cached_fabm_info = parse_fabm_yaml(fabm_path)
        except Exception as e:
            result["success"] = False
            result["warnings"].append(f"写入鱼类模块失败: {e}")
    if fabm_path.exists() and sel.get("ghg") is not None:
        try:
            ok, warns = toggle_ghg_modules(fabm_path, bool(sel["ghg"]))
            if not ok:
                result["success"] = False
                result["warnings"].extend(warns)
                return jsonify(result)
            result["applied"].append("fabm.yaml: inorganic_carbon/methane")
            cached_fabm_info = parse_fabm_yaml(fabm_path)
            if sel["ghg"] and _ghg_exe_is_stale():
                if _ghg_start_build():
                    result["warnings"].append("温室气体模块正在后台编译，完成后自动部署新程序")
                else:
                    result["warnings"].append("温室气体模块编译已在进行中")
        except Exception as e:
            result["warnings"].append(f"写入 fabm.yaml 失败: {e}")
    try:
        global cached_getm_config
        cached_getm_config = parse_getm_inp(inp) if inp.exists() else {}
    except Exception:
        pass
    result["sources"] = ["draft", "case"]
    return jsonify(result)


# ── Initial conditions (water level / temperature / water quality) ────

INIT_COND_FILE = "initial_conditions.json"
INIT_COND_DEFAULT = {"surface_elev_abs": None, "datum_abs": None,
                     "trophic": None, "macrophytes": None}


def _load_init_cond():
    p = active_case_path / INIT_COND_FILE
    out = dict(INIT_COND_DEFAULT)
    if p.exists():
        try:
            with open(p, "r", encoding="utf-8") as f:
                d = json.load(f)
            if isinstance(d, dict):
                out.update({k: v for k, v in d.items() if v is not None})
        except Exception:
            pass
    return out


def _bathy_stats(case_path):
    p = case_path / "bathymetry.nc"
    if not p.exists():
        return None
    try:
        with nc_open(p) as ds:
            b = np.ma.filled(ds.variables["bathymetry"][:], np.nan)
        w = b[b > 0]
        return {"min_depth": float(np.min(w)) if w.size else None,
                "max_depth": float(np.max(w)) if w.size else None,
                "mean_depth": float(np.mean(w)) if w.size else None,
                "n_water": int(w.size)}
    except Exception:
        return None


def _detect_trophic(initialization):
    """Match the current water-quality initial values against the presets."""
    best, best_score = "custom", None
    for key, preset in TROPHIC_PRESETS.items():
        score = 0.0
        for f in ("sNH4W", "sNO3W", "sPO4W", "sO2W", "sSiO2W",
                  "diatoms_sDW", "greens_sDW", "cyanobacteria_sDW"):
            cur = initialization.get(f)
            ref = preset.get(f)
            if cur is None or not ref:
                continue
            a, b = float(cur), float(ref)
            score += ((a - b) / max(b, 1e-9)) ** 2
        if best_score is None or score < best_score:
            best, best_score = key, score
    return best if (best_score is not None and best_score < 1e-3) else "custom"


@app.route("/api/case/init_conditions", methods=["GET"])
def case_init_conditions_get():
    """Initial state of the run: water level, temperature, water quality."""
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    case_path = active_case_path
    inp = case_path / "getm.inp"
    cfg = parse_getm_inp(inp) if inp.exists() else {}
    side = _load_init_cond()
    bathy = _bathy_stats(case_path)

    m2d = cfg.get("m2d", {}) or {}
    temp = cfg.get("temp", {}) or {}
    hydro = {
        "elev_const": m2d.get("elev_const", 0.0),
        "temp_const": temp.get("temp_const", 15.0),
        "surface_elev_abs": side.get("surface_elev_abs"),
        "datum_abs": side.get("datum_abs"),
        "hotstart": bool((cfg.get("param", {}) or {}).get("hotstart", False)),
    }
    if hydro["surface_elev_abs"] is not None and hydro["datum_abs"] is not None:
        hydro["elev_const_abs"] = round(float(hydro["surface_elev_abs"]) - float(hydro["datum_abs"]), 4)

    modules, initialization = [], {}
    fabm_path = case_path / "fabm.yaml"
    if fabm_path.exists():
        try:
            with open(fabm_path, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f) or {}
            raw = json.loads(json.dumps(raw, default=str))
            for name, inst in (raw.get("instances") or {}).items():
                if not isinstance(inst, dict):
                    continue
                init = inst.get("initialization") or {}
                if not isinstance(init, dict) or not init:
                    continue
                init = {k: v for k, v in init.items()
                        if isinstance(v, (int, float)) and not isinstance(v, bool)}
                if not init:
                    continue
                initialization[name] = init
                meta = MODULE_CATEGORIES.get(name, {})
                modules.append({
                    "name": name,
                    "long_name": inst.get("long_name", name),
                    "category": meta.get("category", "其他"),
                    "color": meta.get("color", "#64748b"),
                    "model": inst.get("model", ""),
                    "n_init": len(init),
                    "init": init,
                    "desc": _fabm_docs().get("modules", {}).get(name, ""),
                    "docs": {k: _annotate_variable(inst.get("model", ""), k)
                             for k in init},
                })
        except Exception as e:
            return jsonify({"error": f"解析 fabm.yaml 失败: {e}"}), 500
    modules.sort(key=lambda m: (m["category"], m["name"]))

    trophic = side.get("trophic")
    if initialization:
        flat = {}
        for m, d in initialization.items():
            flat.update(d)
        if not trophic:
            trophic = _detect_trophic(flat)

    # macrophyte biomass currently written into fabm_init.nc
    macro_sD = None
    for fn in ("fabm_init.nc", "fabm_init_v2.nc"):
        fp = case_path / fn
        if fp.exists():
            try:
                with nc_open(fp) as ds:
                    if "macrophytes_sD" in ds.variables:
                        macro_sD = float(np.nanmax(
                            np.ma.filled(ds.variables["macrophytes_sD"][:], np.nan)))
                break
            except Exception:
                pass

    return jsonify({
        "case_name": active_case,
        "hydro": hydro,
        "trophic": trophic,
        "trophic_presets": {k: v.get("label") for k, v in TROPHIC_PRESETS.items()},
        "modules": modules,
        "macrophytes": {"sD_max": side.get("macrophytes") if side.get("macrophytes") is not None else macro_sD,
                        "sD_from_nc": macro_sD},
        "bathymetry": bathy,
        "preset_values": {k: {kk: vv for kk, vv in v.items()}
                          for k, v in TROPHIC_PRESETS.items()} if trophic in TROPHIC_PRESETS else {},
    })


@app.route("/api/case/init_conditions", methods=["POST"])
def case_init_conditions_set():
    """Apply initial conditions and persist them for future rebuilds."""
    global cached_getm_config
    if not active_case_path:
        return jsonify({"error": "未加载案例"}), 400
    case_path = active_case_path
    data = request.json or {}
    hydro_in = data.get("hydro") or {}
    notes, warnings = [], []

    # ── 1) water level & temperature → getm.inp ──────────────────────
    inp = case_path / "getm.inp"
    side = _load_init_cond()
    elev = hydro_in.get("elev_const")
    surface_abs = hydro_in.get("surface_elev_abs")
    datum_abs = hydro_in.get("datum_abs")
    if surface_abs not in (None, "") and datum_abs not in (None, ""):
        elev = float(surface_abs) - float(datum_abs)
        side["surface_elev_abs"] = float(surface_abs)
        side["datum_abs"] = float(datum_abs)
        notes.append(f"水位换算：湖面绝对高程 {surface_abs} m − 地形基准面 {datum_abs} m "
                     f"→ elev_const = {elev:.4f} m")
    elif elev is not None and elev != "":
        elev = float(elev)
        side.pop("surface_elev_abs", None)
        side.pop("datum_abs", None)
    if elev is not None and elev != "" and inp.exists():
        try:
            config = parse_getm_inp(inp)
            config.setdefault("m2d", {})["elev_const"] = float(elev)
            write_getm_inp(inp, config)
            global cached_getm_config
            cached_getm_config = parse_getm_inp(inp)
            notes.append(f"getm.inp 已写入 m2d/elev_const = {float(elev):.4f} m")
        except Exception as e:
            warnings.append(f"写入 getm.inp 失败: {e}")
    temp_const = hydro_in.get("temp_const")
    if temp_const not in (None, "") and inp.exists():
        try:
            config = parse_getm_inp(inp)
            config.setdefault("temp", {})["temp_const"] = float(temp_const)
            write_getm_inp(inp, config)
            cached_getm_config = parse_getm_inp(inp)
            notes.append(f"getm.inp 已写入 temp/temp_const = {float(temp_const):.2f} ℃")
        except Exception as e:
            warnings.append(f"写入 getm.inp 失败: {e}")

    # ── 2) water quality initial values → fabm.yaml ──────────────────
    wq = data.get("water_quality") or {}
    fabm_path = case_path / "fabm.yaml"
    n_written = 0
    if wq and fabm_path.exists():
        try:
            with open(fabm_path, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f) or {}
            instances = raw.get("instances") or {}
            for key, val in wq.items():
                mod, _, par = str(key).partition(".")
                if mod not in instances or not isinstance(instances[mod], dict):
                    continue
                inst = instances[mod]
                block = inst.get("initialization")
                if not isinstance(block, dict):
                    block = {}
                    inst["initialization"] = block
                try:
                    block[par] = float(val)
                    n_written += 1
                except (TypeError, ValueError):
                    continue
            with open(fabm_path, "w", encoding="utf-8") as f:
                yaml.dump(raw, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            if n_written:
                notes.append(f"fabm.yaml 已更新 {n_written} 个水质初始条件")
        except Exception as e:
            warnings.append(f"写入 fabm.yaml 失败: {e}")

    trophic = data.get("trophic")
    if trophic in TROPHIC_PRESETS:
        side["trophic"] = trophic
        if n_written == 0:
            # values were already in place; nothing else to do
            pass
    elif not trophic:
        side.pop("trophic", None)

    # ── 3) macrophyte biomass → fabm_init.nc ──────────────────────────
    macro = data.get("macrophytes")
    if isinstance(macro, dict) and macro.get("sD_max") not in (None, ""):
        sD_max = float(macro["sD_max"])
        side["macrophytes"] = sD_max
        try:
            init_name = _gen_fabm_init(case_path, {**TROPHIC_PRESETS.get(
                side.get("trophic") or "eutrophic", TROPHIC_PRESETS["eutrophic"]),
                "macro_sD": sD_max})
            notes.append(f"已重新生成生态初值文件 {init_name}（沉水植物生物量上限 {sD_max:.2f} gDW/m²）")
        except Exception as e:
            warnings.append(f"重新生成 fabm_init.nc 失败: {e}")

    # Persist the side-car (absolute elevation / trophic preset / macro)
    try:
        with open(case_path / INIT_COND_FILE, "w", encoding="utf-8") as f:
            json.dump({k: v for k, v in side.items() if v is not None},
                      f, ensure_ascii=False, indent=2)
    except Exception as e:
        warnings.append(f"保存初始条件元数据失败: {e}")

    return jsonify({"success": True, "n_written": n_written,
                    "notes": notes, "warnings": warnings})


# ── Main ───────────────────────────────────────────────────────────────

def _reattach_orphan_model():
    """Detect a getm_cartesian.exe still running from a previous service
    instance (the exe outlives the service that spawned it) and re-attach:
    keeps run_status='running' so the dashboard 409 guard (HDF5 concurrent
    access) and the delete/save-as guards stay effective, and clears the
    status when the exe exits. Must be called once at service startup."""
    global run_status, run_case_path, run_start_time
    try:
        import psutil
        procs = [p for p in psutil.process_iter(["name", "pid", "create_time"])
                 if (p.info["name"] or "").lower() == "getm_cartesian.exe"]
    except Exception:
        return
    if not procs:
        return
    p = procs[0]
    run_status = "running"
    try:
        run_start_time = p.info["create_time"]
    except Exception:
        run_start_time = time.time()
    # Locate the running case: the known case whose model_run.log was
    # touched most recently (the exe appends stderr continuously).
    candidates = []
    try:
        dirs = [d for d in CASE_DIR.iterdir() if d.is_dir()] + \
               [Path(p) for p in _load_external_cases()]
        for case_dir in dirs:
            log = case_dir / "model_run.log"
            if log.exists():
                candidates.append((log.stat().st_mtime, case_dir))
    except Exception:
        pass
    if candidates:
        candidates.sort(reverse=True)
        if time.time() - candidates[0][0] < 600:
            run_case_path = candidates[0][1]
            print(f"[启动] 检测到运行中的模型 (PID {p.info['pid']}, 案例 {run_case_path.name})，已恢复运行状态")
        else:
            print(f"[启动] 检测到运行中的模型进程 (PID {p.info['pid']})，已恢复运行状态")
    else:
        print(f"[启动] 检测到运行中的模型进程 (PID {p.info['pid']})，已恢复运行状态")

    def _watch(pid):
        global run_status, run_case_path
        while True:
            time.sleep(30)
            try:
                import psutil
                psutil.Process(pid)
            except Exception:
                run_status = "completed"
                run_case_path = None
                return

    threading.Thread(target=_watch, args=(p.info["pid"],), daemon=True).start()

def main():
    _reattach_orphan_model()
    # WET_PORT 环境变量可覆盖端口（自动化测试用 8767 避免占用用户的 8766）
    PORT = int(os.environ.get("WET_PORT", "8766"))
    url = f"http://localhost:{PORT}/"
    print("=" * 60)
    print("  3DWET 生态水动力模型 Web 系统")
    print("=" * 60)
    print(f"  服务地址: {url}")
    print("  请在浏览器中打开上述地址")
    print("  关闭此窗口将停止服务")
    print("=" * 60)
    try:
        import sys
        sys.path.insert(0, str(APP_DIR / "libs"))
        from waitress import serve
        print("  使用 Waitress 生产级服务器 (4线程)")
        serve(app, host="127.0.0.1", port=PORT, threads=4)
    except ImportError as e:
        print(f"  Waitress不可用({e})，使用 Flask 开发服务器")
        app.run(host="127.0.0.1", port=PORT, debug=False, threaded=False)

if __name__ == "__main__":
    main()
