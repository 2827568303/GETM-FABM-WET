"""3DWET 前处理模块 - 从lake_config.yaml生成所有输入数据文件

Usage:
    python preprocess.py <lake_config.yaml> [--output-dir <dir>]

Inputs:
    lake_config.yaml - 湖泊配置文件（参考templates/lake_config.yaml）

Outputs (4 files):
    bathymetry.nc  - 湖底地形
    meteo.nc       - 气象强迫
    rivers.nc      - 河流数据
    fabm_init.nc   - 生态初始化场
    riverinfo.dat  - 河流位置信息
    meteo_input.txt - 气象文件名
"""
import os
import sys
import math
import argparse
import numpy as np
import netCDF4 as nc
from datetime import datetime, timedelta


def load_config(config_path):
    """Load YAML configuration file."""
    import yaml
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def utm_to_latlon(x_utm, y_utm, zone_number=48, northern=True):
    """Convert UTM to lat/lon (simplified for lake-scale)."""
    lat0 = y_utm / 111000.0
    lon0 = x_utm / (111000.0 * math.cos(math.radians(lat0)))
    return lat0, lon0


# ============================================================
# 1. Bathymetry generation
# ============================================================
def generate_bathymetry(config, output_dir):
    """Generate bathymetry.nc from lake configuration."""
    print("\n[1/4] Generating bathymetry.nc ...")

    lake = config['lake']
    grid = config['grid']
    shape = config['shape']
    bathy_cfg = config['bathymetry']

    NX, NY = grid['nx'], grid['ny']
    DX, DY = grid['dx'], grid['dy']

    # UTM origin (arbitrary, just for coordinate consistency)
    lat0 = lake['latitude']
    lon0 = lake['longitude']
    X0_UTM = 500000.0 + lon0 * 111000.0 * math.cos(math.radians(lat0))
    Y0_UTM = lat0 * 111000.0

    # --- Generate lake mask ---
    lake_mask = np.zeros((NY, NX), dtype=bool)
    cx = (NX - 1) / 2.0

    if shape['mode'] == 'rectangle':
        lake_mask[:, :] = True
    elif shape['mode'] == 'oval':
        width_ratio = shape.get('width_ratio', 0.9)
        for j in range(NY):
            cy_norm = (j - (NY - 1) / 2.0) / ((NY - 1) / 2.0)  # -1 to 1
            for i in range(NX):
                dx_norm = (i - cx) / cx if cx > 0 else 0
                half_width = 0.5 + (width_ratio - 0.5) * math.cos(dx_norm * math.pi * 0.8)
                half_width = max(0.05, min(1.0, half_width))
                if abs(cy_norm) <= half_width:
                    lake_mask[j, i] = True
    elif shape['mode'] == 'custom':
        mask_file = shape.get('mask_file')
        if mask_file and os.path.exists(mask_file):
            lake_mask = np.load(mask_file).astype(bool)
        else:
            raise ValueError(f"Custom shape requires mask_file, got: {mask_file}")

    n_water = lake_mask.sum()
    if n_water == 0:
        raise ValueError("No water cells in lake mask! Check shape configuration.")

    # --- Generate bathymetry ---
    bathymetry = np.full((NY, NX), -9999.0)
    avg_depth = bathy_cfg['avg_depth']
    max_depth = bathy_cfg['max_depth']
    min_depth = bathy_cfg['min_depth']
    profile = bathy_cfg.get('depth_profile', 'center_deep')

    for j in range(NY):
        for i in range(NX):
            if not lake_mask[j, i]:
                continue
            dx_norm = (i - cx) / cx if cx > 0 else 0
            cy_lake = (NY - 1) / 2.0
            half_width = 0.5 + (0.9 - 0.5) * math.cos(dx_norm * math.pi * 0.8)
            half_width = max(0.05, min(1.0, half_width))
            dy_norm = abs(j - cy_lake) / (cy_lake * half_width) if cy_lake > 0 else 0

            if profile == 'center_deep':
                depth_factor = 1.0 - 0.7 * dy_norm**2
                ew_factor = 1.0
            elif profile == 'east_deep':
                depth_factor = 1.0 - 0.7 * dy_norm**2
                ew_factor = 1.0 + 0.1 * dx_norm
            elif profile == 'uniform':
                depth_factor = 1.0
                ew_factor = 1.0
            else:
                depth_factor = 1.0 - 0.7 * dy_norm**2
                ew_factor = 1.0

            base_depth = max_depth * depth_factor * ew_factor
            bathymetry[j, i] = max(min_depth, min(max_depth, base_depth))

    # Adjust to target average depth
    water_depths = bathymetry[lake_mask]
    current_avg = water_depths.mean()
    if current_avg > 0:
        scale = avg_depth / current_avg
        bathymetry[lake_mask] = np.clip(bathymetry[lake_mask] * scale, min_depth, max_depth)

    # --- Write NetCDF ---
    bathy_path = os.path.join(output_dir, 'bathymetry.nc')
    ds = nc.Dataset(bathy_path, 'w', format='NETCDF4')
    ds.createDimension('x', NX)
    ds.createDimension('y', NY)
    ds.createDimension('xq', NX + 1)
    ds.createDimension('yq', NY + 1)

    grid_type = ds.createVariable('grid_type', 'i4')
    grid_type[:] = 1

    x_var = ds.createVariable('x', 'f8', ('x',))
    x_var.units = 'm'
    x_var.long_name = 'x coordinate of cell centers'
    x_var[:] = X0_UTM + np.arange(NX) * DX + DX / 2

    y_var = ds.createVariable('y', 'f8', ('y',))
    y_var.units = 'm'
    y_var.long_name = 'y coordinate of cell centers'
    y_var[:] = Y0_UTM + np.arange(NY) * DY + DY / 2

    lat_var = ds.createVariable('latc', 'f8', ('y', 'x'))
    lat_var.units = 'degrees_north'
    lat_var.long_name = 'latitude of cell centers'
    for j in range(NY):
        lat_var[j, :] = lat0 + ((NY - 1) / 2.0 - j) * (DY / 111000.0)

    lon_var = ds.createVariable('lonc', 'f8', ('y', 'x'))
    lon_var.units = 'degrees_east'
    lon_var.long_name = 'longitude of cell centers'
    cos_lat = math.cos(math.radians(lat0))
    for i in range(NX):
        lon_var[:, i] = lon0 + (i - (NX - 1) / 2.0) * (DX / (111000.0 * cos_lat))

    bath_var = ds.createVariable('bathymetry', 'f8', ('y', 'x'))
    bath_var.units = 'm'
    bath_var.long_name = 'water depth'
    bath_var.standard_name = 'sea_floor_depth'
    bath_var.coordinates = 'lonc latc'
    bath_var[:] = bathymetry

    ds.title = f'{lake["name"]} Bathymetry'
    ds.source = 'Generated by 3DWET preprocess module'
    ds.history = f'Created {datetime.now()}'
    ds.Conventions = 'CF-1.0'

    # Save arrays before closing dataset
    latc_2d = lat_var[:].copy()
    lonc_2d = lon_var[:].copy()
    ds.close()

    lake_area = n_water * DX * DY
    lake_volume = np.sum(bathymetry[lake_mask]) * DX * DY
    print(f"  Water cells: {n_water}/{NX*NY} ({n_water/(NX*NY)*100:.1f}%)")
    print(f"  Lake area: {lake_area/1e6:.2f} km²")
    print(f"  Avg depth: {bathymetry[lake_mask].mean():.2f} m")
    print(f"  Max depth: {bathymetry[lake_mask].max():.2f} m")
    print(f"  Volume: {lake_volume/1e6:.1f} Mm³")
    print(f"  Saved: {bathy_path}")

    return bathymetry, lake_mask, latc_2d, lonc_2d


# ============================================================
# 2. Meteorology generation
# ============================================================
def generate_meteo(config, output_dir, latc_2d, lonc_2d):
    """Generate meteo.nc from climate configuration."""
    print("\n[2/4] Generating meteo.nc ...")

    lake = config['lake']
    grid = config['grid']
    meteo_cfg = config['meteo']

    NX, NY = grid['nx'], grid['ny']
    n_days = meteo_cfg['n_days']
    mode = meteo_cfg['mode']

    if mode == 'synthetic':
        climate = meteo_cfg['climate']
        days = np.arange(n_days)

        avg_temp = climate['avg_temp']
        temp_amp = climate['temp_amplitude']
        temp_peak = climate['temp_peak_day']
        annual_precip_mm = climate['annual_precip']
        annual_evap_mm = climate['annual_evap']
        wet_start, wet_end = climate['wet_season']
        precip_ratio = climate['wet_season_precip_ratio']

        # Temperature: sinusoidal
        temp = avg_temp + temp_amp * np.sin(2 * np.pi * (days - (temp_peak - 90)) / 365.0)

        # Precipitation: wet season concentration
        precip_daily = np.zeros(n_days)
        wet_days = sum(1 for d in range(n_days) if wet_start <= d <= wet_end)
        dry_days = n_days - wet_days
        wet_total = annual_precip_mm * precip_ratio
        dry_total = annual_precip_mm * (1 - precip_ratio)
        for d in range(n_days):
            if wet_start <= d <= wet_end:
                np.random.seed(d)
                precip_daily[d] = max(0, wet_total / wet_days + np.random.exponential(2.0))
            else:
                np.random.seed(d + 10000)
                precip_daily[d] = max(0, dry_total / max(dry_days, 1) + np.random.exponential(0.3))
        precip_mms = precip_daily / 86400.0 / 1000.0  # m/s

        # Evaporation: opposite phase to precip
        evap_daily = np.zeros(n_days)
        for d in range(n_days):
            if wet_start <= d <= wet_end:
                evap_daily[d] = annual_evap_mm * (1 - precip_ratio) / max(wet_days, 1)
            else:
                evap_daily[d] = annual_evap_mm * precip_ratio / max(dry_days, 1)
            evap_daily[d] *= (1 + 0.3 * math.sin(2 * math.pi * (d - 60) / 365.0))
        evap_daily = np.maximum(evap_daily, 0)
        evap_mms = -evap_daily / 86400.0 / 1000.0  # negative = loss

        # Wind
        wind_dir = climate.get('wind_direction', 'variable')
        if wind_dir == 'monsoon':
            u10 = np.array([climate['avg_wind_speed'] * math.sin(2 * math.pi * (d - 150) / 365.0) for d in range(n_days)])
            v10 = np.array([climate['avg_wind_speed'] * 0.6 * math.cos(2 * math.pi * (d - 150) / 365.0) for d in range(n_days)])
        else:
            u10 = np.full(n_days, climate['avg_wind_speed'])
            v10 = np.zeros(n_days)

        # Other
        elevation = lake.get('elevation', 0)
        slp = np.full(n_days, 101325.0 * (1 - 2.25577e-5 * elevation)**5.25588)
        rh = np.clip(np.full(n_days, climate['avg_humidity']) +
                     15 * np.sin(2 * np.pi * (days - 200) / 365.0), 30, 95)
        tcc = np.clip(np.full(n_days, climate['avg_cloud_cover']) +
                      0.2 * np.sin(2 * math.pi * (days - 200) / 365.0), 0.1, 0.9)

    elif mode == 'file':
        # Read from external NetCDF file
        file_path = meteo_cfg['file_path']
        ds_in = nc.Dataset(file_path, 'r')
        temp = to_np(ds_in.variables['t2'][:])
        u10 = to_np(ds_in.variables['u10'][:])
        v10 = to_np(ds_in.variables['v10'][:])
        slp = to_np(ds_in.variables['slp'][:])
        rh = to_np(ds_in.variables['rh'][:])
        tcc = to_np(ds_in.variables['tcc'][:])
        precip_mms = to_np(ds_in.variables['precip'][:])
        evap_mms = to_np(ds_in.variables['evap'][:])
        ds_in.close()
        n_days = len(temp)
    else:
        raise ValueError(f"Unknown meteo mode: {mode}")

    # Write meteo.nc (C order: time, lat, lon)
    meteo_path = os.path.join(output_dir, 'meteo.nc')
    ds = nc.Dataset(meteo_path, 'w', format='NETCDF4')
    ds.createDimension('lon', NX)
    ds.createDimension('lat', NY)
    ds.createDimension('time', n_days)

    lon_1d = latc_2d[0, :] if len(latc_2d.shape) == 2 else latc_2d
    lat_1d = lonc_2d[:, 0] if len(lonc_2d.shape) == 2 else lonc_2d
    # Fix: latc varies along y (rows), lonc varies along x (cols)
    lat_1d = latc_2d[:, 0] if len(latc_2d.shape) == 2 else latc_2d
    lon_1d = lonc_2d[0, :] if len(lonc_2d.shape) == 2 else lonc_2d

    lon_v = ds.createVariable('lon', 'f8', ('lon',))
    lon_v.units = 'degrees_east'
    lon_v[:] = lon_1d

    lat_v = ds.createVariable('lat', 'f8', ('lat',))
    lat_v.units = 'degrees_north'
    lat_v[:] = lat_1d

    time_v = ds.createVariable('time', 'f8', ('time',))
    time_v.units = f'seconds since {meteo_cfg["start_date"]} 00:00:00'
    time_v[:] = np.arange(n_days) * 86400.0

    # f32 variables
    for var_name, units, long_name, data in [
        ('u10', 'm s-1', '10m wind u-component', u10),
        ('v10', 'm s-1', '10m wind v-component', v10),
        ('slp', 'Pa', 'sea level pressure', slp),
        ('t2', 'degC', '2m air temperature', temp),
        ('rh', '1', 'relative humidity', rh),
        ('tcc', '1', 'total cloud cover', tcc),
    ]:
        var = ds.createVariable(var_name, 'f4', ('time', 'lat', 'lon'))
        var.units = units
        var.long_name = long_name
        if len(data.shape) == 1:
            var[:] = np.broadcast_to(data[:, np.newaxis, np.newaxis], (n_days, NY, NX))
        else:
            var[:] = data

    # f64 variables (CRITICAL: precip/evap must be float64!)
    for var_name, units, long_name, data in [
        ('precip', 'm s-1', 'precipitation rate', precip_mms),
        ('evap', 'm s-1', 'evaporation rate (negative = water loss)', evap_mms),
    ]:
        var = ds.createVariable(var_name, 'f8', ('time', 'lat', 'lon'))
        var.units = units
        var.long_name = long_name
        if len(data.shape) == 1:
            var[:] = np.broadcast_to(data[:, np.newaxis, np.newaxis], (n_days, NY, NX))
        else:
            var[:] = data

    ds.title = f'{lake["name"]} meteorology'
    ds.close()

    if mode == 'synthetic':
        print(f"  Temperature: avg={temp.mean():.1f}°C, range=[{temp.min():.1f}, {temp.max():.1f}]")
        print(f"  Precip: total={precip_daily.sum():.0f} mm/yr")
        print(f"  Evap:   total={evap_daily.sum():.0f} mm/yr")
        print(f"  P-E:    {(precip_daily.sum()-evap_daily.sum()):.0f} mm/yr")
    print(f"  Saved: {meteo_path}")

    # Write meteo_input.txt
    meteo_input_path = os.path.join(output_dir, 'meteo_input.txt')
    with open(meteo_input_path, 'w') as f:
        f.write('meteo.nc\n')
    print(f"  Saved: {meteo_input_path}")

    return precip_mms, evap_mms


# ============================================================
# 3. Rivers generation
# ============================================================
def find_edge_cell(side, lake_mask):
    """Find a water cell on the specified edge (or closest water row/col)."""
    NY_l, NX_l = lake_mask.shape
    if side == 'north':
        for j in range(NY_l):
            water_is = [i for i in range(NX_l) if lake_mask[j, i]]
            if water_is:
                return water_is[len(water_is)//2], j
    elif side == 'south':
        for j in range(NY_l - 1, -1, -1):
            water_is = [i for i in range(NX_l) if lake_mask[j, i]]
            if water_is:
                return water_is[len(water_is)//2], j
    elif side == 'west':
        for i in range(NX_l):
            water_js = [j for j in range(NY_l) if lake_mask[j, i]]
            if water_js:
                return i, water_js[len(water_js)//2]
    elif side == 'east':
        for i in range(NX_l - 1, -1, -1):
            water_js = [j for j in range(NY_l) if lake_mask[j, i]]
            if water_js:
                return i, water_js[len(water_js)//2]
    return None


def generate_rivers(config, output_dir, lake_mask, bathymetry, lake_area, precip_mms, evap_mms):
    """Generate rivers.nc and riverinfo.dat from river configuration."""
    print("\n[3/4] Generating rivers.nc and riverinfo.dat ...")

    grid = config['grid']
    NX, NY = grid['nx'], grid['ny']
    n_days = config['meteo']['n_days']
    rivers_cfg = config['rivers']

    # Resolve river positions
    river_positions = []
    for river in rivers_cfg:
        pos = river['position']
        if isinstance(pos, str):
            cell = find_edge_cell(pos, lake_mask)
            if cell is None:
                raise ValueError(f"Cannot find water cell on {pos} edge for river {river['name']}")
            i_1based, j_1based = cell[0] + 1, cell[1] + 1
        elif isinstance(pos, list) and len(pos) == 2:
            i_1based, j_1based = pos[0], pos[1]
        else:
            raise ValueError(f"Invalid position for river {river['name']}: {pos}")
        river_positions.append((river, i_1based, j_1based))
        print(f"  {river['name']} ({river['type']}): ({i_1based},{j_1based}) - {pos}")

    # Compute discharge time series
    discharge = {r['name']: np.zeros(n_days) for r in rivers_cfg}
    wet_season = config['meteo'].get('climate', {}).get('wet_season', [120, 300])

    for river in rivers_cfg:
        name = river['name']
        rtype = river['type']
        base_flow = river.get('base_flow', 0)
        amp = river.get('seasonal_amplitude', 0)
        wet_start, wet_end = river.get('wet_season', wet_season)

        if rtype == 'inflow' and base_flow is not None:
            for day in range(n_days):
                if wet_start <= day <= wet_end:
                    seasonal = 1.0 + amp * math.sin(2 * math.pi * (day - wet_start) / max(1, wet_end - wet_start))
                else:
                    seasonal = 1.0 - amp * 0.5
                discharge[name][day] = base_flow * seasonal

    # Compute outflow from water balance
    total_inflow_per_day = np.zeros(n_days)
    for river in rivers_cfg:
        if river['type'] == 'inflow':
            total_inflow_per_day += discharge[river['name']]

    precip_vol_per_day = np.maximum(precip_mms, 0) * lake_area
    evap_vol_per_day = np.maximum(-evap_mms, 0) * lake_area
    net_outflow = total_inflow_per_day + precip_vol_per_day - evap_vol_per_day

    for river in rivers_cfg:
        if river['type'] == 'outflow':
            name = river['name']
            base_flow = river.get('base_flow')
            if base_flow is None:
                discharge[name] = -np.maximum(0.1, net_outflow)
            else:
                discharge[name] = -base_flow

    # Water balance check
    total_in = sum(d.sum() for r in rivers_cfg if r['type'] == 'inflow' for d in [discharge[r['name']]]) * 86400
    total_out = sum(-d.sum() for r in rivers_cfg if r['type'] == 'outflow' for d in [discharge[r['name']]]) * 86400
    precip_vol = precip_mms.sum() * lake_area * 86400
    evap_vol = (-evap_mms).sum() * lake_area * 86400
    balance = total_in + precip_vol - total_out - evap_vol
    print(f"  Water balance (366 days):")
    print(f"    Inflow:  {total_in/1e6:.2f} Mm³")
    print(f"    Precip:  {precip_vol/1e6:.2f} Mm³")
    print(f"    Outflow: {total_out/1e6:.2f} Mm³")
    print(f"    Evap:    {evap_vol/1e6:.2f} Mm³")
    print(f"    Balance: {balance:.0f} m³ ({balance/lake_area*1000:.3f} mm)")

    # Write riverinfo.dat
    riverinfo_path = os.path.join(output_dir, 'riverinfo.dat')
    with open(riverinfo_path, 'w') as f:
        f.write(f"{len(river_positions)}\n")
        for river, i, j in river_positions:
            f.write(f"{i} {j} {river['name']} -1 -1\n")
    print(f"  Saved: {riverinfo_path}")

    # Write rivers.nc
    rivers_path = os.path.join(output_dir, 'rivers.nc')
    ds = nc.Dataset(rivers_path, 'w', format='NETCDF4')
    ds.createDimension('time', None)
    time_v = ds.createVariable('time', 'f8', ('time',))
    time_v.units = f'seconds since {config["meteo"]["start_date"]} 00:00:00'
    time_v[:] = np.arange(n_days) * 86400.0

    for river in rivers_cfg:
        name = river['name']
        wq = river.get('water_quality', {})
        var = ds.createVariable(name, 'f8', ('time',))
        var.units = 'm3/s'
        var[:] = discharge[name]

        temp_base = wq.get('temp', 15.0)
        temp_vals = np.array([temp_base + 8 * math.sin(2 * math.pi * (d - 110) / 365.0) for d in range(n_days)])
        var_t = ds.createVariable(f'{name}_temp', 'f8', ('time',))
        var_t.units = 'degC'
        var_t[:] = temp_vals

        for wq_name in ['nh4', 'no3', 'po4', 'doc', 'poc']:
            var_wq = ds.createVariable(f'{name}_{wq_name}', 'f8', ('time',))
            var_wq.units = 'g/m3'
            var_wq[:] = np.full(n_days, wq.get(wq_name, 0.0))

    ds.title = f'{config["lake"]["name"]} river data'
    ds.close()
    print(f"  Saved: {rivers_path}")


# ============================================================
# 4. FABM initial conditions
# ============================================================
def generate_fabm_init(config, output_dir, bathymetry, lake_mask, latc_2d, lonc_2d):
    """Generate fabm_init.nc with spatial initial conditions (macrophytes)."""
    print("\n[4/4] Generating fabm_init.nc ...")

    grid = config['grid']
    NX, NY = grid['nx'], grid['ny']
    eco_cfg = config.get('ecology', {})

    fabm_init_path = os.path.join(output_dir, 'fabm_init.nc')
    ds = nc.Dataset(fabm_init_path, 'w', format='NETCDF4')
    ds.createDimension('x', NX)
    ds.createDimension('y', NY)
    ds.createDimension('z', 1)

    lat_1d = latc_2d[:, 0] if len(latc_2d.shape) == 2 else latc_2d
    lon_1d = lonc_2d[0, :] if len(lonc_2d.shape) == 2 else lonc_2d

    lon_v = ds.createVariable('lon', 'f8', ('x',))
    lon_v[:] = lon_1d
    lat_v = ds.createVariable('lat', 'f8', ('y',))
    lat_v[:] = lat_1d
    z_v = ds.createVariable('z', 'f8', ('z',))
    z_v[:] = [0.0]

    # Macrophytes
    macro_cfg = eco_cfg.get('macrophytes', {})
    if macro_cfg.get('enabled', True):
        depth_min, depth_max = macro_cfg.get('depth_range', [1.0, 2.5])
        initial_biomass = macro_cfg.get('initial_biomass', 30.0)
        macro_mask = np.zeros((NY, NX), dtype=bool)
        for j in range(NY):
            for i in range(NX):
                if lake_mask[j, i] and depth_min <= bathymetry[j, i] <= depth_max:
                    macro_mask[j, i] = True
        n_macro = macro_mask.sum()
        macro_field = np.zeros((1, NY, NX))
        macro_field[0, macro_mask] = initial_biomass
        macro_var = ds.createVariable('macrophytes_sD', 'f8', ('z', 'y', 'x'))
        macro_var.units = 'gDW/m2'
        macro_var[:] = macro_field
        print(f"  Macrophytes: {n_macro} cells ({n_macro/lake_mask.sum()*100:.1f}% of lake)")
    else:
        print(f"  Macrophytes: disabled")

    ds.title = f'{config["lake"]["name"]} FABM initial conditions'
    ds.close()
    print(f"  Saved: {fabm_init_path}")


# ============================================================
# Main
# ============================================================
def main():
    parser = argparse.ArgumentParser(description='3DWET Pre-processing Module')
    parser.add_argument('config', help='Path to lake_config.yaml')
    parser.add_argument('--output-dir', '-o', default=None,
                        help='Output directory (default: same as config location)')
    args = parser.parse_args()

    config_path = os.path.abspath(args.config)
    if not os.path.exists(config_path):
        print(f"ERROR: Config file not found: {config_path}")
        sys.exit(1)

    config = load_config(config_path)
    lake_name = config['lake']['name']

    if args.output_dir:
        output_dir = os.path.abspath(args.output_dir)
    else:
        output_dir = os.path.join(os.path.dirname(config_path), f'{lake_name}_data')

    os.makedirs(output_dir, exist_ok=True)

    print("=" * 70)
    print(f"3DWET Pre-processing Module")
    print(f"Lake: {lake_name}")
    print(f"Config: {config_path}")
    print(f"Output: {output_dir}")
    print("=" * 70)

    # Step 1: Bathymetry
    bathymetry, lake_mask, latc_2d, lonc_2d = generate_bathymetry(config, output_dir)

    # Step 2: Meteorology
    precip_mms, evap_mms = generate_meteo(config, output_dir, latc_2d, lonc_2d)

    # Step 3: Rivers
    lake_area = lake_mask.sum() * config['grid']['dx'] * config['grid']['dy']
    generate_rivers(config, output_dir, lake_mask, bathymetry, lake_area, precip_mms, evap_mms)

    # Step 4: FABM init
    generate_fabm_init(config, output_dir, bathymetry, lake_mask, latc_2d, lonc_2d)

    print("\n" + "=" * 70)
    print("Pre-processing COMPLETE!")
    print("=" * 70)
    print(f"\nGenerated files in: {output_dir}")
    for f in ['bathymetry.nc', 'meteo.nc', 'rivers.nc', 'fabm_init.nc',
              'riverinfo.dat', 'meteo_input.txt']:
        path = os.path.join(output_dir, f)
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"  {f:20s}  {size/1024:.1f} KB")

    print(f"\nNext step:")
    print(f"  python workflow/2_build_case/build_case.py <case_config.yaml>")
    print(f"  (use --data-dir {output_dir} to use these generated files)")


if __name__ == '__main__':
    main()
