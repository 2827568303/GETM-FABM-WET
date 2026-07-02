import os
import sys
import json
import webbrowser
import http.server
import socketserver
import urllib.parse
from pathlib import Path

BASE_DIR = Path(__file__).parent
TEST_CASE_DIR = BASE_DIR / "test_case"
LUOMAHU_DIR = BASE_DIR / "luomahu_case"
VIEWER_DIR = BASE_DIR / "viewer"


def get_nc_files():
    files = []
    for dir_path in [LUOMAHU_DIR, TEST_CASE_DIR]:
        if not dir_path.exists():
            continue
        for nc_file in dir_path.glob("*.nc"):
            if nc_file.name.endswith(".3d.nc"):
                files.append({
                    "name": nc_file.name,
                    "path": str(nc_file),
                    "size": f"{nc_file.stat().st_size / 1024 / 1024:.1f} MB"
                })
    return files


def get_nc_info(nc_path):
    try:
        import numpy as np
        import netCDF4 as nc
    except ImportError:
        os.system(f"{sys.executable} -m pip install numpy netCDF4")
        import numpy as np
        import netCDF4 as nc

    ds = nc.Dataset(nc_path)
    result = {"dimensions": {}, "variables": [], "time": None}

    for dim_name, dim in ds.dimensions.items():
        result["dimensions"][dim_name] = len(dim)

    for var_name, var in ds.variables.items():
        var_info = {
            "name": var_name,
            "dimensions": list(var.dimensions),
            "shape": list(var.shape),
            "units": getattr(var, "units", ""),
            "long_name": getattr(var, "long_name", var_name),
            "ndim": var.ndim
        }
        result["variables"].append(var_info)

    if "time" in ds.variables:
        times = ds.variables["time"][:]
        result["time"] = {
            "values": [float(t) for t in times],
            "units": getattr(ds.variables["time"], "units", ""),
            "nsteps": len(times)
        }

    ds.close()
    return result


def get_var_data(nc_path, var_name, time_step, z_level=None):
    try:
        import numpy as np
        import netCDF4 as nc
    except ImportError:
        os.system(f"{sys.executable} -m pip install numpy netCDF4")
        import numpy as np
        import netCDF4 as nc

    ds = nc.Dataset(nc_path)
    var = ds.variables[var_name]
    dims = list(var.dimensions)
    data = var[:]

    if isinstance(data, np.ma.MaskedArray):
        data = data.filled(np.nan)

    time_idx = dims.index("time")
    data = np.take(data, time_step, axis=time_idx)

    if z_level is not None and var.ndim >= 3:
        z_idx = None
        for i, d in enumerate(dims):
            if d in ["sigma", "z", "level"] and i != time_idx:
                z_idx = i
                break
        if z_idx is not None:
            data = np.take(data, z_level, axis=z_idx)

    coords = {}
    if "lonc" in ds.variables:
        lon_data = ds.variables["lonc"][:]
        if isinstance(lon_data, np.ma.MaskedArray):
            lon_data = lon_data.filled(np.nan)
        coords["lon"] = lon_data.tolist()
    if "latc" in ds.variables:
        lat_data = ds.variables["latc"][:]
        if isinstance(lat_data, np.ma.MaskedArray):
            lat_data = lat_data.filled(np.nan)
        coords["lat"] = lat_data.tolist()
    if "xc" in ds.variables:
        xc_data = ds.variables["xc"][:]
        coords["xc"] = xc_data.tolist() if hasattr(xc_data, 'tolist') else list(xc_data)
    if "yc" in ds.variables:
        yc_data = ds.variables["yc"][:]
        coords["yc"] = yc_data.tolist() if hasattr(yc_data, 'tolist') else list(yc_data)
    if "sigma" in ds.variables:
        sigma_data = ds.variables["sigma"][:]
        coords["sigma"] = sigma_data.tolist() if hasattr(sigma_data, 'tolist') else list(sigma_data)

    ds.close()

    result = {
        "data": [],
        "coords": coords,
        "shape": list(data.shape),
        "ndim": data.ndim
    }

    if data.ndim == 2:
        for row in data:
            result["data"].append([float(v) if not np.isnan(v) else None for v in row])
    elif data.ndim == 1:
        result["data"] = [float(v) if not np.isnan(v) else None for v in data]
    else:
        for level in data:
            level_data = []
            for row in level:
                level_data.append([float(v) if not np.isnan(v) else None for v in row])
            result["data"].append(level_data)

    return result


class ViewerHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(VIEWER_DIR), **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)

        if parsed.path == "/api/files":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(get_nc_files()).encode("utf-8"))

        elif parsed.path == "/api/info":
            nc_path = query.get("path", [None])[0]
            if nc_path:
                data = get_nc_info(nc_path)
            else:
                data = {"error": "No file path provided"}
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))

        elif parsed.path == "/api/data":
            nc_path = query.get("path", [None])[0]
            var_name = query.get("var", [None])[0]
            time_step = int(query.get("time", [0])[0])
            z_level = query.get("z", [None])[0]
            if z_level is not None:
                z_level = int(z_level)

            if nc_path and var_name:
                data = get_var_data(nc_path, var_name, time_step, z_level)
            else:
                data = {"error": "Missing parameters"}
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))

        else:
            super().do_GET()

    def log_message(self, format, *args):
        pass


def main():
    print("=" * 60)
    print("  GETM-FABM-WET 结果可视化工具")
    print("=" * 60)

    files = get_nc_files()
    if not files:
        print("错误: 找不到NC输出文件")
        input("\n按回车键退出...")
        return

    print(f"找到 {len(files)} 个NC文件:")
    for f in files:
        print(f"  - {f['name']} ({f['size']})")
    print()

    VIEWER_DIR.mkdir(exist_ok=True)

    PORT = 8765
    url = f"http://localhost:{PORT}/index.html"

    print("正在启动可视化服务器...")
    print(f"页面地址: {url}")
    print()
    print("浏览器将自动打开，请稍候...")
    print("关闭此窗口将停止服务器")
    print("=" * 60)

    webbrowser.open(url)

    os.chdir(str(VIEWER_DIR))

    with socketserver.TCPServer(("", PORT), ViewerHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务器已停止")


if __name__ == "__main__":
    main()
