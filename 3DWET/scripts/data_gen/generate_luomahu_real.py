import numpy as np
import pandas as pd
import netCDF4 as nc
from pathlib import Path
from scipy.interpolate import griddata
from matplotlib.path import Path as MplPath

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "Luomahu_inputs"
CASE_DIR = BASE_DIR / "luomahu_case"
CASE_DIR.mkdir(exist_ok=True)

DX = 500.0
DY = 500.0
NLEV = 10

UTM_ZONE = 50

def read_p2d_elev():
    points = []
    with open(INPUT_DIR / "Bottom_Elev.p2d", "r") as f:
        f.readline()
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 3:
                points.append((float(parts[0]), float(parts[1]), float(parts[2])))
    return np.array(points)

def read_p2d_boundary():
    points = []
    with open(INPUT_DIR / "骆马湖_边界.p2d", "r") as f:
        f.readline()
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                points.append((float(parts[0]), float(parts[1])))
    return np.array(points)

def generate_grid_and_bathymetry():
    print("  读取地形数据...")
    elev_points = read_p2d_elev()
    bdy_points = read_p2d_boundary()

    x_min = elev_points[:, 0].min() - DX
    x_max = elev_points[:, 0].max() + DX
    y_min = elev_points[:, 1].min() - DY
    y_max = elev_points[:, 1].max() + DY

    x_min = np.floor(x_min / DX) * DX
    x_max = np.ceil(x_max / DX) * DX
    y_min = np.floor(y_min / DY) * DY
    y_max = np.ceil(y_max / DY) * DY

    nx = int((x_max - x_min) / DX) + 1
    ny = int((y_max - y_min) / DY) + 1

    print(f"  网格范围: X={x_min:.0f}~{x_max:.0f}, Y={y_min:.0f}~{y_max:.0f}")
    print(f"  网格大小: {nx} x {ny} = {nx*ny} 个网格")

    x_centers = x_min + DX/2 + np.arange(nx) * DX
    y_centers = y_min + DY/2 + np.arange(ny) * DY

    X, Y = np.meshgrid(x_centers, y_centers)

    print("  判断湖内网格...")
    bdy_path = MplPath(bdy_points)
    grid_points = np.column_stack((X.ravel(), Y.ravel()))
    inside = bdy_path.contains_points(grid_points).reshape(ny, nx)

    print(f"  湖内网格数: {np.sum(inside)}")

    print("  插值水深...")
    elev_interp = griddata(
        elev_points[:, :2],
        elev_points[:, 2],
        (X, Y),
        method='linear',
        fill_value=np.nan
    )

    reference_elev = 21.0
    bathy = reference_elev - elev_interp
    bathy[~inside] = 0.0
    bathy[np.isnan(bathy)] = 0.0
    bathy = np.clip(bathy, 0, 20.0)

    print(f"  水深范围: {bathy[bathy>0].min():.2f} ~ {bathy.max():.2f} m")
    print(f"  水域面积: {np.sum(bathy > 0) * DX * DY / 1e6:.2f} km²")

    lat0 = 34.0
    lon0 = 118.07
    lon = lon0 + (X - X[0, 0]) / (111000.0 * np.cos(np.radians(lat0)))
    lat = lat0 + (Y - Y[0, 0]) / 111000.0

    return {
        "nx": nx, "ny": ny,
        "x_centers": x_centers, "y_centers": y_centers,
        "X": X, "Y": Y,
        "lon": lon, "lat": lat,
        "bathy": bathy,
        "inside": inside,
        "x_min": x_min, "x_max": x_max,
        "y_min": y_min, "y_max": y_max,
    }

def write_bathy_nc(grid):
    nx, ny = grid["nx"], grid["ny"]
    ds = nc.Dataset(str(CASE_DIR / "bathymetry.nc"), "w", format="NETCDF4")

    ds.createDimension("x", nx)
    ds.createDimension("y", ny)

    grid_type = ds.createVariable("grid_type", "i4")
    grid_type.long_name = "grid type"
    grid_type[:] = 1

    x_var = ds.createVariable("x", "f4", ("x",))
    x_var.units = "m"
    x_var.long_name = "x-coordinate"
    x_var[:] = grid["x_centers"]

    y_var = ds.createVariable("y", "f4", ("y",))
    y_var.units = "m"
    y_var.long_name = "y-coordinate"
    y_var[:] = grid["y_centers"]

    lonc_var = ds.createVariable("lonc", "f8", ("y", "x"))
    lonc_var.units = "degrees_east"
    lonc_var.long_name = "longitude"
    lonc_var[:] = grid["lon"]

    latc_var = ds.createVariable("latc", "f8", ("y", "x"))
    latc_var.units = "degrees_north"
    latc_var.long_name = "latitude"
    latc_var[:] = grid["lat"]

    bathy_var = ds.createVariable("bathymetry", "f4", ("y", "x"), fill_value=-10.0)
    bathy_var.units = "m"
    bathy_var.long_name = "bathymetry"
    bathy_var.missing_value = -10.0
    bathy_var.valid_range = [-5., 13000.]

    bathy = grid["bathy"].copy()
    bathy[bathy <= 0] = -10.0
    bathy_var[:] = bathy

    ds.close()
    print(f"  已写入 bathymetry.nc")

def find_river_locations(grid):
    bdy_points = read_p2d_boundary()
    bathy = grid["bathy"]
    X, Y = grid["X"], grid["Y"]

    def find_nearest_water(target_x, target_y, search_radius=5000):
        distances = np.sqrt((X - target_x)**2 + (Y - target_y)**2)
        mask = (bathy > 0) & (distances <= search_radius)
        if not np.any(mask):
            return None, None
        dist_masked = np.where(mask, distances, np.inf)
        idx = np.unravel_index(np.argmin(dist_masked), dist_masked.shape)
        return idx[0], idx[1]

    x_min_idx = np.argmin(bdy_points[:, 0])
    x_max_idx = np.argmax(bdy_points[:, 0])
    y_min_idx = np.argmin(bdy_points[:, 1])
    y_max_idx = np.argmax(bdy_points[:, 1])

    rivers = {}

    x, y = bdy_points[x_min_idx, 0] + 1500, bdy_points[x_min_idx, 1] + 2500
    j, i = find_nearest_water(x, y)
    rivers["DAYUN"] = {"name": "京杭大运河", "type": "inout", "i": i, "j": j}

    x, y = bdy_points[y_max_idx, 0] - 3000, bdy_points[y_max_idx, 1] - 500
    j, i = find_nearest_water(x, y)
    rivers["YIHE"] = {"name": "沂河", "type": "in", "i": i, "j": j}

    x, y = bdy_points[y_min_idx, 0] - 2000, bdy_points[y_min_idx, 1] + 500
    j, i = find_nearest_water(x, y)
    rivers["LUONAN"] = {"name": "骆南中运河", "type": "in", "i": i, "j": j}

    x, y = bdy_points[x_max_idx, 0] - 2000, bdy_points[y_min_idx, 1] + 5000
    j, i = find_nearest_water(x, y)
    rivers["ZHANGSHAN"] = {"name": "嶂山闸/新沂河", "type": "out", "i": i, "j": j}

    x, y = bdy_points[x_max_idx, 0] - 3000, (bdy_points[y_max_idx, 1] + bdy_points[y_min_idx, 1]) / 2
    j, i = find_nearest_water(x, y)
    rivers["YANGHE"] = {"name": "杨河滩/总六塘河", "type": "out", "i": i, "j": j}

    print("\n  河道位置:")
    for key, info in rivers.items():
        depth = bathy[info["j"], info["i"]] if info["j"] is not None else 0
        print(f"    {key:10s} ({info['name']:8s}): i={info['i']}, j={info['j']}, depth={depth:.2f}m, type={info['type']}")

    return rivers

def write_riverinfo(rivers):
    with open(CASE_DIR / "riverinfo.dat", "w") as f:
        f.write(f"{len(rivers)}\n")
        for key, info in rivers.items():
            f.write(f"{info['i']+1} {info['j']+1} {key} -1 -1\n")
    print(f"  已写入 riverinfo.dat ({len(rivers)} 条河流)")

def read_flow_data(ndays=20):
    df = pd.read_excel(INPUT_DIR / "Inputs.xlsx", sheet_name="Flows", header=2)
    df = df.iloc[1:ndays+2].reset_index(drop=True)

    dates = pd.to_datetime(df.iloc[:, 0])
    dayun = pd.to_numeric(df.iloc[:, 1], errors='coerce').fillna(0).values
    luonan = pd.to_numeric(df.iloc[:, 2], errors='coerce').fillna(0).values
    yihe = pd.to_numeric(df.iloc[:, 3], errors='coerce').fillna(0).values
    zhangshan = pd.to_numeric(df.iloc[:, 4], errors='coerce').fillna(0).values
    yanghe = pd.to_numeric(df.iloc[:, 5], errors='coerce').fillna(0).values

    print(f"  京杭大运河: {dayun.mean():.1f} m³/s (范围: {dayun.min():.1f}~{dayun.max():.1f})")
    print(f"  骆南中运河: {luonan.mean():.1f} m³/s")
    print(f"  沂河: {yihe.mean():.1f} m³/s")
    print(f"  嶂山闸: {zhangshan.mean():.1f} m³/s")
    print(f"  杨河滩: {yanghe.mean():.1f} m³/s")

    return {
        "dates": dates,
        "DAYUN": dayun,
        "LUONAN": luonan,
        "YIHE": yihe,
        "ZHANGSHAN": zhangshan,
        "YANGHE": yanghe,
    }

def read_load_data(sheet_name, ndays=20):
    df = pd.read_excel(INPUT_DIR / "Inputs.xlsx", sheet_name=sheet_name)
    df_data = df.iloc[2:ndays+2].reset_index(drop=True)

    result = {}

    result["temp"] = pd.to_numeric(df_data.iloc[:, 3], errors='coerce').fillna(10.0).values
    result["do"] = pd.to_numeric(df_data.iloc[:, 6], errors='coerce').fillna(8.0).values
    result["imn"] = pd.to_numeric(df_data.iloc[:, 8], errors='coerce').fillna(3.0).values
    result["nh4"] = pd.to_numeric(df_data.iloc[:, 10], errors='coerce').fillna(0.2).values
    result["tp"] = pd.to_numeric(df_data.iloc[:, 11], errors='coerce').fillna(0.1).values
    result["tn"] = pd.to_numeric(df_data.iloc[:, 12], errors='coerce').fillna(2.0).values

    po4_col = None
    for idx, col in enumerate(df.columns):
        if "PO4" in str(col) and idx < 20:
            po4_col = idx
            break
    if po4_col is not None:
        result["po4"] = pd.to_numeric(df_data.iloc[:, po4_col], errors='coerce').fillna(0.05).values
    else:
        result["po4"] = result["tp"] * 0.5

    result["chla_cyano"] = pd.to_numeric(df_data.iloc[:, 20], errors='coerce').fillna(0.01).values
    result["chla_diatom"] = pd.to_numeric(df_data.iloc[:, 22], errors='coerce').fillna(0.01).values
    result["chla_green"] = pd.to_numeric(df_data.iloc[:, 24], errors='coerce').fillna(0.01).values

    result["nh4_mmol"] = result["nh4"] / 14.0 * 1000.0
    result["no3_mmol"] = result["tn"] / 14.0 * 1000.0 * 0.6
    result["po4_mmol"] = result["po4"] / 31.0 * 1000.0
    result["pom_mmol"] = result["tn"] / 14.0 * 1000.0 * 0.1

    return result

def write_rivers_nc(flow_data, ndays=20):
    times = np.arange(ndays + 1) * 86400.0

    ds = nc.Dataset(str(CASE_DIR / "rivers.nc"), "w", format="NETCDF4")
    ds.createDimension("time", None)

    time_var = ds.createVariable("time", "f8", ("time",))
    time_var.units = "seconds since 2020-01-01 00:00:00"
    time_var.long_name = "time"
    time_var[:] = times

    load_dayun = read_load_data("Loads-京杭大运河", ndays)
    load_luonan = read_load_data("Loads-骆南中运河", ndays)
    load_yihe = read_load_data("Loads-沂河", ndays)

    river_loads = {
        "DAYUN": load_dayun,
        "LUONAN": load_luonan,
        "YIHE": load_yihe,
        "ZHANGSHAN": load_dayun,
        "YANGHE": load_dayun,
    }

    for river_key in ["DAYUN", "LUONAN", "YIHE", "ZHANGSHAN", "YANGHE"]:
        flow = flow_data[river_key]
        load = river_loads[river_key]

        q_var = ds.createVariable(river_key, "f4", ("time",), fill_value=-999.0)
        q_var.units = "m3 s-1"
        q_var.long_name = f"{river_key} discharge"
        q_var.temp = 0
        q_var[:] = flow[:ndays+1]

        nh4_var = ds.createVariable(f"{river_key}_ammonium", "f4", ("time",), fill_value=-999.0)
        nh4_var.units = "mmol m-3"
        nh4_var.long_name = f"{river_key} NH4 concentration"
        nh4_var[:] = load["nh4_mmol"][:ndays+1]

        no3_var = ds.createVariable(f"{river_key}_nitrate", "f4", ("time",), fill_value=-999.0)
        no3_var.units = "mmol m-3"
        no3_var.long_name = f"{river_key} NO3 concentration"
        no3_var[:] = load["no3_mmol"][:ndays+1]

        po4_var = ds.createVariable(f"{river_key}_phosphate", "f4", ("time",), fill_value=-999.0)
        po4_var.units = "mmol m-3"
        po4_var.long_name = f"{river_key} PO4 concentration"
        po4_var[:] = load["po4_mmol"][:ndays+1]

        pom_var = ds.createVariable(f"{river_key}_POM_sNW", "f4", ("time",), fill_value=-999.0)
        pom_var.units = "mmol m-3"
        pom_var.long_name = f"{river_key} POM N concentration"
        pom_var[:] = load["pom_mmol"][:ndays+1]

    ds.close()
    print(f"  已写入 rivers.nc ({ndays+1} 天)")

def read_meteo_data(ndays=20):
    df_atoms = pd.read_excel(INPUT_DIR / "Inputs.xlsx", sheet_name="Atoms")
    df_winds = pd.read_excel(INPUT_DIR / "Inputs.xlsx", sheet_name="Winds")

    df_atoms = df_atoms.iloc[:ndays].reset_index(drop=True)
    df_winds = df_winds.iloc[:ndays].reset_index(drop=True)

    meteo = {}
    meteo["patm"] = pd.to_numeric(df_atoms["PATM"], errors='coerce').fillna(1013.25).values * 100.0
    meteo["tdry"] = pd.to_numeric(df_atoms["TDRY"], errors='coerce').fillna(15.0).values
    meteo["relh"] = pd.to_numeric(df_atoms["RelH"], errors='coerce').fillna(0.7).values
    meteo["rain"] = pd.to_numeric(df_atoms["RAIN"], errors='coerce').fillna(0.0).values
    meteo["evap"] = pd.to_numeric(df_atoms["EVAP"], errors='coerce').fillna(0.0).values
    meteo["solar"] = pd.to_numeric(df_atoms["SOLAR"], errors='coerce').fillna(100.0).values
    meteo["cloud"] = pd.to_numeric(df_atoms["CLOUD"], errors='coerce').fillna(0.5).values

    meteo["wind_speed"] = pd.to_numeric(df_winds["Speed"], errors='coerce').fillna(2.0).values
    meteo["wind_dir"] = pd.to_numeric(df_winds["Dir "], errors='coerce').fillna(180.0).values

    meteo["wind_u"] = -meteo["wind_speed"] * np.sin(np.radians(meteo["wind_dir"]))
    meteo["wind_v"] = -meteo["wind_speed"] * np.cos(np.radians(meteo["wind_dir"]))

    print(f"  气温: {meteo['tdry'].mean():.1f} °C (范围: {meteo['tdry'].min():.1f}~{meteo['tdry'].max():.1f})")
    print(f"  风速: {meteo['wind_speed'].mean():.1f} m/s")
    print(f"  气压: {meteo['patm'].mean():.0f} Pa")

    return meteo

def write_meteo_nc(meteo, grid, ndays=20):
    nx, ny = grid["nx"], grid["ny"]
    ntimes = ndays * 24 + 1
    times = np.arange(ntimes) * 3600.0

    ds = nc.Dataset(str(CASE_DIR / "meteo.nc"), "w", format="NETCDF4")
    ds.createDimension("time", len(times))
    ds.createDimension("x", nx)
    ds.createDimension("y", ny)

    time_var = ds.createVariable("time", "f8", ("time",))
    time_var.units = "seconds since 2020-01-01 00:00:00"
    time_var.long_name = "time"
    time_var[:] = times

    temp_air = ds.createVariable("air_temp", "f4", ("time", "y", "x"))
    temp_air.units = "degC"
    temp_air.long_name = "air temperature"

    sp = ds.createVariable("mslp", "f4", ("time", "y", "x"))
    sp.units = "Pa"
    sp.long_name = "sea level pressure"

    wind_u = ds.createVariable("wind_u", "f4", ("time", "y", "x"))
    wind_u.units = "m s-1"
    wind_u.long_name = "u-component of wind"

    wind_v = ds.createVariable("wind_v", "f4", ("time", "y", "x"))
    wind_v.units = "m s-1"
    wind_v.long_name = "v-component of wind"

    cloud = ds.createVariable("cloud", "f4", ("time", "y", "x"))
    cloud.units = "0-1"
    cloud.long_name = "cloud cover"

    rain_var = ds.createVariable("precip", "f4", ("time", "y", "x"))
    rain_var.units = "m/s"
    rain_var.long_name = "precipitation rate"

    for t in range(ntimes):
        day_idx = min(t // 24, ndays - 1)

        temp_air[t, :, :] = meteo["tdry"][day_idx]
        sp[t, :, :] = meteo["patm"][day_idx]
        wind_u[t, :, :] = meteo["wind_u"][day_idx]
        wind_v[t, :, :] = meteo["wind_v"][day_idx]
        cloud[t, :, :] = np.clip(meteo["cloud"][day_idx], 0, 1)
        rain_var[t, :, :] = max(0, meteo["rain"][day_idx] / 86400.0)

    ds.close()
    print(f"  已写入 meteo.nc ({ntimes} 个时间步)")

def update_getm_inp(grid, ndays=20):
    nx, ny = grid["nx"], grid["ny"]
    inp_path = CASE_DIR / "getm.inp"

    with open(inp_path, "r") as f:
        content = f.read()

    import re

    content = re.sub(r'il\s*=\s*\d+', f'il = 1', content)
    content = re.sub(r'ih\s*=\s*\d+', f'ih = {nx}', content)
    content = re.sub(r'jl\s*=\s*\d+', f'jl = 1', content)
    content = re.sub(r'jh\s*=\s*\d+', f'jh = {ny}', content)
    content = re.sub(r'M\s*=\s*\d+', f'M = {NLEV}', content)
    content = re.sub(r'maxdepth\s*=\s*[\d.]+', f'maxdepth = 25.0', content)
    content = re.sub(r'min_depth\s*=\s*[\d.]+', f'min_depth = 0.5', content)
    content = re.sub(r'crit_depth\s*=\s*[\d.]+', f'crit_depth = 2.0', content)

    content = re.sub(r'river_method\s*=\s*\d+', 'river_method = 1', content)

    old_mm = re.search(r'MM\s*=\s*(\d+)', content)
    if old_mm:
        content = re.sub(r'MM\s*=\s*\d+', f'MM = {nx*ny}', content)

    content = re.sub(r'start\s*=\s*"[^"]*"', 'start = "2020-01-01 00:00:00"', content)
    content = re.sub(r'stop\s*=\s*"[^"]*"', f'stop = "2020-01-{1+ndays} 00:00:00"', content)

    with open(inp_path, "w") as f:
        f.write(content)

    print(f"  已更新 getm.inp (nx={nx}, ny={ny}, nlev={NLEV}, {ndays}天)")

def main():
    ndays = 20

    print("=" * 70)
    print("  骆马湖模型数据生成（基于真实地形和实测数据）")
    print("=" * 70)

    print("\n1. 生成地形文件（从 Bottom_Elev.p2d 插值）...")
    grid = generate_grid_and_bathymetry()
    write_bathy_nc(grid)

    print("\n2. 确定河道位置...")
    rivers = find_river_locations(grid)
    write_riverinfo(rivers)

    print("\n3. 读取流量数据...")
    flow_data = read_flow_data(ndays)

    print("\n4. 生成河流边界条件...")
    write_rivers_nc(flow_data, ndays)

    print("\n5. 读取并生成气象强迫...")
    meteo = read_meteo_data(ndays)
    write_meteo_nc(meteo, grid, ndays)

    print("\n6. 更新模型配置...")
    update_getm_inp(grid, ndays)

    print("\n" + "=" * 70)
    print("  ✅ 数据生成完成！")
    print(f"   输出目录: {CASE_DIR}")
    print("=" * 70)

if __name__ == "__main__":
    main()
