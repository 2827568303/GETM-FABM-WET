import numpy as np
import openpyxl
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent
CASE_DIR = BASE_DIR / "luomahu_case"
CASE_DIR.mkdir(exist_ok=True)

NX = 50
NY = 46
DX = 500.0
DY = 500.0
NLEV = 5

LON0 = 118.07
LAT0 = 34.00
DLON = 0.26
DLAT = 0.24

xc = np.linspace(DX/2, (NX-0.5)*DX, NX)
yc = np.linspace(DY/2, (NY-0.5)*DY, NY)
lon = LON0 + np.linspace(0, DLON, NX)
lat = LAT0 + np.linspace(0, DLAT, NY)

def lonlat_to_xy(lon_p, lat_p):
    i = int((lon_p - LON0) / DLON * NX)
    j = int((lat_p - LAT0) / DLAT * NY)
    return i, j

def make_bathymetry():
    bathy = np.ones((NY, NX)) * 2.0

    cx, cy = NX * 0.45, NY * 0.5
    rx = NX * 0.42
    ry = NY * 0.45

    for j in range(NY):
        for i in range(NX):
            nx = (i - cx) / rx
            ny = (j - cy) / ry
            r = nx**2 + ny**2
            if r < 1.0:
                edge_factor = 1.0 - r
                depth = 2.0 + 4.0 * edge_factor**0.6
                bathy[j, i] = depth
            else:
                bathy[j, i] = 0.0

    north_inlet_start = int(NY * 0.35)
    north_inlet_end = int(NY * 0.65)
    inlet_width = 3
    for j in range(north_inlet_start, north_inlet_end):
        for i in range(inlet_width):
            if bathy[j, i] > 0:
                bathy[j, i] = max(bathy[j, i], 3.0)
            else:
                bathy[j, i] = 3.0

    south_outlet_j = int(NY * 0.5)
    for j in range(south_outlet_j - 2, south_outlet_j + 2):
        for i in range(NX-4, NX):
            if bathy[j, i] > 0:
                bathy[j, i] = max(bathy[j, i], 3.0)
            else:
                bathy[j, i] = 3.0

    return bathy

def write_bathy_nc(bathy):
    try:
        import netCDF4 as nc
    except ImportError:
        return

    ds = nc.Dataset(str(CASE_DIR / "bathymetry.nc"), "w", format="NETCDF4")

    ds.createDimension("x", NX)
    ds.createDimension("y", NY)

    grid_type = ds.createVariable("grid_type", "i4")
    grid_type.long_name = "grid type"
    grid_type[:] = 1

    x_var = ds.createVariable("x", "f4", ("x",))
    x_var.units = "m"
    x_var.long_name = "x-coordinate"
    x_var[:] = xc

    y_var = ds.createVariable("y", "f4", ("y",))
    y_var.units = "m"
    y_var.long_name = "y-coordinate"
    y_var[:] = yc

    lonc_var = ds.createVariable("lonc", "f8", ("y", "x"))
    lonc_var.units = "degrees_east"
    lonc_var.long_name = "longitude"
    for j in range(NY):
        for i in range(NX):
            lonc_var[j, i] = LON0 + i / (NX-1) * DLON

    latc_var = ds.createVariable("latc", "f8", ("y", "x"))
    latc_var.units = "degrees_north"
    latc_var.long_name = "latitude"
    for j in range(NY):
        for i in range(NX):
            latc_var[j, i] = LAT0 + j / (NY-1) * DLAT

    bathy_var = ds.createVariable("bathymetry", "f4", ("y", "x"), fill_value=-10.0)
    bathy_var.units = "m"
    bathy_var.long_name = "bathymetry"
    bathy_var.missing_value = -10.0
    bathy_var.valid_range = [-5., 13000.]

    for j in range(NY):
        for i in range(NX):
            if bathy[j, i] <= 0:
                bathy_var[j, i] = -10.0
            else:
                bathy_var[j, i] = bathy[j, i]

    ds.close()
    print(f"  水深范围: {bathy[bathy>0].min():.2f} ~ {bathy.max():.2f} m")
    print(f"  水域格数: {np.sum(bathy > 0)}")
    print(f"  水域面积: {np.sum(bathy > 0) * DX * DY / 1e6:.2f} km²")

def read_excel_data():
    """读取Excel文件中的骆马湖数据
    L1=大运河, L2=沂河, L3=骆南中运河(入流)
    L4=气象, L5=三场流速, L6=三场水质, L7=Chl-a
    """
    xlsx_path = r"c:\Users\dinod\Desktop\封装函数\Luomahu-sanchang.xlsx"
    
    try:
        wb = openpyxl.load_workbook(xlsx_path, data_only=True)
        ws = wb["三场点位数据"]
    except Exception as e:
        print(f"  警告: 无法读取Excel文件: {e}")
        return None

    dates = []
    # L1-L3 入流数据
    q_l1, q_l2, q_l3 = [], [], []  # 大运河, 沂河, 骆南中运河
    tn_l1, tn_l2, tn_l3 = [], [], []  # 总氮
    tp_l1, tp_l2, tp_l3 = [], [], []  # 总磷
    # L4 气象数据
    air_temp, rain, wind, wind_dir = [], [], [], []
    # L5 三场水文
    water_temp, flow_vel, flow_dir = [], [], []
    # L6 三场水质
    nh4, no3, po4 = [], [], []
    # L7 Chl-a
    chla = []

    for row in ws.iter_rows(min_row=3, max_row=ws.max_row, values_only=True):
        if row[0] is None:
            continue
        dates.append(row[0])
        # 入流流量 (m³/s)
        q_l1.append(row[1] if row[1] is not None else 0.0)
        q_l2.append(row[2] if row[2] is not None else 0.0)
        q_l3.append(row[3] if row[3] is not None else 0.0)
        # 总氮 (mg/L)
        tn_l1.append(row[4] if row[4] is not None else 1.0)
        tn_l2.append(row[5] if row[5] is not None else 5.0)
        tn_l3.append(row[6] if row[6] is not None else 1.0)
        # 总磷 (mg/L)
        tp_l1.append(row[7] if row[7] is not None else 0.05)
        tp_l2.append(row[8] if row[8] is not None else 0.05)
        tp_l3.append(row[9] if row[9] is not None else 0.05)
        # 气象
        air_temp.append(row[10] if row[10] is not None else 15.0)
        rain.append(row[11] if row[11] is not None else 0.0)
        wind.append(row[12] if row[12] is not None else 2.0)
        wind_dir.append(row[13] if row[13] is not None else 180.0)
        # 三场水文
        water_temp.append(row[14] if row[14] is not None else 15.0)
        flow_vel.append(row[15] if row[15] is not None else 0.0)
        flow_dir.append(row[16] if row[16] is not None else 0.0)
        # 三场水质
        nh4.append(row[17] if row[17] is not None else 0.02)
        no3.append(row[18] if row[18] is not None else 0.5)
        po4.append(row[19] if row[19] is not None else 0.01)
        # Chl-a
        chla.append(row[20] if row[20] is not None else 5.0)

    return {
        "dates": dates,
        # 入流
        "q_l1": np.array(q_l1), "q_l2": np.array(q_l2), "q_l3": np.array(q_l3),
        "tn_l1": np.array(tn_l1), "tn_l2": np.array(tn_l2), "tn_l3": np.array(tn_l3),
        "tp_l1": np.array(tp_l1), "tp_l2": np.array(tp_l2), "tp_l3": np.array(tp_l3),
        # 气象
        "air_temp": np.array(air_temp), "rain": np.array(rain),
        "wind": np.array(wind), "wind_dir": np.array(wind_dir),
        # 三场水文
        "water_temp": np.array(water_temp),
        "flow_vel": np.array(flow_vel), "flow_dir": np.array(flow_dir),
        # 三场水质
        "nh4": np.array(nh4), "no3": np.array(no3), "po4": np.array(po4),
        # Chl-a
        "chla": np.array(chla),
    }

def write_meteo_data(data, ndays=20):
    try:
        import netCDF4 as nc
    except ImportError:
        return

    times = np.arange(ndays * 24 + 1) * 3600.0

    ds = nc.Dataset(str(CASE_DIR / "meteo.nc"), "w", format="NETCDF4")
    ds.createDimension("time", len(times))
    ds.createDimension("x", NX)
    ds.createDimension("y", NY)

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

    for t in range(len(times)):
        day_idx = min(t // 24, ndays - 1)
        day_idx = min(day_idx, len(data["air_temp"]) - 1)

        temp_val = data["air_temp"][day_idx]
        wind_val = data["wind"][day_idx]
        wind_d = data["wind_dir"][day_idx] * np.pi / 180.0
        rain_val = data["rain"][day_idx] / 86400.0

        u_val = -wind_val * np.sin(wind_d)
        v_val = -wind_val * np.cos(wind_d)

        temp_air[t, :, :] = temp_val
        sp[t, :, :] = 101325.0
        wind_u[t, :, :] = u_val
        wind_v[t, :, :] = v_val
        cloud[t, :, :] = 0.3
        rain_var[t, :, :] = max(0, rain_val)

    ds.close()
    print(f"  气象数据: {len(times)} 个时间步")

def write_rivers_nc(data, ndays=20):
    """生成河流边界条件NetCDF文件

    GETM 河流 NetCDF 格式:
    - time 是 unlimited 维度
    - 每条河流主变量名就是河流名 (流量 m³/s)
    - 正流量=入流，负流量=出流
    - 出流通过水量平衡自动计算: 总出流 = 总入流
    """
    try:
        import netCDF4 as nc
    except ImportError:
        return

    times = np.arange(ndays + 1) * 86400.0  # 日数据

    ds = nc.Dataset(str(CASE_DIR / "rivers.nc"), "w", format="NETCDF4")

    # time 必须是 unlimited dimension
    ds.createDimension("time", None)

    # 时间
    time_var = ds.createVariable("time", "f8", ("time",))
    time_var.units = "seconds since 2020-01-01 00:00:00"
    time_var.long_name = "time"
    time_var[:] = times

    # 入流河流配置: (变量名前缀, 流量数据key, TN数据key, TP数据key)
    inflows = [
        ("DAYUN",  "q_l1", "tn_l1", "tp_l1"),   # 大运河
        ("YIHE",   "q_l2", "tn_l2", "tp_l2"),   # 沂河
        ("LUONAN", "q_l3", "tn_l3", "tp_l3"),   # 骆南中运河
    ]

    # 出流河流配置: (变量名, 位置描述)
    # 骆马湖主要出流：
    # - 嶂山闸(ZHANGSHAN): 湖东南侧，新沂河出口
    # - 洋河滩闸(YANGHE): 湖东侧
    # - 二河闸(ERHE): 湖东北侧
    outflows = [
        ("ZHANGSHAN", "东南侧，新沂河出口"),   # 最大出流
        ("YANGHE",    "东侧，洋河滩闸"),       # 第二出流
        ("ERHE",      "东北侧，二河闸"),       # 第三出流
    ]

    # 计算每日入流量
    inflow_daily = np.zeros(ndays + 1)
    for river_name, q_key, tn_key, tp_key in inflows:
        inflow_daily += data[q_key][:ndays+1]

    # 出流量按比例分配，保持水量平衡
    # ZHANGSHAN: 60%, YANGHE: 25%, ERHE: 15%
    outflow_ratio = np.array([0.60, 0.25, 0.15])

    # 入流数据
    inflow_values = []
    for idx, (river_name, q_key, tn_key, tp_key) in enumerate(inflows):
        # 使用Excel数据作为入流（clip到正值，避免负流量）
        flow = np.clip(data[q_key][:ndays+1], 0, 5000.0)
        q_var = ds.createVariable(river_name, "f4", ("time",), fill_value=-999.0)
        q_var.units = "m3 s-1"
        q_var.long_name = f"{river_name} discharge (inflow)"
        q_var[:] = flow
        inflow_values.append(flow)

        # 温度属性
        q_var.temp = 0

        # FABM 状态变量 - NH4
        nh4_var = ds.createVariable(
            f"{river_name}_ammonium", "f4", ("time",), fill_value=-999.0
        )
        nh4_var.units = "mmol m-3"
        nh4_var.long_name = f"{river_name} NH4 concentration"
        nh4_var[:] = data[tn_key][:ndays+1] / 14.0 * 1000.0 * 0.1

        # FABM 状态变量 - NO3
        no3_var = ds.createVariable(
            f"{river_name}_nitrate", "f4", ("time",), fill_value=-999.0
        )
        no3_var.units = "mmol m-3"
        no3_var.long_name = f"{river_name} NO3 concentration"
        no3_var[:] = data[tn_key][:ndays+1] / 14.0 * 1000.0 * 0.8

        # FABM 状态变量 - PO4
        po4_var = ds.createVariable(
            f"{river_name}_phosphate", "f4", ("time",), fill_value=-999.0
        )
        po4_var.units = "mmol m-3"
        po4_var.long_name = f"{river_name} PO4 concentration"
        po4_var[:] = data[tp_key][:ndays+1] / 31.0 * 1000.0

        # FABM 状态变量 - POM
        pom_var = ds.createVariable(
            f"{river_name}_POM_sNW", "f4", ("time",), fill_value=-999.0
        )
        pom_var.units = "mmol m-3"
        pom_var.long_name = f"{river_name} POM N concentration"
        pom_var[:] = data[tn_key][:ndays+1] / 14.0 * 1000.0 * 0.1

    # 出流暂时禁用 - 仅测试入流配置
    # 骆马湖主要出流：
    # - 嶂山闸(ZHANGSHAN): 湖东南侧，新沂河出口
    # - 洋河滩闸(YANGHE): 湖东侧
    # - 二河闸(ERHE): 湖东北侧
    # 出流量按比例分配，保持水量平衡
    # ZHANGSHAN: 60%, YANGHE: 25%, ERHE: 15%
    # outflow_ratio = np.array([0.60, 0.25, 0.15])
    # outflow_data = np.zeros((len(outflows), ndays + 1))
    # for idx, (river_name, desc) in enumerate(outflows):
    #     outflow_data[idx] = -inflow_daily * outflow_ratio[idx]
    #     q_var = ds.createVariable(river_name, "f4", ("time",), fill_value=-999.0)
    #     q_var.units = "m3 s-1"
    #     q_var.long_name = f"{river_name} discharge (outflow: {desc})"
    #     q_var[:] = outflow_data[idx]
    #     q_var.temp = 0
    #     for suffix, default_val in [("ammonium", 0.1), ("nitrate", 0.5), ("phosphate", 0.01), ("POM_sNW", 0.05)]:
    #         var = ds.createVariable(f"{river_name}_{suffix}", "f4", ("time",), fill_value=-999.0)
    #         var.units = "mmol m-3"
    #         var.long_name = f"{river_name} {suffix} concentration"
    #         var[:] = default_val

    ds.close()

    # 打印水量平衡信息
    total_inflow = np.sum(inflow_values)
    print(f"  河流边界条件: {ndays+1} 天")
    print(f"  入流: {', '.join(r[0] for r in inflows)}")
    print(f"  日均入流: {inflow_daily.mean():.1f} m³/s")

def main():
    print("=" * 60)
    print("  骆马湖模型数据生成")
    print("=" * 60)

    print("\n1. 生成地形文件...")
    bathy = make_bathymetry()
    write_bathy_nc(bathy)

    print("\n2. 读取Excel数据...")
    data = read_excel_data()
    if data is None:
        return
    print(f"  数据条数: {len(data['dates'])}")
    print(f"  时间范围: {data['dates'][0]} ~ {data['dates'][-1]}")
    print(f"  流量范围: L1={data['q_l1'].mean():.1f}, L2={data['q_l2'].mean():.1f}, L3={data['q_l3'].mean():.1f} m³/s")
    print(f"  TN范围: L1={data['tn_l1'].mean():.2f}, L2={data['tn_l2'].mean():.2f}, L3={data['tn_l3'].mean():.2f} mg/L")
    print(f"  TP范围: L1={data['tp_l1'].mean():.3f}, L2={data['tp_l2'].mean():.3f}, L3={data['tp_l3'].mean():.3f} mg/L")
    print(f"  气温范围: {data['air_temp'].min():.1f} ~ {data['air_temp'].max():.1f} °C")

    print("\n3. 生成气象数据...")
    write_meteo_data(data, ndays=20)

    print("\n4. 生成河流边界条件...")
    write_rivers_nc(data, ndays=20)

    print("\n5. 三场点位坐标换算...")
    # 根据骆马湖形状和大运河入流位置设定
    # L1大运河: 湖西侧 (约118.07°E)
    # L2沂河: 湖西北侧 (约118.08°E, 34.10°N)
    # L3骆南中运河: 湖南侧
    # 三场: 湖中深水区 (约118.19°E, 34.07°N)
    sanchang_lon = 118.19
    sanchang_lat = 34.07
    i_san, j_san = lonlat_to_xy(sanchang_lon, sanchang_lat)
    print(f"  三场点位: 经度={sanchang_lon}°, 纬度={sanchang_lat}°")
    print(f"  网格位置: i={i_san}, j={j_san}")
    if 0 <= j_san < NY and 0 <= i_san < NX:
        print(f"  当地水深: {bathy[j_san, i_san]:.2f} m")
    else:
        print(f"  警告: 点位超出湖体范围!")

    print("\n✅ 数据生成完成！")
    print(f"   输出目录: {CASE_DIR}")

if __name__ == "__main__":
    main()
