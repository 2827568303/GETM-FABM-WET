#!/usr/bin/env python3
"""Exercise every 3DWET UI module through its backend endpoints.

The restored Lake Dianchi case is copied into a temporary case root first.
Nothing in this script writes to the repository case tree or starts a solver.
"""
from __future__ import annotations

import io
import os
import shutil
import sys
import tempfile
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "3DWET" / "app"
SOURCE_CASE = ROOT / "3DWET" / "case" / "Lake Dianchi"


def _finite(rows):
    for row in rows or []:
        for value in row:
            if isinstance(value, (int, float)):
                return value
    return None


class Report:
    def __init__(self):
        self.rows = []

    def add(self, module, ok, detail):
        self.rows.append((module, bool(ok), detail))
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {module}: {detail}", flush=True)

    def failed(self):
        return [row for row in self.rows if not row[1]]


def main() -> int:
    report = Report()
    if not (SOURCE_CASE / "getm.inp").is_file():
        report.add("案例管理", False, f"仓库中没有可复制的案例: {SOURCE_CASE}")
        return 1

    work = Path(tempfile.mkdtemp(prefix="3dwet-smoke-"))
    case_root = work / "cases"
    state_root = work / "state"
    case_root.mkdir()
    state_root.mkdir()
    os.environ["WET_CASE_DIR"] = str(case_root)
    os.environ["WET_CASE_STATE_DIR"] = str(state_root)
    os.environ["WET_MODEL_ROOT"] = str(ROOT / "3DWET")
    sys.path.insert(0, str(APP))

    try:
        import netCDF4 as nc
        import numpy as np
        import shapefile
        import server
        from netcdf_compression import compress_netcdf_file
    except Exception as exc:
        report.add("案例管理", False, f"服务导入失败: {exc}")
        traceback.print_exc()
        return 1

    case = case_root / "Lake Dianchi"
    shutil.copytree(SOURCE_CASE, case)
    for folder in (case, case / "output"):
        if not folder.is_dir():
            continue
        for path in folder.glob("*"):
            if path.is_file() and (
                path.name in {"output.nc", "restart.nc"}
                or path.name.endswith(".2d.nc")
                or path.name.endswith(".3d.nc")
                or path.name.startswith("ext_wq")
            ):
                path.unlink()

    with nc.Dataset(case / "bathymetry.nc") as ds:
        ny, nx = ds.variables["bathymetry"].shape
    client = server.app.test_client()

    def expect(response, status=200):
        if response.status_code != status:
            body = response.get_data(as_text=True)[:500]
            raise AssertionError(f"HTTP {response.status_code}: {body}")
        return response.get_json(silent=True)

    try:
        listed = expect(client.get("/api/cases"))
        names = [item.get("name") or item.get("case_name") for item in listed]
        if "Lake Dianchi" not in names:
            raise AssertionError(f"案例列表没有 Lake Dianchi: {names}")
        storage = expect(client.get("/api/system/case-storage"))
        if Path(storage["case_root"]).resolve() != case_root.resolve():
            raise AssertionError(f"案例根不是临时目录: {storage}")
        loaded = expect(client.post("/api/case/load", json={"case_name": "Lake Dianchi"}))
        if loaded.get("case_name") != "Lake Dianchi" or not loaded.get("success"):
            raise AssertionError(loaded)
        current = expect(client.get("/api/case/current"))
        if Path(current["case_path"]).resolve() != case.resolve():
            raise AssertionError(current)
        inputs = expect(client.get("/api/case/inputs"))
        input_names = {item.get("name") or item.get("file") or str(item) for item in inputs.get("files", [])}
        if not any("getm.inp" in name for name in input_names):
            raise AssertionError(f"输入列表缺少 getm.inp: {inputs}")
        report.add("案例管理", True, f"已加载副本 {case.name}，列表 {len(listed)} 个案例")
    except Exception as exc:
        report.add("案例管理", False, str(exc))

    boundary_id = grid_id = bathy_id = None
    try:
        shore = work / "shore"
        writer = shapefile.Writer(str(shore), shapeType=shapefile.POLYGON)
        writer.field("id", "N")
        writer.poly([[[102.65, 24.75], [102.65, 24.85], [102.75, 24.85],
                      [102.75, 24.75], [102.65, 24.75]]])
        writer.record(1)
        writer.close()
        (work / "shore.prj").write_text(
            'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],'
            'PRIMEM["Greenwich",0],UNIT["Degree",0.0174532925199433]]', encoding="utf-8")
        uploads = [(io.BytesIO((work / f"shore{suffix}").read_bytes()), f"shore{suffix}")
                   for suffix in (".shp", ".shx", ".dbf", ".prj")]
        uploaded = expect(client.post(
            "/api/preprocess/boundary/upload",
            data={"files": uploads, "crs_preset": "auto"},
            content_type="multipart/form-data"))
        boundary_id = uploaded["boundary_id"]
        generated = expect(client.post("/api/preprocess/grid/generate", json={
            "boundary_id": boundary_id, "dx": 500, "dy": 500}))
        if generated["n_water_cells"] < 1:
            raise AssertionError(f"边界栅格没有水格: {generated['nx']}x{generated['ny']}")
        hypsograph = "0 1000\n2 80000\n4 250000\n"
        hypo = expect(client.post(
            "/api/preprocess/hypsograph",
            data={"file": (io.BytesIO(hypsograph.encode()), "hypsograph.dat"),
                  "center_lon": "102.7", "center_lat": "24.8"},
            content_type="multipart/form-data"))
        bathy_id = hypo["bathy_id"]
        generated = expect(client.post("/api/preprocess/grid/generate", json={
            "boundary_id": hypo["boundary_id"], "dx": 40, "dy": 40}))
        grid_id = generated["grid_id"]
        if generated["n_water_cells"] < 1:
            raise AssertionError("深度-面积曲线没有生成水格")
        report.add("前处理与网格生成", True,
                   f"岸线 {uploaded['n_polygons']} 个环，曲线网格 {generated['nx']}x{generated['ny']}，"
                   f"水格 {generated['n_water_cells']}")
    except Exception as exc:
        report.add("前处理与网格生成", False, str(exc))

    try:
        if not grid_id or not bathy_id:
            raise AssertionError("没有可用的网格缓存")
        terrain = expect(client.post("/api/preprocess/bathymetry/interpolate", json={
            "grid_id": grid_id, "bathy_id": bathy_id, "method": "nearest"}))
        if terrain["depth_max"] <= 0 or not terrain["depth_array"]:
            raise AssertionError(terrain)
        preview = expect(client.get(f"/api/preprocess/preview?grid_id={grid_id}&boundary_id={hypo['boundary_id']}"))
        if "grid" not in preview:
            raise AssertionError(preview)
        report.add("地形", True, f"插值水深 {terrain['depth_min']:.2f}–{terrain['depth_max']:.2f} m")
    except Exception as exc:
        report.add("地形", False, str(exc))

    try:
        fabm = expect(client.get("/api/config/fabm"))
        modules = fabm.get("modules") or []
        if not modules:
            raise AssertionError("fabm.yaml 没有模块")
        catalog = expect(client.get("/api/config/modules"))
        engines = expect(client.get("/api/config/engines"))
        ghg = expect(client.get("/api/config/ghg"))
        if "modules" not in catalog and "available" not in catalog and not isinstance(catalog, dict):
            raise AssertionError(catalog)
        report.add("FABM 配置", True, f"{len(modules)} 个模块，引擎接口 {list(engines)[:4]}")
    except Exception as exc:
        report.add("FABM 配置", False, str(exc))

    try:
        draft = expect(client.get("/api/input/meteo/draft"))
        if "exists" not in draft:
            raise AssertionError(draft)
        if not (case / "meteo.nc").is_file():
            raise AssertionError("案例副本缺少 meteo.nc")
        report.add("气象", True, "气象草稿接口可用，案例含 meteo.nc" if not draft["exists"]
                   else f"气象草稿 {len(draft.get('dates') or [])} 行")
    except Exception as exc:
        report.add("气象", False, str(exc))

    try:
        rivers = expect(client.get("/api/input/rivers"))
        if not (rivers.get("has_riverinfo") or rivers.get("has_rivers_nc") or rivers.get("rivers")):
            raise AssertionError(rivers)
        detail = f"{len(rivers.get('rivers') or [])} 条河流记录"
        named = next((item.get("name") for item in rivers.get("rivers") or [] if item.get("name")), None)
        if named:
            series = expect(client.get(f"/api/input/rivers/series?name={named}"))
            detail += f"，{named} 序列已读出"
        report.add("河流", True, detail)
    except Exception as exc:
        report.add("河流", False, str(exc))

    try:
        timing = expect(client.get("/api/config/time"))
        if not timing.get("start") or not timing.get("stop"):
            raise AssertionError(timing)
        output = expect(client.get("/api/config/output"))
        hotstart = expect(client.get("/api/config/hotstart"))
        if not isinstance(output, dict) or not isinstance(hotstart, dict):
            raise AssertionError("时间/输出/热启动响应不是对象")
        report.add("时间与输出", True, f"{timing['start']} → {timing['stop']}，dt={timing.get('timestep')}")
    except Exception as exc:
        report.add("时间与输出", False, str(exc))

    try:
        page = client.get("/")
        if page.status_code != 200:
            raise AssertionError(f"首页 HTTP {page.status_code}")
        html = page.get_data(as_text=True)
        for needle in ("使用核数", "重新测定", "core-trial-table", "检测并采用建议", "实测进程数"):
            if needle not in html:
                raise AssertionError(f"运行控制页面缺少 {needle}")
        status = expect(client.get("/api/run/status"))
        if status.get("status") == "running":
            raise AssertionError("冒烟开始时已有模型在运行")
        estimate = expect(client.get("/api/run/estimate"))
        plan = expect(client.get("/api/run/core-plan"))
        if not isinstance(plan.get("trials"), list) or "recommendation" not in plan:
            raise AssertionError("核数方案没有测定表")
        caps = expect(client.get("/api/run/mpi-capabilities"))
        if "enabled" not in caps:
            raise AssertionError(caps)
        tuning = expect(client.get("/api/run/mpi-tuning"))
        report.add("运行控制与监测", True,
                   f"状态 {status.get('status')}，测定 {len(plan['trials'])} 行，"
                   f"MPI {'可用' if caps.get('enabled') else '未启用'}")
    except Exception as exc:
        report.add("运行控制与监测", False, str(exc))

    health = None
    health_error = None
    try:
        help_doc = expect(client.get("/api/preprocess/help"))
        if "boundary" not in help_doc or "bathymetry_point" not in help_doc:
            raise AssertionError(help_doc)
        health = expect(client.get("/api/run/check"))
        if "checks" not in health:
            raise AssertionError(health)
        blocking = [item for item in health["checks"] if item.get("level") == "error"]
        if blocking:
            raise AssertionError("；".join(f"{item['title']}: {item['detail']}" for item in blocking))
    except Exception as exc:
        health_error = exc

    wq_name = "abiotic_water_sO2W"
    try:
        temp = np.zeros((2, 3, ny, nx), dtype="f4")
        temp[:, 0] = 11
        temp[:, 1] = 22
        temp[:, 2] = 33
        oxygen = np.zeros((2, 3, ny, nx), dtype="f4")
        oxygen[:, 0] = 4.5
        oxygen[:, 1] = 8.5
        oxygen[:, 2] = 12.5

        def write_field(path, name, values):
            path.parent.mkdir(parents=True, exist_ok=True)
            with nc.Dataset(path, "w") as ds:
                ds.createDimension("time", values.shape[0])
                ds.createDimension("z", values.shape[1])
                ds.createDimension("y", ny)
                ds.createDimension("x", nx)
                clock = ds.createVariable("time", "f8", ("time",))
                clock.units = "seconds since 2000-01-01 00:00:00"
                clock[:] = [0, 86400]
                field = ds.createVariable(name, "f4", ("time", "z", "y", "x"))
                field[:] = values

        write_field(case / "output" / "output.nc", "temp", temp)
        write_field(case / "ext_wq.nc", wq_name, oxygen)
        variables = expect(client.get("/api/results/variables"))
        names = {item["name"] for item in variables.get("3d", [])}
        if "temp" not in names or wq_name not in names:
            raise AssertionError(f"根目录 ext_wq 未进入变量表: {sorted(names)}")
        surface = expect(client.get("/api/results/2d?var=temp&time=0&level=0"))
        upper = expect(client.get("/api/results/2d?var=temp&time=0&level=1"))
        if _finite(surface.get("data")) != 11 or _finite(upper.get("data")) != 22:
            raise AssertionError(f"层切换未读到不同水温: {_finite(surface.get('data'))} / {_finite(upper.get('data'))}")
        wq = expect(client.get(f"/api/results/2d?var={wq_name}&time=0&level=1"))
        if _finite(wq.get("data")) != 8.5:
            raise AssertionError(f"水质变量层值不符: {_finite(wq.get('data'))}")
        server._archive_run_outputs(case, [])
        if (case / "ext_wq.nc").exists() or not (case / "output" / "ext_wq.nc").is_file():
            raise AssertionError("ext_wq.nc 没有在运行结束后进入 output/")
        variables = expect(client.get("/api/results/variables"))
        names = {item["name"] for item in variables.get("3d", [])}
        if wq_name not in names:
            raise AssertionError("归档到 output/ 后水质变量消失")
        wq = expect(client.get(f"/api/results/2d?var={wq_name}&time=0&level=0"))
        if _finite(wq.get("data")) != 4.5:
            raise AssertionError("output/ext_wq.nc 未能按层读出")
        report.add("二维可视化", True, f"网格 {ny}x{nx}，水温层 11/22，{wq_name} 在根目录和 output/ 都可读")
    except Exception as exc:
        report.add("二维可视化", False, str(exc))

    try:
        volume = expect(client.get("/api/results/3d_surface?var=temp&time=0&target=32"))
        if not volume.get("data") or volume.get("var_name") != "temp":
            raise AssertionError(volume.get("error") or "三维水温没有数据")
        wq_volume = expect(client.get(f"/api/results/3d_surface?var={wq_name}&time=0&target=32"))
        if wq_volume.get("var_name") != wq_name or not wq_volume.get("data"):
            raise AssertionError(wq_volume.get("error") or "三维水质没有数据")
        report.add("三维可视化", True,
                   f"水温层数 {volume.get('total_layers')}，水质变量 {wq_name}")
    except Exception as exc:
        report.add("三维可视化", False, str(exc))

    try:
        grid = expect(client.get("/api/geo/grid"))
        if not grid.get("depth") or grid.get("nx", 0) < 1:
            raise AssertionError(grid.get("error") or "地图网格为空")
        field = expect(client.get("/api/geo/field?var=temp&time=0&level=-1"))
        other = expect(client.get("/api/geo/field?var=temp&time=0&level=0"))
        if _finite(field.get("values")) == _finite(other.get("values")):
            raise AssertionError("地图表层和底层温度没有区别")
        report.add("地图", True, f"{grid['ny']}x{grid['nx']}，坐标 {grid.get('coordinate_mode')}")
    except Exception as exc:
        report.add("地图", False, str(exc))

    try:
        target = work / "compressible.nc"
        with nc.Dataset(target, "w", format="NETCDF3_CLASSIC") as ds:
            ds.createDimension("n", 80000)
            values = ds.createVariable("pattern", "f4", ("n",))
            values[:] = np.resize(np.arange(8, dtype="f4"), 80000)
        compressed = compress_netcdf_file(target)
        if compressed.get("status") != "compressed":
            raise AssertionError(compressed)
        report.add("结果压缩", True,
                   f"{compressed['original_bytes']} → {compressed['compressed_bytes']} 字节")
    except Exception as exc:
        report.add("结果压缩", False, str(exc))

    try:
        if health_error is not None:
            raise health_error
        dashboard = expect(client.get("/api/dashboard/summary"))
        if "temp" not in dashboard or wq_name not in dashboard:
            raise AssertionError(f"仪表盘缺少水温或溶解氧: {list(dashboard)[:8]}")
        report.add("帮助与诊断", True,
                   f"体检 {len(health['checks'])} 项且无阻塞，仪表盘含 {wq_name}")
    except Exception as exc:
        report.add("帮助与诊断", False, str(exc))

    try:
        editor = expect(client.get("/api/grid/editor"))
        cell = None
        for j, row in enumerate(editor["depth"]):
            for i, value in enumerate(row):
                if isinstance(value, (int, float)) and value > 0:
                    cell = (i, j, value)
                    break
            if cell:
                break
        if cell is None:
            raise AssertionError("地形里没有可编辑水格")
        i, j, original = cell
        edited = expect(client.post("/api/grid/edit", json={
            "case_path": editor["case_path"], "revision": editor["revision"],
            "action": "depth", "cells": [[i, j]], "value": original + 1.5}))
        if edited["depth"][j][i] != original + 1.5:
            raise AssertionError("水深编辑没有写入会话")
        restored = expect(client.post("/api/grid/edit", json={
            "case_path": editor["case_path"], "revision": edited["revision"],
            "action": "undo"}))
        if restored["depth"][j][i] != original:
            raise AssertionError("撤销没有恢复水深")
        report.add("交互网格编辑", True, f"水格 ({i},{j}) 修改后已撤销")
    except Exception as exc:
        report.add("交互网格编辑", False, str(exc))

    try:
        created = expect(client.post("/api/preprocess/case/create", json={"case_name": "SmokeTemp"}))
        removed = expect(client.post("/api/case/delete", json={"path": created["case_path"]}))
        if not removed.get("success") or Path(created["case_path"]).exists():
            raise AssertionError(removed)
        reloaded = expect(client.post("/api/case/load", json={"case_name": "Lake Dianchi"}))
        if not reloaded.get("success"):
            raise AssertionError(reloaded)
        report.add("案例新建与删除", True, "临时案例已创建并删除，滇池副本仍可重新加载")
    except Exception as exc:
        report.add("案例新建与删除", False, str(exc))

    print("\n模块 | 结果 | 说明")
    print("---|---|---")
    for module, ok, detail in report.rows:
        print(f"{module} | {'通过' if ok else '失败'} | {detail}")
    failed = report.failed()
    print(f"\n{len(report.rows) - len(failed)} passed, {len(failed)} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
