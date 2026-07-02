import os
import sys
import json
import uuid
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory

BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = Path(__file__).resolve().parent
PROJECTS_DIR = APP_DIR / "projects"
BIN_DIR = BASE_DIR / "bin"
TEST_CASE_DIR = BASE_DIR / "test_case"

PROJECTS_DIR.mkdir(exist_ok=True)

app = Flask(__name__,
            template_folder=str(APP_DIR / "templates"),
            static_folder=str(APP_DIR / "static"))

active_project = None
run_process = None
run_logs = []
run_status = "idle"


def load_project_config(project_path):
    config_file = Path(project_path) / "project.json"
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_project_config(project_path, config):
    config_file = Path(project_path) / "project.json"
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def get_default_config(project_name):
    return {
        "name": project_name,
        "created_at": datetime.now().isoformat(),
        "hydro": {
            "grid_nx": 25,
            "grid_ny": 25,
            "dx": 100.0,
            "dy": 100.0,
            "depth": 10.0,
            "nlev": 5,
            "timestep": 300,
            "start_date": "2000-01-01 00:00:00",
            "end_date": "2000-01-02 00:00:00",
        },
        "ecology": {
            "model": "wet",
            "modules": {
                "phytoplankton": True,
                "zooplankton": True,
                "fish": False,
                "macrophytes": False,
                "zoobenthos": False,
            },
            "nutrients": {
                "O2_initial": 8.0,
                "NH4_initial": 0.05,
                "NO3_initial": 0.5,
                "PO4_initial": 0.02,
            }
        },
        "output": {
            "save2d": True,
            "save3d": True,
            "out_dt": 3600,
        }
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/projects/list")
def list_projects():
    projects = []
    if PROJECTS_DIR.exists():
        for p in PROJECTS_DIR.iterdir():
            if p.is_dir():
                config = load_project_config(p)
                if config:
                    projects.append({
                        "id": p.name,
                        "name": config.get("name", p.name),
                        "created_at": config.get("created_at", ""),
                    })
    return jsonify(projects)


@app.route("/api/projects/create", methods=["POST"])
def create_project():
    data = request.json
    name = data.get("name", "未命名项目")
    project_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]
    project_path = PROJECTS_DIR / project_id
    project_path.mkdir(parents=True, exist_ok=True)

    config = get_default_config(name)
    config["id"] = project_id
    save_project_config(project_path, config)

    return jsonify({"success": True, "project_id": project_id, "config": config})


@app.route("/api/projects/open", methods=["POST"])
def open_project():
    global active_project
    data = request.json
    project_id = data.get("project_id")
    project_path = PROJECTS_DIR / project_id

    if not project_path.exists():
        return jsonify({"success": False, "error": "项目不存在"}), 404

    config = load_project_config(project_path)
    if not config:
        return jsonify({"success": False, "error": "项目配置损坏"}), 400

    active_project = project_id
    return jsonify({"success": True, "config": config})


@app.route("/api/projects/save", methods=["POST"])
def save_project():
    global active_project
    data = request.json
    project_id = data.get("project_id") or active_project
    if not project_id:
        return jsonify({"success": False, "error": "没有活动项目"}), 400

    project_path = PROJECTS_DIR / project_id
    if not project_path.exists():
        return jsonify({"success": False, "error": "项目不存在"}), 404

    config = data.get("config")
    if config:
        save_project_config(project_path, config)
        active_project = project_id

    return jsonify({"success": True})


@app.route("/api/run/start", methods=["POST"])
def start_run():
    global run_process, run_logs, run_status, active_project

    if not active_project:
        return jsonify({"success": False, "error": "请先打开或创建项目"}), 400

    if run_status == "running":
        return jsonify({"success": False, "error": "模型正在运行中"}), 400

    run_logs = []
    run_status = "running"

    def run_model():
        global run_process, run_status
        try:
            test_case = str(TEST_CASE_DIR)
            exe_path = str(BIN_DIR / "getm_cartesian")

            if sys.platform == "win32":
                cmd = ["wsl.exe", "bash", "-c",
                       f"cd /mnt{test_case.replace(':', '').replace(chr(92), '/')} && "
                       f"/mnt{BIN_DIR.resolve().drive.lower()}{str(BIN_DIR.resolve())[2:].replace(chr(92), '/')}/getm_cartesian"]
            else:
                cmd = [exe_path]

            run_logs.append(f"[INFO] 开始运行模型...")
            run_logs.append(f"[INFO] 工作目录: {test_case}")

            run_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=str(TEST_CASE_DIR)
            )

            for line in run_process.stdout:
                line = line.strip()
                if line:
                    run_logs.append(line)

            run_process.wait()
            if run_process.returncode == 0:
                run_status = "completed"
                run_logs.append("[INFO] 模型运行完成")
            else:
                run_status = "failed"
                run_logs.append(f"[ERROR] 模型运行失败，退出码: {run_process.returncode}")

        except Exception as e:
            run_status = "failed"
            run_logs.append(f"[ERROR] 运行异常: {str(e)}")

    thread = threading.Thread(target=run_model, daemon=True)
    thread.start()

    return jsonify({"success": True})


@app.route("/api/run/status")
def run_status_api():
    return jsonify({
        "status": run_status,
        "logs": run_logs[-200:],
        "total_lines": len(run_logs),
    })


@app.route("/api/run/stop", methods=["POST"])
def stop_run():
    global run_process, run_status
    if run_process and run_status == "running":
        run_process.terminate()
        run_status = "stopped"
        run_logs.append("[INFO] 模型已停止")
    return jsonify({"success": True})


@app.route("/api/results")
def get_results():
    nc_file = TEST_CASE_DIR / "GETM_FABM_WET_TEST.3d.nc"
    if not nc_file.exists():
        return jsonify({"error": "No data file found"})

    try:
        import numpy as np
        import netCDF4 as nc

        ds = nc.Dataset(str(nc_file))
        result = {
            "dimensions": {},
            "variables": {},
            "timeseries": {}
        }

        for dim_name, dim in ds.dimensions.items():
            result["dimensions"][dim_name] = len(dim)

        for var_name, var in ds.variables.items():
            result["variables"][var_name] = {
                "name": var_name,
                "dimensions": list(var.dimensions),
                "shape": list(var.shape),
                "units": getattr(var, "units", ""),
                "long_name": getattr(var, "long_name", var_name)
            }

        time_var = None
        for vname in ["time", "Time", "time_counter"]:
            if vname in ds.variables:
                time_var = vname
                break

        if time_var:
            times = ds.variables[time_var][:]
            result["time"] = {
                "values": [float(t) for t in times],
                "units": getattr(ds.variables[time_var], "units", ""),
                "nsteps": len(times)
            }

        center_j = None
        center_i = None
        for var_name, var in ds.variables.items():
            dims = list(var.dimensions)
            y_dims = [d for d in dims if d in ["yc", "y", "lat"]]
            x_dims = [d for d in dims if d in ["xc", "x", "lon"]]
            if y_dims and x_dims:
                y_idx = dims.index(y_dims[0])
                x_idx = dims.index(x_dims[0])
                center_j = var.shape[y_idx] // 2
                center_i = var.shape[x_idx] // 2
                break

        if time_var and center_j is not None:
            for var_name, var in ds.variables.items():
                dims = list(var.dimensions)
                if var.ndim >= 3 and dims[0] == time_var:
                    try:
                        vals = var[:]
                        if var.ndim == 3:
                            series_data = vals[:, center_j, center_i]
                        elif var.ndim == 4:
                            series_data = vals[:, :, center_j, center_i]
                        else:
                            continue

                        if isinstance(series_data, np.ma.MaskedArray):
                            series_data = series_data.filled(np.nan)

                        if series_data.ndim == 1:
                            result["timeseries"][var_name] = {
                                "values": [float(v) if not np.isnan(v) else None for v in series_data],
                                "long_name": getattr(var, "long_name", var_name),
                                "units": getattr(var, "units", ""),
                                "type": "2d_center"
                            }
                        elif series_data.ndim == 2:
                            result["timeseries"][var_name] = {
                                "values": [[float(v) if not np.isnan(v) else None for v in row] for row in series_data],
                                "long_name": getattr(var, "long_name", var_name),
                                "units": getattr(var, "units", ""),
                                "type": "3d_center",
                                "nlevels": series_data.shape[1]
                            }
                    except Exception:
                        pass

        ds.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/results/3d")
def get_results_3d():
    nc_file = TEST_CASE_DIR / "GETM_FABM_WET_TEST.3d.nc"
    if not nc_file.exists():
        return jsonify({"error": "No data file found"}), 404

    try:
        import numpy as np
        import netCDF4 as nc

        ds = nc.Dataset(str(nc_file))

        xc = ds.variables["xc"][:].tolist() if "xc" in ds.variables else []
        yc = ds.variables["yc"][:].tolist() if "yc" in ds.variables else []
        bathy = ds.variables["bathymetry"][:].tolist() if "bathymetry" in ds.variables else []
        sigma = ds.variables["sigma"][:].tolist() if "sigma" in ds.variables else []

        var_name = request.args.get("var", "temp")
        timestep = int(request.args.get("time", 0))

        var_data = None
        if var_name in ds.variables:
            var = ds.variables[var_name]
            if var.ndim == 4:
                data = var[timestep, :, :, :]
            elif var.ndim == 3:
                data = var[timestep, :, :]
            else:
                data = var[:]

            if isinstance(data, np.ma.MaskedArray):
                data = data.filled(np.nan)
            var_data = data.tolist()

        ds.close()

        return jsonify({
            "xc": xc,
            "yc": yc,
            "bathymetry": bathy,
            "sigma": sigma,
            "var_data": var_data,
            "var_name": var_name,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def main():
    import webbrowser
    PORT = 8766
    url = f"http://localhost:{PORT}/"

    print("=" * 60)
    print("  GETM-FABM-WET 生态水动力模型系统")
    print("=" * 60)
    print(f"  服务地址: {url}")
    print("  浏览器将自动打开...")
    print("  关闭此窗口将停止服务")
    print("=" * 60)

    webbrowser.open(url)
    app.run(host="127.0.0.1", port=PORT, debug=False)


if __name__ == "__main__":
    main()
