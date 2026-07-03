"""EFDC -> GETM data converter for Luoma Lake.

Converts EFDC input files (cell.inp, dxdy.inp, lxly.inp, aser.inp, wser.inp,
qser.inp, efdc.inp C24) into GETM-format NetCDF files:
  - bathymetry.nc  (grid, depth, lonc, latc)
  - meteo.nc       (u10, v10, slp, t2, rh, tcc, precip, evap)
  - rivers.nc      (5 flow series: ZYH, ZH, YH, XYH, YHT)
  - riverinfo.dat  (9 source/sink cells mapping to 5 rivers)

EFDC grid: 52 cols (I) x 46 rows (J), 1194 active cells, 500m resolution.
Water level reference: 21.82 m. UTM Zone 50N -> WGS84.

Usage:
    python efdc_to_getm.py
"""
import os
import re
import numpy as np
import netCDF4 as nc

# ------------------------------------------------------------------
# Paths
# ------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EFDC_DIR = r"D:\00_数据\00_骆马湖-模型\LMH_Balanced_test_WL0 = 21.82"

# Grid (from efdc.inp: IC=52, JC=46)
NX, NY = 52, 46          # I=1..52, J=1..46
DX, DY = 500.0, 500.0    # meters
WATER_LEVEL = 21.82      # reference water level (m)
LAND_VALUE = -10.0       # GETM land marker
UTM_ZONE = 50

# River names (EFDC series order)
RIVER_NAMES = ["ZYH", "ZH", "YH", "XYH", "YHT"]

# Source/sink cells (from efdc.inp C24): (i, j, series_id, label)
# series_id is 1-based index into RIVER_NAMES
SOURCES = [
    (10, 20, 1, "ZYH-In/Out 1"),
    (15, 44, 3, "YH-In"),
    (50, 12, 5, "YHT-Out"),
    (21,  6, 2, "ZH-In"),
    ( 8, 18, 1, "ZYH-In/Out 3"),
    ( 9, 19, 1, "ZYH-In/Out 2"),
    (45, 33, 4, "XYH-Out"),
    (44, 33, 4, "XYH-Out"),
    (43, 33, 4, "XYH-Out"),
]


# ------------------------------------------------------------------
# UTM -> lat/lon (vectorized, WGS84)
# ------------------------------------------------------------------
def utm_to_latlon(easting, northing, zone=UTM_ZONE):
    a = 6378137.0
    f = 1 / 298.257223563
    k0 = 0.9996
    e2 = 2*f - f*f
    e_prime2 = e2 / (1 - e2)

    x = np.asarray(easting) - 500000.0
    y = np.asarray(northing)
    M = y / k0
    mu = M / (a * (1 - e2/4 - 3*e2**2/64 - 5*e2**3/256))
    e1 = (1 - np.sqrt(1 - e2)) / (1 + np.sqrt(1 - e2))
    phi1 = mu + (3*e1/2 - 27*e1**3/32) * np.sin(2*mu)
    phi1 = phi1 + (21*e1**2/16 - 55*e1**4/32) * np.sin(4*mu)
    phi1 = phi1 + (151*e1**3/96) * np.sin(6*mu)

    N1 = a / np.sqrt(1 - e2 * np.sin(phi1)**2)
    T1 = np.tan(phi1)**2
    C1 = e_prime2 * np.cos(phi1)**2
    R1 = a * (1 - e2) / (1 - e2 * np.sin(phi1)**2)**1.5
    D = x / (N1 * k0)

    lat = phi1 - (N1 * np.tan(phi1) / R1) * (D**2/2
         - (5 + 3*T1 + 10*C1 - 4*C1**2 - 9*e_prime2) * D**4/24
         + (61 + 90*T1 + 298*C1 + 45*T1**2 - 252*e_prime2 - 3*C1**2) * D**6/720)
    lon = (D - (1 + 2*T1 + C1) * D**3/6
          + (5 - 2*C1 + 28*T1 - 3*C1**2 + 8*e_prime2 + 24*T1**2) * D**5/120) / np.cos(phi1)
    lon = lon * 180/np.pi + zone * 6 - 183
    lat = lat * 180/np.pi
    return lat, lon


# ------------------------------------------------------------------
# Parsers
# ------------------------------------------------------------------
def parse_cell_inp(path):
    """Parse cell.inp -> 2D mask (NY, NX). 1=water, 0=land.

    cell.inp layout: first line is header, then rows from j=NY down to j=1.
    Each data line: '{j}  {52 chars}' where 5/9=water, 0=land.
    """
    mask = np.zeros((NY, NX), dtype=np.int8)
    with open(path, 'r', encoding='latin-1') as f:
        lines = [ln.rstrip('\n') for ln in f if ln.strip()]
    # skip header lines (starting with C or not matching data pattern)
    for ln in lines:
        parts = ln.split()
        if len(parts) < 2:
            continue
        try:
            j = int(parts[0])
        except ValueError:
            continue
        if j < 1 or j > NY:
            continue
        # second token is the row string
        row_str = parts[1]
        if len(row_str) < NX:
            continue
        for i in range(NX):
            ch = row_str[i]
            mask[j - 1, i] = 1 if ch in ('5', '9') else 0
    return mask


def parse_dxdy_inp(path):
    """Parse dxdy.inp -> depth(NY,NX), elev(NY,NX). Land cells = NaN."""
    depth = np.full((NY, NX), np.nan)
    elev = np.full((NY, NX), np.nan)
    with open(path, 'r', encoding='latin-1') as f:
        for ln in f:
            parts = ln.split()
            if len(parts) < 6:
                continue
            try:
                i = int(parts[0]); j = int(parts[1])
                dx = float(parts[2]); dy = float(parts[3])
                d = float(parts[4]); e = float(parts[5])
            except ValueError:
                continue
            if 1 <= i <= NX and 1 <= j <= NY:
                depth[j - 1, i - 1] = d
                elev[j - 1, i - 1] = e
    return depth, elev


def parse_lxly_inp(path):
    """Parse lxly.inp -> utm_x(NY,NX), utm_y(NY,NX), rotation params.

    Returns (utm_x, utm_y, ref) where ref = (i0, j0, x0, y0, cue, cve, cun, cvn)
    from the first valid record. Land cells in utm_x/utm_y are NaN.
    """
    utm_x = np.full((NY, NX), np.nan)
    utm_y = np.full((NY, NX), np.nan)
    ref = None
    with open(path, 'r', encoding='latin-1') as f:
        for ln in f:
            parts = ln.split()
            if len(parts) < 7:
                continue
            try:
                i = int(parts[0]); j = int(parts[1])
                x = float(parts[2]); y = float(parts[3])
                cue = float(parts[4]); cve = float(parts[5])
                cun = float(parts[6]); cvn = float(parts[7]) if len(parts) > 7 else 0.0
            except ValueError:
                continue
            if 1 <= i <= NX and 1 <= j <= NY:
                utm_x[j - 1, i - 1] = x
                utm_y[j - 1, i - 1] = y
                if ref is None:
                    ref = (i, j, x, y, cue, cve, cun, cvn)
    return utm_x, utm_y, ref


def compute_utm_grid(ref):
    """Compute UTM (x, y) for every (I, J) cell using affine transform.

    From lxly.inp the grid is rotated 30 deg: I direction -> (CUE, -CVE),
    J direction -> (-CUN, CVN) per cell of size DX, DY. Verified against
    multiple sample points: X(I+1)-X(I) = DX*CUE, Y(I+1)-Y(I) = -DX*CVE,
    X(J+1)-X(J) = -DY*CUN, Y(J+1)-Y(J) = DY*CVN.
    """
    i0, j0, x0, y0, cue, cve, cun, cvn = ref
    ii = np.arange(1, NX + 1)  # I = 1..NX
    jj = np.arange(1, NY + 1)  # J = 1..NY
    I, J = np.meshgrid(ii, jj)  # shape (NY, NX), J varies along rows
    utm_x = x0 + (I - i0) * DX * cue + (J - j0) * DY * (-cun)
    utm_y = y0 + (I - i0) * DX * (-cve) + (J - j0) * DY * cvn
    return utm_x, utm_y


def parse_aser_inp(path):
    """Parse aser.inp -> dict of 1D arrays (length n_days).

    Returns: dict with keys t2, slp, rh, tcc, precip, evap, swr
    Units after conversion: slp=Pa, t2=degC, rh=0-1, tcc=0-1,
                            precip=m/s, evap=m/s (negative=loss), swr=W/m2
    """
    with open(path, 'r', encoding='latin-1') as f:
        lines = f.readlines()

    # find header line with MASER
    hdr_idx = None
    for k, ln in enumerate(lines):
        if 'MASER' in ln or (ln.strip() and ln.strip()[0].isdigit()
                             and 'TCASER' not in ln and '86400' in ln):
            # data header line like: 1096 86400.0 0.0 1 1.1574E-05 ...
            parts = ln.split()
            try:
                int(parts[0])
                if len(parts) >= 4:
                    hdr_idx = k
                    break
            except (ValueError, IndexError):
                continue

    if hdr_idx is None:
        raise ValueError("Could not find aser.inp header")

    hdr = lines[hdr_idx].split()
    n_recs = int(hdr[0])
    irelh = int(hdr[3]) if len(hdr) > 3 else 0

    # parse data records
    t2 = np.zeros(n_recs)
    slp = np.zeros(n_recs)
    rh = np.zeros(n_recs)
    precip = np.zeros(n_recs)
    evap = np.zeros(n_recs)
    swr = np.zeros(n_recs)
    tcc = np.zeros(n_recs)

    data_count = 0
    for ln in lines[hdr_idx + 1:]:
        parts = ln.split()
        if len(parts) < 8:
            continue
        try:
            t = float(parts[0])
        except ValueError:
            continue
        if data_count >= n_recs:
            break
        slp[data_count] = float(parts[1]) * 100.0      # mb -> Pa
        t2[data_count] = float(parts[2])                # degC
        rh[data_count] = float(parts[3])                # 0-1 (IRELH=1)
        precip[data_count] = float(parts[4]) / 86400.0  # m/d -> m/s
        # evap in file is positive value (m/d); GETM wants negative = loss
        evap[data_count] = -abs(float(parts[5])) / 86400.0
        swr[data_count] = float(parts[6])               # W/m2
        tcc[data_count] = float(parts[7])               # 0-1
        data_count += 1

    return {
        'n_days': n_recs,
        't2': t2, 'slp': slp, 'rh': rh, 'tcc': tcc,
        'precip': precip, 'evap': evap, 'swr': swr,
    }


def parse_wser_inp(path):
    """Parse wser.inp -> u10, v10 (m/s at 10m).

    EFDC ISWDINT=0: direction is 'towards' (where wind blows TO).
    Wind vector components:
        u = speed * sin(dir)    (eastward)
        v = speed * cos(dir)    (northward)
    Height correction 2m -> 10m: factor = (10/2)^(1/7) = 1.349
    """
    with open(path, 'r', encoding='latin-1') as f:
        lines = f.readlines()

    hdr_idx = None
    for k, ln in enumerate(lines):
        parts = ln.split()
        if len(parts) >= 6:
            try:
                n = int(parts[0])
                if n > 100:
                    hdr_idx = k
                    break
            except ValueError:
                continue

    hdr = lines[hdr_idx].split()
    n_recs = int(hdr[0])
    wind_h = float(hdr[5]) if len(hdr) > 5 else 2.0
    height_factor = (10.0 / wind_h) ** (1.0 / 7.0)

    u10 = np.zeros(n_recs)
    v10 = np.zeros(n_recs)
    count = 0
    for ln in lines[hdr_idx + 1:]:
        parts = ln.split()
        if len(parts) < 3:
            continue
        try:
            t = float(parts[0])
        except ValueError:
            continue
        if count >= n_recs:
            break
        speed = float(parts[1]) * height_factor
        direction = float(parts[2])  # degrees, towards
        rad = np.deg2rad(direction)
        # towards direction: wind vector points to that azimuth
        u10[count] = speed * np.sin(rad)
        v10[count] = speed * np.cos(rad)
        count += 1

    return u10[:count], v10[:count]


def parse_qser_inp(path):
    """Parse qser.inp -> dict {river_name: np.array(n_days)}.

    Returns 5 series: ZYH, ZH, YH, XYH, YHT (in EFDC series order).
    """
    with open(path, 'r', encoding='latin-1') as f:
        lines = f.readlines()

    series = {}
    i = 0
    while i < len(lines):
        ln = lines[i]
        parts = ln.split()
        # header line: InType MQSER TCQSER TAASER RMULADJ ADDADJ ICHGQS ! name
        if len(parts) >= 7:
            try:
                intype = int(parts[0])
                m = int(parts[1])
                # confirm it's a header by checking next line(s)
                # skip comment lines
                if parts[0].isdigit() and m > 100:
                    # extract name after '!'
                    name = ''
                    if '!' in ln:
                        name = ln.split('!')[1].strip().split()[0]
                        # take only first token, strip non-alnum
                        name = re.sub(r'[^A-Za-z0-9_\-]', '', name)
                    # read depth weights (KC=1, one value)
                    i += 1
                    if i < len(lines):
                        # skip the single depth-weight value line
                        pass
                    # read m data records
                    vals = np.zeros(m)
                    rec = 0
                    i += 1
                    while i < len(lines) and rec < m:
                        dp = lines[i].split()
                        if len(dp) >= 2:
                            try:
                                t = float(dp[0])
                                q = float(dp[1])
                                vals[rec] = q
                                rec += 1
                            except ValueError:
                                pass
                        i += 1
                    series[name] = vals[:rec]
                    continue
            except ValueError:
                pass
        i += 1

    # map to standard names in EFDC series order (1..5)
    # The qser.inp file lists series in order; the series_id in efdc.inp C24
    # references them by position. We assign names based on the labels.
    result = {}
    series_list = list(series.values())
    names_list = list(series.keys())
    for k, rname in enumerate(RIVER_NAMES):
        if k < len(series_list):
            result[rname] = series_list[k]
        else:
            result[rname] = np.zeros(1096)
    return result


# ------------------------------------------------------------------
# NetCDF writers
# ------------------------------------------------------------------
def smooth_bathymetry(H, water_mask, n_passes=1):
    """Apply light 5-point smoothing to water cells only.

    Necessary to suppress 2Δx instability in 3D sigma-coordinate momentum
    equation that originates from small-scale bathymetry variations near
    deep-water / land-boundary transitions. Preserves land mask and keeps
    depth envelope roughly intact (typical mean change < 0.1 m).
    """
    Hs = H.copy()
    for _ in range(n_passes):
        Hnew = Hs.copy()
        for j in range(1, H.shape[0] - 1):
            for i in range(1, H.shape[1] - 1):
                if not water_mask[j, i]:
                    continue
                vals = [Hs[j, i]]
                for dj, di in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if water_mask[j + dj, i + di]:
                        vals.append(Hs[j + dj, i + di])
                Hnew[j, i] = np.mean(vals)
        Hs = Hnew
    return Hs


def fill_missing_depth(mask, depth, max_iter=50):
    """Fill NaN depth for water cells (mask==1) via iterative neighbor averaging.

    EFDC cell.inp marks water cells with '5' (has depth in dxdy.inp) or '9'
    (no depth data). Without this fix, '9' cells get depth=0 and are silently
    dropped to land by the depth<=0 check, losing ~25% of the lake area.
    """
    depth_filled = depth.copy().astype(np.float64)
    n_need = int(np.sum((mask == 1) & np.isnan(depth_filled)))
    if n_need == 0:
        return depth_filled
    print(f"  Filling depth for {n_need} water cells lacking dxdy.inp data (iterative neighbor avg)")
    for it in range(max_iter):
        still_nan = (mask == 1) & np.isnan(depth_filled)
        if not still_nan.any():
            break
        filled_this_pass = 0
        for j in range(depth_filled.shape[0]):
            for i in range(depth_filled.shape[1]):
                if not still_nan[j, i]:
                    continue
                vals = []
                for dj, di in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    jj, ii = j + dj, i + di
                    if (0 <= jj < depth_filled.shape[0] and
                            0 <= ii < depth_filled.shape[1] and
                            not np.isnan(depth_filled[jj, ii]) and
                            mask[jj, ii] == 1):
                        vals.append(depth_filled[jj, ii])
                if vals:
                    depth_filled[j, i] = np.mean(vals)
                    filled_this_pass += 1
        if filled_this_pass == 0:
            # no progress; fall back to global mean of valid water depths
            valid = depth_filled[(mask == 1) & ~np.isnan(depth_filled)]
            fallback = float(np.mean(valid)) if valid.size > 0 else 2.0
            depth_filled[(mask == 1) & np.isnan(depth_filled)] = fallback
            print(f"    iter {it+1}: no progress, filled remaining with fallback={fallback:.2f}m")
            break
        print(f"    iter {it+1}: filled {filled_this_pass} cells")
    n_remaining = int(np.sum((mask == 1) & np.isnan(depth_filled)))
    print(f"  Fill complete: {n_need - n_remaining}/{n_need} cells filled, {n_remaining} still NaN")
    return depth_filled


def write_bathymetry_nc(out_path, mask, depth, utm_x, utm_y, ref):
    """Write GETM bathymetry.nc.

    - x, y: 1D grid coordinates (meters, based on cell index * DX/DY)
    - lonc, latc: 2D WGS84 from UTM conversion (affine-computed for all cells)
    - bathymetry: 2D water depth (m), land = -10.0
    """
    # Fill depth for '9' cells (water mask=1 but depth=NaN in dxdy.inp)
    depth = fill_missing_depth(mask, depth)

    # Fill land cells in depth with LAND_VALUE
    depth_grid = np.where(mask == 1, np.nan_to_num(depth, nan=0.0), LAND_VALUE)
    # safety: ensure positive depth for water cells
    depth_grid = np.where(depth_grid <= 0, LAND_VALUE, depth_grid)
    depth_grid = np.where(mask == 0, LAND_VALUE, depth_grid)

    # Apply light smoothing to suppress 3D sigma-coordinate 2Δx instability
    water_mask = depth_grid > 0
    depth_orig = depth_grid.copy()
    depth_grid = smooth_bathymetry(depth_grid, water_mask, n_passes=1)
    max_dh = float(np.max(np.abs(depth_grid[water_mask] - depth_orig[water_mask])))
    mean_dh = float(np.mean(np.abs(depth_grid[water_mask] - depth_orig[water_mask])))
    print(f"  Applied 5-point bathymetry smoothing: max dH={max_dh:.3f} m, mean |dH|={mean_dh:.3f} m")

    # Compute UTM coordinates for ALL cells via affine transform (no NaN)
    utm_x_full, utm_y_full = compute_utm_grid(ref)

    # Sanity check: compare computed vs lxly.inp values at active cells
    if np.sum(~np.isnan(utm_x)) > 0:
        diff_x = np.abs(utm_x_full - utm_x)
        diff_y = np.abs(utm_y_full - utm_y)
        max_dx = np.nanmax(diff_x)
        max_dy = np.nanmax(diff_y)
        print(f"  UTM affine check vs lxly.inp: max dx={max_dx:.2f} m, max dy={max_dy:.2f} m")

    # 1D grid coordinates (cell index * resolution)
    x_grid = (np.arange(NX) + 1) * DX
    y_grid = (np.arange(NY) + 1) * DY

    # lonc, latc from UTM
    latc, lonc = utm_to_latlon(utm_x_full, utm_y_full)

    ds = nc.Dataset(out_path, 'w', format='NETCDF4')
    ds.createDimension('x', NX)
    ds.createDimension('y', NY)
    ds.createDimension('xq', NX + 1)
    ds.createDimension('yq', NY + 1)

    gtype = ds.createVariable('grid_type', 'i4')
    gtype[:] = 1

    xv = ds.createVariable('x', 'f8', ('x',))
    xv[:] = x_grid; xv.units = 'm'; xv.long_name = 'x coordinate of cell centers'

    yv = ds.createVariable('y', 'f8', ('y',))
    yv[:] = y_grid; yv.units = 'm'; yv.long_name = 'y coordinate of cell centers'

    lv = ds.createVariable('lonc', 'f8', ('y', 'x'))
    lv[:] = lonc; lv.units = 'degrees_east'; lv.long_name = 'longitude of cell centers'

    lav = ds.createVariable('latc', 'f8', ('y', 'x'))
    lav[:] = latc; lav.units = 'degrees_north'; lav.long_name = 'latitude of cell centers'

    bv = ds.createVariable('bathymetry', 'f8', ('y', 'x'))
    bv[:] = depth_grid
    bv.units = 'm'; bv.long_name = 'water depth'
    bv.standard_name = 'sea_floor_depth'
    bv.coordinates = 'lonc latc'

    ds.title = 'Luoma Lake bathymetry (from EFDC dxdy.inp)'
    ds.source = 'Converted by efdc_to_getm.py'
    ds.Conventions = 'CF-1.0'
    ds.close()

    n_water = int(np.sum(depth_grid > 0))
    d = depth_grid[depth_grid > 0]
    print(f"  bathymetry.nc: {n_water} water cells, depth {d.min():.2f}-{d.max():.2f} m")
    print(f"  lonc: {lonc.min():.4f} to {lonc.max():.4f}")
    print(f"  latc: {latc.min():.4f} to {latc.max():.4f}")


def write_meteo_nc(out_path, meteo, u10, v10, nx, ny):
    """Write GETM meteo.nc.

    C variable dims (time, lat, lon) -> Fortran reversal -> (lon, lat, time).
    Variables: u10, v10, slp, t2, rh, tcc (f4); precip, evap (f8).
    """
    n_days = meteo['n_days']
    ds = nc.Dataset(out_path, 'w', format='NETCDF4')
    ds.createDimension('lon', nx)
    ds.createDimension('lat', ny)
    ds.createDimension('time', n_days)

    lon_v = ds.createVariable('lon', 'f8', ('lon',))
    lon_v.units = 'degrees_east'; lon_v.long_name = 'longitude'
    # use a representative lon/lat (will be overwritten by bathymetry in GETM)
    lon_v[:] = np.linspace(118.0, 118.5, nx)

    lat_v = ds.createVariable('lat', 'f8', ('lat',))
    lat_v.units = 'degrees_north'; lat_v.long_name = 'latitude'
    lat_v[:] = np.linspace(34.0, 34.3, ny)

    tv = ds.createVariable('time', 'f8', ('time',))
    tv.units = 'seconds since 2020-01-01 00:00:00'
    tv.long_name = 'time'
    tv[:] = np.arange(n_days) * 86400.0

    var_specs_f32 = [
        ('u10',  'm s-1',  '10m wind u-component', u10),
        ('v10',  'm s-1',  '10m wind v-component', v10),
        ('slp',  'Pa',     'sea level pressure',   meteo['slp']),
        ('t2',   'degC',   '2m air temperature',   meteo['t2']),
        ('rh',   '1',      'relative humidity',    meteo['rh']),
        ('tcc',  '1',      'total cloud cover',    meteo['tcc']),
    ]
    var_specs_f64 = [
        ('precip', 'm s-1', 'precipitation rate',  meteo['precip']),
        ('evap',   'm s-1', 'evaporation rate',    meteo['evap']),
    ]

    for name, units, long_name, data_1d in var_specs_f32:
        v = ds.createVariable(name, 'f4', ('time', 'lat', 'lon'),
                              fill_value=np.float32(-9999.0))
        v.units = units; v.long_name = long_name
        data_3d = np.broadcast_to(data_1d[:, None, None], (n_days, ny, nx)).astype(np.float32).copy()
        v[:] = data_3d

    for name, units, long_name, data_1d in var_specs_f64:
        v = ds.createVariable(name, 'f8', ('time', 'lat', 'lon'),
                              fill_value=np.float64(-9999.0))
        v.units = units; v.long_name = long_name
        data_3d = np.broadcast_to(data_1d[:, None, None], (n_days, ny, nx)).astype(np.float64).copy()
        v[:] = data_3d

    ds.title = 'Luoma Lake meteorological data (from EFDC aser.inp + wser.inp)'
    ds.source = 'Converted by efdc_to_getm.py'
    ds.Conventions = 'CF-1.0'
    ds.close()
    print(f"  meteo.nc: {n_days} days, "
          f"t2={meteo['t2'].min():.1f}-{meteo['t2'].max():.1f} C, "
          f"wind={np.sqrt(u10**2+v10**2).max():.1f} m/s")


def write_rivers_nc(out_path, flow_series, n_days):
    """Write GETM rivers.nc (5 rivers, 1D time series)."""
    ds = nc.Dataset(out_path, 'w', format='NETCDF4')
    ds.createDimension('time', None)  # unlimited

    tv = ds.createVariable('time', 'f8', ('time',))
    tv.units = 'seconds since 2020-01-01 00:00:00'
    tv.long_name = 'time'
    tv[:] = np.arange(n_days) * 86400.0

    for name in RIVER_NAMES:
        q = flow_series.get(name, np.zeros(n_days))
        if len(q) < n_days:
            q = np.pad(q, (0, n_days - len(q)), 'edge')
        v = ds.createVariable(name, 'f8', ('time',))
        v.units = 'm3/s'
        v.long_name = f'{name} river discharge'
        v[:] = q
        print(f"  {name}: Q=[{q.min():.1f}, {q.max():.1f}] m3/s, mean={q.mean():.1f}")

    ds.title = 'Luoma Lake river data (from EFDC qser.inp)'
    ds.source = 'Converted by efdc_to_getm.py'
    ds.close()


def write_riverinfo_dat(out_path):
    """Write GETM riverinfo.dat (9 cells mapping to 5 rivers).

    GETM requires same-named river entries to be on consecutive lines so it
    can group them as a multi-cell river. Sort by river name to guarantee this.
    """
    # Sort by river name so same-named entries are consecutive
    sorted_sources = sorted(SOURCES, key=lambda s: RIVER_NAMES[s[2] - 1])
    lines = [f"{len(sorted_sources)}"]
    for i, j, sid, label in sorted_sources:
        rname = RIVER_NAMES[sid - 1]
        lines.append(f"{i} {j} {rname} -1 -1")
    with open(out_path, 'w', encoding='latin-1') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"  riverinfo.dat: {len(sorted_sources)} cells, 5 rivers (sorted by name)")


def write_meteo_input_txt(out_path):
    """Write meteo_input.txt (points to meteo.nc)."""
    with open(out_path, 'w') as f:
        f.write('meteo.nc\n')


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
def main():
    print("=" * 70)
    print("EFDC -> GETM converter for Luoma Lake")
    print(f"  EFDC source: {EFDC_DIR}")
    print(f"  Output dir:  {SCRIPT_DIR}")
    print("=" * 70)

    # 1. bathymetry
    print("\n[1/4] Parsing bathymetry data...")
    mask = parse_cell_inp(os.path.join(EFDC_DIR, 'cell.inp'))
    depth, elev = parse_dxdy_inp(os.path.join(EFDC_DIR, 'dxdy.inp'))
    utm_x, utm_y, ref = parse_lxly_inp(os.path.join(EFDC_DIR, 'lxly.inp'))
    print(f"  Water cells: {int(mask.sum())} / {NX*NY}")
    print(f"  Depth data points: {int(np.sum(~np.isnan(depth)))}")
    print(f"  UTM data points: {int(np.sum(~np.isnan(utm_x)))}")
    if ref:
        print(f"  Ref point: I={ref[0]} J={ref[1]} X={ref[2]:.1f} Y={ref[3]:.1f} "
              f"CUE={ref[4]:.5f} CVE={ref[5]:.5f}")

    write_bathymetry_nc(os.path.join(SCRIPT_DIR, 'bathymetry.nc'),
                        mask, depth, utm_x, utm_y, ref)

    # 2. meteo
    print("\n[2/4] Parsing meteorological data...")
    meteo = parse_aser_inp(os.path.join(EFDC_DIR, 'aser.inp'))
    u10, v10 = parse_wser_inp(os.path.join(EFDC_DIR, 'wser.inp'))
    n_days = meteo['n_days']
    if len(u10) < n_days:
        u10 = np.pad(u10, (0, n_days - len(u10)), 'edge')
        v10 = np.pad(v10, (0, n_days - len(v10)), 'edge')
    write_meteo_nc(os.path.join(SCRIPT_DIR, 'meteo.nc'),
                   meteo, u10[:n_days], v10[:n_days], NX, NY)
    write_meteo_input_txt(os.path.join(SCRIPT_DIR, 'meteo_input.txt'))

    # 3. rivers
    print("\n[3/4] Parsing river data...")
    flow_series = parse_qser_inp(os.path.join(EFDC_DIR, 'qser.inp'))
    write_rivers_nc(os.path.join(SCRIPT_DIR, 'rivers.nc'), flow_series, n_days)
    write_riverinfo_dat(os.path.join(SCRIPT_DIR, 'riverinfo.dat'))

    # 4. summary
    print("\n[4/4] Summary")
    print("=" * 70)
    print(f"Generated files in {SCRIPT_DIR}:")
    for fn in ['bathymetry.nc', 'meteo.nc', 'rivers.nc',
               'riverinfo.dat', 'meteo_input.txt']:
        p = os.path.join(SCRIPT_DIR, fn)
        if os.path.exists(p):
            print(f"  {fn:20s}  {os.path.getsize(p)/1024:.1f} KB")
    print("=" * 70)
    print("\nNext step: generate getm.inp and run model")


if __name__ == '__main__':
    main()
