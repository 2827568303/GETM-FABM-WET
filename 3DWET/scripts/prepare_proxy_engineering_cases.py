"""Create an append-only, provenance-labelled four-lake proxy attempt."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

import yaml


ERKEN_SOURCE = Path("build/real-use-validation-20261021/erken-real-location-24h/baseline")
RAVN_ARCHIVE = Path("build/source-research-au-cases-20261027/testcase_Lake_Ravn.zip")
WET_ROOT = Path("3DWET/src/wet/testcases")
ERKEN_FILES = (
    "bathymetry.nc", "fabm.yaml", "fabm_init.nc", "getm.inp", "getm_fabm.inp",
    "gotm_fabm.yaml", "gotmturb.nml", "meteo.nc", "meteo_input.txt", "output.yaml",
    "initial_conditions.json", "meteo_provenance.json", "rivers_setup.json",
    "Input/Erken_TW_profile_2020-01-01_hourly.txt",
)
WET_FILES = {
    "Bryrup": ("lake_bryrup_denmark", (
        "fabm.yaml", "gotm.yaml", "hypsograph.dat", "inflow_chem.dat", "inflow.dat",
        "meteo_file.dat", "outflow.dat", "output.yaml")),
    "Arreskov": ("lake_arreskov_denmark", (
        "ERA5_meteo_file_arreskov.dat", "gotm.yaml", "hypsograph.dat",
        "inflow_chem_adj.dat", "inflow_chem_SiO2.dat", "inflow.dat",
        "manipulations.nml", "meteo_file.dat", "outflow.dat", "output.yaml",
        "README.md", "waterlevel.dat")),
}
LAKE_SLUGS = {"Erken": "erken", "Lake Ravn": "lake-ravn", "Bryrup": "bryrup", "Arreskov": "arreskov"}
RUNTIME_FILES = (
    ("bathymetry.nc", "GETM bathymetry and spatial grid"),
    ("fabm.yaml", "case-specific FABM configuration"),
    ("fabm_init.nc", "case-specific FABM initial state"),
    ("getm.inp", "GETM run configuration"),
    ("getm_fabm.inp", "GETM-FABM coupling configuration"),
    ("gotmturb.nml", "GETM turbulence configuration"),
    ("meteo.nc", "GETM meteorology input"),
    ("output.yaml", "GETM output configuration"),
)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _copy(repo: Path, case: Path, source: Path, rel_dest: Path, *, role: str,
          purpose: str, description: str) -> dict:
    src = (repo / source).resolve()
    if not src.is_file() or src.is_symlink():
        raise FileNotFoundError(src)
    dest = case / rel_dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    return {"path": rel_dest.as_posix(), "bytes": dest.stat().st_size,
            "sha256": _sha256(dest), "role": role, "status": "copied_source",
            "purpose": purpose, "source_description": description,
            "origin_path": source.as_posix()}


def _missing(name: str, purpose: str, search: str) -> dict:
    return {"path": f"missing/{name}", "role": "missing", "status": "missing",
            "purpose": purpose,
            "source_description": "未找到可直接用于当前 GETM 3D 运行的源文件；保留为未完成项。",
            "origin_search": search}


def _case_record(repo: Path, case: Path, lake: str) -> dict:
    sources, blockers = [], []
    geometry_status = forcing_status = "missing"
    if lake == "Erken":
        desc = "既有 Erken 24h 工程代理包的逐文件隔离副本；不包含历史输出或旧日志。"
        for name in ERKEN_FILES:
            try:
                sources.append(_copy(repo, case, ERKEN_SOURCE / name, Path(name),
                                     role="derived", purpose=f"Erken工程代理输入：{name}",
                                     description=desc))
            except FileNotFoundError:
                sources.append(_missing(name, f"Erken输入 {name}", ERKEN_SOURCE.as_posix()))
        missing_runtime = [name for name, _ in RUNTIME_FILES
                           if not (case / name).is_file()]
        if missing_runtime:
            blockers.append("缺少当前 GETM 运行必需文件：" + ", ".join(missing_runtime))
        # The recorded input package configures river_method=0, so absence of
        # river boundary files is intentional and is checked by the validator.
        getm = case / "getm.inp"
        if getm.is_file() and "river_method = 0" not in getm.read_text(encoding="utf-8", errors="replace").lower():
            blockers.append("当前输入未明确禁用河流边界，且未提供映射后的河流文件。")
        geometry_status = "derived" if (case / "bathymetry.nc").is_file() else "missing"
        forcing_status = "derived" if (case / "meteo.nc").is_file() else "missing"
        if not any(item.startswith("缺少当前 GETM") or item.startswith("当前输入") for item in blockers):
            geometry_status = "proxy"
            forcing_status = "proxy"
    elif lake == "Lake Ravn":
        try:
            sources.append(_copy(repo, case, RAVN_ARCHIVE, Path("sources/testcase_Lake_Ravn.zip"),
                                 role="upstream_reference", purpose="Ravn上游1D GOTM案例归档",
                                 description="本地 source-research 案例ZIP；不是GETM空间运行包。"))
        except FileNotFoundError:
            sources.append(_missing("testcase_Lake_Ravn.zip", "Ravn上游案例归档", RAVN_ARCHIVE.as_posix()))
        blockers.extend([
            "仅发现上游1D GOTM案例；缺少 GETM 空间网格、FABM初始化、3D强迫与可用运行配置。",
            "未生成或验证由 hypsograph 推导的 synthetic_proxy 网格/强迫输入。",
        ])
    else:
        directory, filenames = WET_FILES[lake]
        source_dir = WET_ROOT / directory
        for filename in filenames:
            try:
                sources.append(_copy(repo, case, source_dir / filename,
                                     Path("sources") / filename, role="upstream_reference",
                                     purpose=f"{lake}上游WET/GOTM参考输入：{filename}",
                                     description="保留原文件供溯源；未经转换，不作为GETM 3D空间输入。"))
            except FileNotFoundError:
                sources.append(_missing(filename, f"{lake}上游文件 {filename}", source_dir.as_posix()))
        blockers.extend([
            "已有材料为上游WET/GOTM 1D输入；缺少GETM空间网格、FABM初始化与应用级3D运行配置。",
            "未生成或验证明确标记为 synthetic_proxy 的空间网格与均匀强迫输入。",
        ])
        if lake == "Arreskov":
            blockers.append("未发现Arreskov专属 fabm.yaml；不借用其他湖泊的生态配置。")

    # Non-Erken cases keep a complete inventory of required runtime gaps.
    if lake != "Erken":
        for name, purpose in RUNTIME_FILES:
            sources.append(_missing(name, purpose, lake))
        geometry_status, forcing_status = "missing", "missing"
    prepared = lake == "Erken" and not blockers and not any(s["role"] == "missing" for s in sources)
    return {"schema_version": 1, "kind": "engineering_proxy", "target_lake": lake,
            "validation_status": "not_scientifically_validated", "prepared": prepared,
            "geometry": {"status": geometry_status,
                         "description": "Erken隔离来源包中的空间浴深输入，仅供工程运行；并非本轮科学验证。"
                         if lake == "Erken" else "上游资料可审计，但本attempt未创建GETM空间几何。"},
            "forcing": {"status": forcing_status,
                        "description": "Erken隔离来源包中的气象输入，仅供工程运行；并非本轮科学验证。"
                        if lake == "Erken" else "本attempt未创建GETM 3D强迫。"},
            "sources": sources, "blockers": blockers}


def _enable_proxy_meteorology(case: Path, manifest: dict) -> None:
    """Enable the existing NetCDF meteo source in an isolated Erken copy only."""
    config = case / "getm.inp"
    text = config.read_text(encoding="utf-8")
    updated, count = re.subn(
        r"(?im)^(\s*metforcing\s*=\s*)\.false\.(\s*(?:!.*)?)$",
        r"\1.true.\2", text)
    if count != 1:
        raise ValueError(f"expected exactly one metforcing=.false. in {config}, got {count}")
    if not (case / "meteo.nc").is_file() or not (case / "meteo_input.txt").is_file():
        raise FileNotFoundError("Erken meteo.nc and meteo_input.txt are both required")
    config.write_text(updated, encoding="utf-8", newline="")
    source = next(item for item in manifest["sources"] if item["path"] == "getm.inp")
    source.update({"bytes": config.stat().st_size, "sha256": _sha256(config),
                   "purpose": "工程代理运行配置；仅将 metforcing 改为 true 以读取现有 meteo.nc。"})
    provenance_path = case / "meteo_provenance.json"
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    spatial = provenance.get("spatial", {})
    manifest["forcing"].update({
        "status": "proxy",
        "description": "使用已有站点气象输入并均匀广播至网格；工程代理强迫，confirmed=false，不代表空间实测验证。",
        "spatial_mode": spatial.get("mode"),
        "confirmed": spatial.get("confirmed", False),
        "source_distance_km": spatial.get("distance_km"),
    })
    manifest["engineering_adjustments"] = [{
        "path": "getm.inp", "setting": "metforcing", "from": ".false.", "to": ".true.",
        "reason": "getm.inp otherwise ignores the present meteo.nc; this enables the existing single-station uniform-broadcast forcing for an engineering run.",
        "scientific_validation": "not_scientifically_validated",
        "forcing_confirmed": spatial.get("confirmed", False),
    }]


def create_partial_ghg_off_proxy(source_case: Path, output_case: Path) -> dict:
    """Create an isolated Erken copy with only the two GHG FABM instances removed."""
    source, target = Path(source_case).resolve(), Path(output_case).resolve()
    if target.exists():
        raise FileExistsError(f"refusing to overwrite partial proxy case: {target}")
    source_manifest_path = source / "proxy_engineering.json"
    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    if source_manifest.get("target_lake") != "Erken" or source_manifest.get("prepared") is not True:
        raise ValueError("partial GHG-off preparation requires a prepared Erken engineering proxy")
    source_fabm = yaml.safe_load((source / "fabm.yaml").read_text(encoding="utf-8")) or {}
    source_instances = source_fabm.get("instances")
    if not isinstance(source_instances, dict) or not {"inorganic_carbon", "methane"}.issubset(source_instances):
        raise ValueError("source Erken case must contain both GHG instances")

    target.mkdir(parents=True, exist_ok=False)
    for item in source_manifest.get("sources", []):
        if item.get("role") == "missing":
            continue
        rel = Path(*item["path"].replace("\\", "/").split("/"))
        src, dst = source / rel, target / rel
        if not src.is_file():
            raise FileNotFoundError(src)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)

    fabm_path = target / "fabm.yaml"
    derived_fabm = yaml.safe_load(fabm_path.read_text(encoding="utf-8")) or {}
    instances = derived_fabm["instances"]
    removed = [name for name in ("inorganic_carbon", "methane") if instances.pop(name, None) is not None]
    if set(removed) != {"inorganic_carbon", "methane"}:
        raise ValueError("partial proxy did not remove exactly both GHG instances")
    if any("inorganic_carbon/" in str(value) or "methane/" in str(value)
           for name, item in instances.items() if name not in removed
           for value in (item.get("coupling") or {}).values()):
        raise ValueError("remaining FABM coupling still references a removed GHG instance")
    fabm_path.write_text(yaml.safe_dump(derived_fabm, sort_keys=False, allow_unicode=True), encoding="utf-8")

    manifest = source_manifest
    fabm_source = next(item for item in manifest["sources"] if item["path"] == "fabm.yaml")
    fabm_source["origin_sha256"] = fabm_source["sha256"]
    fabm_source.update({"bytes": fabm_path.stat().st_size, "sha256": _sha256(fabm_path),
                        "purpose": "Erken partial engineering proxy FABM configuration with only GHG instances disabled.",
                        "source_description": "Derived from the approved D-drive Erken proxy; preserves all non-GHG instances and removes inorganic_carbon and methane for the available non-GHG executable."})
    manifest["partial_engineering_proxy"] = True
    manifest["engineering_tier"] = "partial"
    manifest["disabled_modules"] = ["wet/inorganic_carbon", "wet/methane"]
    manifest["active_case_path"] = str(target)
    manifest.setdefault("engineering_adjustments", []).append({
        "path": "fabm.yaml", "setting": "GHG FABM instances", "from": ["inorganic_carbon", "methane"],
        "to": "disabled", "reason": "the available native executable does not contain GHG and local cmake is unavailable; preserve all non-GHG instances for a partial engineering run.",
        "scientific_validation": "not_scientifically_validated",
    })
    manifest["validation_status"] = "not_scientifically_validated"
    (target / "proxy_engineering.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def prepare_proxy_attempt(repo_root: Path, output_root: Path, active_erken_case: Path | None = None) -> dict:
    repo, out = Path(repo_root).resolve(), Path(output_root).resolve()
    if out.exists():
        raise FileExistsError(f"refusing to overwrite existing proxy attempt: {out}")
    active_path = Path(active_erken_case).resolve() if active_erken_case else None
    if active_path and active_path.exists():
        raise FileExistsError(f"refusing to overwrite existing active Erken case: {active_path}")
    if active_path and not active_path.parent.is_dir():
        raise FileNotFoundError(f"active Erken case parent does not exist: {active_path.parent}")
    out.mkdir(parents=True, exist_ok=False)
    result = {}
    for lake, slug in LAKE_SLUGS.items():
        case = out / slug
        case.mkdir()
        manifest = _case_record(repo, case, lake)
        if lake == "Erken" and active_path:
            manifest["active_case_path"] = str(active_path)
        (case / "proxy_engineering.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        result[lake] = {"case_path": str(case), "prepared": manifest["prepared"],
                        "blockers": manifest["blockers"],
                        "copied_source_count": sum(s["role"] != "missing" for s in manifest["sources"])}
        if lake == "Erken" and active_path:
            active_path.mkdir(parents=True, exist_ok=False)
            active_manifest = _case_record(repo, active_path, "Erken")
            if active_manifest["prepared"]:
                _enable_proxy_meteorology(active_path, active_manifest)
            active_manifest["active_case_path"] = str(active_path)
            (active_path / "proxy_engineering.json").write_text(
                json.dumps(active_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            result[lake]["active_case_path"] = str(active_path)
    report = {"kind": "engineering_proxy_preparation", "attempt_root": str(out),
              "scientific_validation_status": "not_scientifically_validated", "cases": result}
    (out / "preparation_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).resolve().parents[2] / "build" /
                                "proxy-engineering-20261027-attempt03")
    parser.add_argument("--active-erken-case", type=Path,
                        default=Path(r"D:\GETM-FABM-WET-outputs\cases\Engineering Proxy - Erken - 20261027"))
    args = parser.parse_args()
    result = prepare_proxy_attempt(args.repo_root, args.output, args.active_erken_case)
    for lake, record in result.items():
        print(f"{lake}: prepared={record['prepared']}; copied_sources={record['copied_source_count']}; blockers={len(record['blockers'])}")
    print(f"Proxy-only preparation complete; scientific validation remains incomplete: {Path(args.output).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
