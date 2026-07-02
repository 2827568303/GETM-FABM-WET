"""Generate all input files for Theoretical Lake test case.

Theoretical Lake specifications:
- Grid: 500m x 500m, i=5 (x), j=7 (y) -> 5x7 = 35 cells
- Vertical: k=10 sigma layers
- Average depth: 3.5 m
- Bathymetry: main basin 3-4m, southeast bay 2-3m (shallower for macrophytes)
- Rivers: 2 inflows (NE, NW), 1 outflow (SW)
- Macrophytes: 30% coverage in SE bay
- Simulation: 365 days (2020-01-01 to 2020-12-31)
- Strict water balance: inflow = outflow + evap - precip + storage change
- Meteorology: based on Luomahu data (same climate region)

Generated files (in case/):
- bathymetry.nc    : lake topography
- riverinfo.dat    : river positions
- rivers.nc        : river discharge + WQ (365 days)
- meteo.nc         : meteorological forcing (365 days)
- fabm_init.nc     : initial conditions for biota
- fabm.yaml        : FABM configuration
- getm.inp         : GETM configuration
- getm_fabm.inp    : FABM-GETM coupling configuration
"""
import numpy as np
import netCDF4 as nc
from datetime import datetime, timedelta
import os
import math

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_GETM_ROOT = os.path.dirname(os.path.dirname(_SCRIPT_DIR))
CASE_DIR = os.path.join(_GETM_ROOT, "case", "Theoretical lake")
LUOMAHU_CASE = os.path.join(_GETM_ROOT, "case", "Lake Luoma")
LUOMAHU_INPUTS = os.path.join(LUOMAHU_CASE, "inputs", "Inputs.xlsx")

# Lake parameters
NX, NY = 5, 7  # i=5 (x), j=7 (y)
DX = DY = 500.0  # grid size in meters
AVG_DEPTH = 3.5  # average depth in meters
MAX_DEPTH = 5.0  # max depth for central basin
N_DAYS = 366  # 2020 is a leap year: Jan 1 to Dec 31 = 366 days
START_DATE = datetime(2020, 1, 1)

# Lake surface area and volume
LAKE_AREA = NX * NY * DX * DY  # 5*7*500*500 = 8,750,000 m² = 8.75 km²
print(f"Lake area: {LAKE_AREA/1e6:.2f} km² = {LAKE_AREA:.0f} m²")

# ============================================================
# 1. Generate bathymetry.nc
# ============================================================
print("\n" + "=" * 70)
print("Step 1: Generating bathymetry.nc")
print("=" * 70)

# Design bathymetry:
# - Main basin (center): 3.5-5m depth
# - SE bay (southeast corner): 2-3m shallower for macrophytes
# - Edges: gradual slope
bathymetry = np.zeros((NY, NX))
for j in range(NY):
    for i in range(NX):
        # Distance from center
        cx, cy = (NX - 1) / 2.0, (NY - 1) / 2.0
        dist = math.sqrt((i - cx) ** 2 + (j - cy) ** 2)
        max_dist = math.sqrt(cx ** 2 + cy ** 2)

        # Base depth: center deepest, edges shallow
        base_depth = MAX_DEPTH * (1 - 0.4 * (dist / max_dist) ** 2)

        # SE bay (i>=3, j>=5): shallower
        if i >= 3 and j >= 5:
            # Southeast bay: shallow, depth 2-3m
            se_factor = 0.55  # 55% of base depth
            base_depth = base_depth * se_factor
            base_depth = max(2.0, min(3.0, base_depth))

        # Ensure minimum depth 1.0m
        bathymetry[j, i] = max(1.0, min(MAX_DEPTH, base_depth))

# Adjust to average depth 3.5m
current_avg = bathymetry.mean()
scale_factor = AVG_DEPTH / current_avg
bathymetry = bathymetry * scale_factor
# Clamp
bathymetry = np.clip(bathymetry, 1.0, MAX_DEPTH)

print(f"Bathymetry: avg={bathymetry.mean():.2f}m, min={bathymetry.min():.2f}m, max={bathymetry.max():.2f}m")
print(f"Target avg: {AVG_DEPTH}m")

# Calculate lake volume
lake_volume = np.sum(bathymetry) * DX * DY
print(f"Lake volume: {lake_volume:.0f} m³ = {lake_volume/1e6:.2f} Mm³")

# Write bathymetry.nc
bathy_path = os.path.join(CASE_DIR, "bathymetry.nc")
print(f"Writing {bathy_path}...")

ds = nc.Dataset(bathy_path, "w", format="NETCDF4")

# Dimensions: x/y for cell centers, xq/yq for cell corners
ds.createDimension("x", NX)
ds.createDimension("y", NY)
ds.createDimension("xq", NX + 1)
ds.createDimension("yq", NY + 1)

# grid_type scalar (1 = cartesian) - required by GETM ncdf_check_grid
grid_type_var = ds.createVariable("grid_type", "i4")
grid_type_var[:] = 1

# Coordinate variables (UTM-like, use arbitrary origin)
x0, y0 = 500000.0, 3800000.0  # UTM zone 50N approximate for the region

x_var = ds.createVariable("x", "f8", ("x",))
x_var.units = "m"
x_var.long_name = "x coordinate of cell centers"
x_var[:] = x0 + np.arange(NX) * DX + DX / 2

y_var = ds.createVariable("y", "f8", ("y",))
y_var.units = "m"
y_var.long_name = "y coordinate of cell centers"
y_var[:] = y0 + np.arange(NY) * DY + DY / 2

# Latc/lonc (2D geographic coordinates) - approximate for the region
lat0, lon0 = 34.15, 118.20  # near Luomahu
lat_var = ds.createVariable("latc", "f8", ("y", "x"))
lat_var.units = "degrees_north"
lat_var.long_name = "latitude of cell centers"
for j in range(NY):
    lat_var[j, :] = lat0 + (NY / 2 - j) * (DY / 111000.0)

lon_var = ds.createVariable("lonc", "f8", ("y", "x"))
lon_var.units = "degrees_east"
lon_var.long_name = "longitude of cell centers"
for i in range(NX):
    lon_var[:, i] = lon0 + (i - NX / 2) * (DX / (111000.0 * math.cos(math.radians(lat0))))

# Bathymetry variable (NY, NX)
bath_var = ds.createVariable("bathymetry", "f8", ("y", "x"))
bath_var.units = "m"
bath_var.long_name = "water depth"
bath_var.standard_name = "sea_floor_depth"
bath_var.coordinates = "lonc latc"
bath_var[:] = bathymetry

ds.title = "Theoretical Lake Bathymetry"
ds.source = "Generated by gen_theoretical_lake.py"
ds.history = f"Created {datetime.now()}"
ds.Conventions = "CF-1.0"
ds.close()
print("  Done!")

# ============================================================
# 2. Generate riverinfo.dat and rivers.nc
# ============================================================
print("\n" + "=" * 70)
print("Step 2: Generating riverinfo.dat and rivers.nc")
print("=" * 70)

# River positions (1-indexed for GETM):
# - INFL1 (Northeast): (i=5, j=1) - top-right corner (NE)
# - INFL2 (Northwest): (i=1, j=1) - top-left corner (NW)
# - OUTFL (Southwest): (i=1, j=7) - bottom-left corner (SW)
#
# Note: j=1 is North (top), j=7 is South (bottom) in GETM array convention
# (j increases southward in typical Cartesian setup)

RIVERS = {
    "INFL1": {"pos": [(5, 1)], "type": "inflow"},   # NE inflow
    "INFL2": {"pos": [(1, 1)], "type": "inflow"},   # NW inflow
    "OUTFL": {"pos": [(1, 7)], "type": "outflow"},  # SW outflow
}

# Write riverinfo.dat
riverinfo_path = os.path.join(CASE_DIR, "riverinfo.dat")
total_cells = sum(len(r["pos"]) for r in RIVERS.values())
with open(riverinfo_path, "w") as f:
    f.write(f"{total_cells}\n")
    for name, info in RIVERS.items():
        for (i, j) in info["pos"]:
            f.write(f"{i} {j} {name} -1 -1\n")
print(f"  riverinfo.dat: {total_cells} river cells")
for name, info in RIVERS.items():
    for (i, j) in info["pos"]:
        print(f"    {name}: ({i},{j}) - {info['type']}")

# Water balance design:
# Annual precipitation (Luomahu region): ~900 mm/year
# Annual evaporation: ~1000 mm/year
# Net atmospheric: -100 mm/year (evap > precip)
#
# Lake volume = 30.6 Mm³ (avg depth 3.5m × 8.75 km²)
# To maintain stable water level:
#   Inflow = Outflow + (Evap - Precip) * Area
#   Inflow = Outflow + 0.1m * 8.75e6 m² = Outflow + 875,000 m³/year
#
# Design flows:
# - INFL1 (NE): 2.0 m³/s (main inflow, 63.1 Mm³/year)
# - INFL2 (NW): 1.0 m³/s (secondary inflow, 31.6 Mm³/year)
# - Total inflow: 3.0 m³/s = 94.7 Mm³/year
# - Precipitation: 0.9 m * 8.75e6 = 7.9 Mm³/year
# - Total input: 102.6 Mm³/year
#
# - Evaporation: 1.0 m * 8.75e6 = 8.8 Mm³/year
# - OUTFL (SW): designed to balance = Total input - Evap = 93.8 Mm³/year = 2.97 m³/s
# Use OUTFL = 2.97 m³/s (negative in GETM convention)

# Seasonal variation: add sinusoidal pattern (wet summer, dry winter)
# Base + amplitude * sin(2*pi*(day-120)/365)  -- peak around day 210 (late July)

BASE_INFL1 = 2.0  # m³/s
BASE_INFL2 = 1.0  # m³/s
SEASONAL_AMP = 0.5  # 50% seasonal variation

# First read meteo to get actual precip/evap, then design outflow for water balance
# (Moved after meteo reading below)

discharge = {}
for day in range(N_DAYS):
    seasonal = 1.0 + SEASONAL_AMP * math.sin(2 * math.pi * (day - 120) / 365.0)
    if day == 0:
        discharge["INFL1"] = np.zeros(N_DAYS)
        discharge["INFL2"] = np.zeros(N_DAYS)
        discharge["OUTFL"] = np.zeros(N_DAYS)
    discharge["INFL1"][day] = BASE_INFL1 * seasonal
    discharge["INFL2"][day] = BASE_INFL2 * seasonal
    # OUTFL will be filled after reading meteo data

print(f"\nWater balance (m³/s):")
print(f"  INFL1: mean={discharge['INFL1'].mean():.3f}, sum={discharge['INFL1'].sum()*86400:.0f} m³")
print(f"  INFL2: mean={discharge['INFL2'].mean():.3f}, sum={discharge['INFL2'].sum()*86400:.0f} m³")
print(f"  OUTFL: mean={discharge['OUTFL'].mean():.3f}, sum={discharge['OUTFL'].sum()*86400:.0f} m³")
total_inflow = discharge["INFL1"].sum() + discharge["INFL2"].sum()
total_outflow = -discharge["OUTFL"].sum()
print(f"  Total inflow: {total_inflow*86400:.0f} m³ = {total_inflow*86400/1e6:.2f} Mm³")
print(f"  Total outflow: {total_outflow*86400:.0f} m³ = {total_outflow*86400/1e6:.2f} Mm³")
print(f"  Net (in-out): {(total_inflow-total_outflow)*86400:.0f} m³ = precip-evap={LAKE_AREA*(0.9-1.0):.0f} m³")

# Water quality (based on Luomahu values, simplified constant)
# Inflow rivers: moderate nutrient levels
# Outflow: use lake WQ (will be overwritten by model)
RIVER_WQ = {
    "INFL1": {"temp": 12.0, "nh4": 0.15, "no3": 1.2, "po4": 0.025},
    "INFL2": {"temp": 12.0, "nh4": 0.10, "no3": 0.8, "po4": 0.020},
    "OUTFL": {"temp": 12.0, "nh4": 0.05, "no3": 1.0, "po4": 0.020},  # approximate lake WQ
}

# rivers.nc will be written after meteo data is read (to compute OUTFL with water balance)
rivers_path = os.path.join(CASE_DIR, "rivers.nc")

# ============================================================
# 3. Generate meteo.nc (based on Luomahu climate)
# ============================================================
print("\n" + "=" * 70)
print("Step 3: Generating meteo.nc")
print("=" * 70)

# Read Luomahu meteo data for reference
try:
    import openpyxl
    wb = openpyxl.load_workbook(LUOMAHU_INPUTS, data_only=True)
    ws1 = wb["气象数据"]
    ws2 = wb["风速风向"]

    # Read Luomahu data
    luomahu_meteo = {
        "t2": np.full(N_DAYS, 10.0),
        "slp": np.full(N_DAYS, 101300.0),
        "rh": np.full(N_DAYS, 70.0),
        "tcc": np.full(N_DAYS, 0.5),
        "precip": np.zeros(N_DAYS),
        "evap": np.zeros(N_DAYS),
        "u10": np.zeros(N_DAYS),
        "v10": np.zeros(N_DAYS),
    }

    for row in ws1.iter_rows(min_row=2, values_only=True):
        if row[1] is None or not isinstance(row[1], datetime):
            continue
        days = (row[1] - START_DATE).days
        if 0 <= days < N_DAYS:
            if row[2] is not None: luomahu_meteo["slp"][days] = float(row[2]) * 100.0
            if row[3] is not None: luomahu_meteo["t2"][days] = float(row[3])
            if row[4] is not None: luomahu_meteo["rh"][days] = float(row[4])
            if row[5] is not None: luomahu_meteo["precip"][days] = float(row[5]) / 86400.0
            if row[6] is not None: luomahu_meteo["evap"][days] = -abs(float(row[6])) / 86400.0
            if row[8] is not None:
                cloud = float(row[8])
                if cloud > 1.0: cloud = cloud / 10.0
                luomahu_meteo["tcc"][days] = cloud

    for row in ws2.iter_rows(min_row=2, values_only=True):
        if row[0] is None or not isinstance(row[0], datetime):
            continue
        days = (row[0] - START_DATE).days
        if 0 <= days < N_DAYS:
            speed = float(row[1]) if row[1] else 0.0
            direction = float(row[2]) if row[2] else 0.0
            if speed > 100: speed = 0.0
            rad = math.radians(direction)
            luomahu_meteo["u10"][days] = -speed * math.sin(rad)
            luomahu_meteo["v10"][days] = -speed * math.cos(rad)

    print(f"  Read Luomahu meteo: {N_DAYS} days")
    print(f"  precip: mean={luomahu_meteo['precip'].mean()*86400*1000:.2f} mm/d")
    print(f"  evap: mean={luomahu_meteo['evap'].mean()*86400*1000:.2f} mm/d")
    meteo = luomahu_meteo

    # Now fill OUTFL discharge based on actual meteo data for strict water balance
    # Water balance: dV/dt = Inflow + Precip*Area - Evap*Area - Outflow = 0 (steady state)
    # Outflow = Inflow + (Precip - Evap) * Area
    # Sign: OUTFL is negative (outflow in GETM convention)
    print("\n  Computing OUTFL for strict water balance...")
    for day in range(N_DAYS):
        seasonal = 1.0 + SEASONAL_AMP * math.sin(2 * math.pi * (day - 120) / 365.0)
        inflow_total = (BASE_INFL1 + BASE_INFL2) * seasonal  # m³/s
        precip_m3s = max(0, meteo["precip"][day]) * LAKE_AREA  # m³/s (precip already in m/s)
        evap_m3s = max(0, -meteo["evap"][day]) * LAKE_AREA  # m³/s (evap stored as negative)
        # Outflow = Inflow + Precip - Evap (positive value, then negate for GETM)
        outflow_pos = inflow_total + precip_m3s - evap_m3s
        discharge["OUTFL"][day] = -outflow_pos  # negative = outflow

except Exception as e:
    print(f"  Warning: could not read Luomahu data ({e}), using synthetic")
    # Synthetic data if Luomahu unavailable
    meteo = {
        "t2": np.array([10 + 12 * math.sin(2 * math.pi * (d - 80) / 365.0) for d in range(N_DAYS)]),
        "slp": np.full(N_DAYS, 101300.0),
        "rh": np.array([70 + 10 * math.sin(2 * math.pi * d / 365.0) for d in range(N_DAYS)]),
        "tcc": np.full(N_DAYS, 0.5),
        "precip": np.array([2.5e-7 * (1 + 0.5 * math.sin(2 * math.pi * (d - 120) / 365.0)) for d in range(N_DAYS)]),
        "evap": np.array([-2.8e-7 * (1 + 0.6 * math.sin(2 * math.pi * (d - 150) / 365.0)) for d in range(N_DAYS)]),
        "u10": np.array([3.0 * math.sin(2 * math.pi * d / 365.0) for d in range(N_DAYS)]),
        "v10": np.array([2.0 * math.cos(2 * math.pi * d / 365.0) for d in range(N_DAYS)]),
    }
    # Fill OUTFL with synthetic meteo too
    print("  Computing OUTFL for strict water balance (synthetic)...")
    for day in range(N_DAYS):
        seasonal = 1.0 + SEASONAL_AMP * math.sin(2 * math.pi * (day - 120) / 365.0)
        inflow_total = (BASE_INFL1 + BASE_INFL2) * seasonal
        precip_m3s = max(0, meteo["precip"][day]) * LAKE_AREA
        evap_m3s = max(0, -meteo["evap"][day]) * LAKE_AREA
        outflow_pos = inflow_total + precip_m3s - evap_m3s
        discharge["OUTFL"][day] = -outflow_pos

# Write meteo.nc (GETM format: C dims (time, lat, lon), Fortran reverses to (lon, lat, time))
meteo_path = os.path.join(CASE_DIR, "meteo.nc")
print(f"Writing {meteo_path}...")

ds = nc.Dataset(meteo_path, "w", format="NETCDF4")
ds.createDimension("lon", NX)
ds.createDimension("lat", NY)
ds.createDimension("time", N_DAYS)

# Read lon/lat from bathymetry
bathy_ds = nc.Dataset(bathy_path)
lonc = bathy_ds.variables["lonc"][:]
latc = bathy_ds.variables["latc"][:]
bathy_ds.close()
lon_1d = lonc[0, :]
lat_1d = latc[:, 0]

lon_var = ds.createVariable("lon", "f8", ("lon",))
lon_var.units = "degrees_east"
lon_var[:] = lon_1d

lat_var = ds.createVariable("lat", "f8", ("lat",))
lat_var.units = "degrees_north"
lat_var[:] = lat_1d

time_var = ds.createVariable("time", "f8", ("time",))
time_var.units = "seconds since 2020-01-01 00:00:00"
time_var[:] = np.arange(N_DAYS) * 86400.0

# Meteorological variables - C order (time, lat, lon)
var_specs_f32 = [
    ("u10", "m s-1", "10m wind u-component"),
    ("v10", "m s-1", "10m wind v-component"),
    ("slp", "Pa", "sea level pressure"),
    ("t2", "degC", "2m air temperature"),
    ("rh", "1", "relative humidity"),
    ("tcc", "1", "total cloud cover"),
]
var_specs_f64 = [
    ("precip", "m s-1", "precipitation rate"),
    ("evap", "m s-1", "evaporation rate (negative = water loss)"),
]

for var_name, units, long_name in var_specs_f32:
    var = ds.createVariable(var_name, "f4", ("time", "lat", "lon"))
    var.units = units
    var.long_name = long_name
    # Broadcast 1D time series to 3D (time, lat, lon)
    data_1d = meteo[var_name]
    var[:] = np.broadcast_to(data_1d[:, np.newaxis, np.newaxis], (N_DAYS, NY, NX))

for var_name, units, long_name in var_specs_f64:
    var = ds.createVariable(var_name, "f8", ("time", "lat", "lon"))
    var.units = units
    var.long_name = long_name
    data_1d = meteo[var_name]
    var[:] = np.broadcast_to(data_1d[:, np.newaxis, np.newaxis], (N_DAYS, NY, NX))

ds.title = "Theoretical Lake meteorology (based on Luomahu)"
ds.close()
print("  Done!")

# Water balance check
precip_mmd = meteo["precip"] * 86400 * 1000
evap_mmd = -meteo["evap"] * 86400 * 1000
fwf_mmd = (meteo["precip"] + meteo["evap"]) * 86400 * 1000
print(f"\n  Water balance (mm/day):")
print(f"    precip: mean={precip_mmd.mean():.3f}, sum={precip_mmd.sum():.1f} mm")
print(f"    evap:   mean={evap_mmd.mean():.3f}, sum={evap_mmd.sum():.1f} mm")
print(f"    fwf:    mean={fwf_mmd.mean():.3f}, total={fwf_mmd.sum()/1000:.3f} m")

# Now write rivers.nc with water-balanced OUTFL
print(f"\nWriting {rivers_path} (with water-balanced OUTFL)...")
total_inflow_vol = (discharge["INFL1"].sum() + discharge["INFL2"].sum()) * 86400  # m³
total_outflow_vol = (-discharge["OUTFL"].sum()) * 86400  # m³
precip_vol = meteo["precip"].sum() * LAKE_AREA * 86400  # m³ (m/s * m² * s)
evap_vol = (-meteo["evap"]).sum() * LAKE_AREA * 86400  # m³
# Water balance: Inflow + Precip = Outflow + Evap (for steady state)
balance_check = total_inflow_vol + precip_vol - total_outflow_vol - evap_vol
print(f"  Water balance check:")
print(f"    Inflow: {total_inflow_vol/1e6:.2f} Mm³")
print(f"    Precip: {precip_vol/1e6:.2f} Mm³")
print(f"    Outflow: {total_outflow_vol/1e6:.2f} Mm³")
print(f"    Evap: {evap_vol/1e6:.2f} Mm³")
print(f"    Balance (should be ~0): {balance_check:.0f} m³")

ds_riv = nc.Dataset(rivers_path, "w", format="NETCDF4")
ds_riv.createDimension("time", None)
time_var = ds_riv.createVariable("time", "f8", ("time",))
time_var.units = "seconds since 2020-01-01 00:00:00"
time_var.long_name = "time"
time_var[:] = np.arange(N_DAYS) * 86400.0

for name in RIVERS:
    var = ds_riv.createVariable(name, "f8", ("time",))
    var.units = "m3/s"
    var.long_name = f"{name} river discharge"
    var[:] = discharge[name]
    wq = RIVER_WQ[name]
    for wq_name, units, long_name in [
        ("temp", "degC", f"{name} temperature"),
        ("nh4", "g/m3", f"{name} ammonium"),
        ("no3", "g/m3", f"{name} nitrate"),
        ("po4", "g/m3", f"{name} phosphate"),
    ]:
        if wq_name == "temp":
            vals = np.array([wq["temp"] + 10 * math.sin(2 * math.pi * (d - 80) / 365.0) for d in range(N_DAYS)])
        else:
            vals = np.full(N_DAYS, wq[wq_name])
        var = ds_riv.createVariable(f"{name}_{wq_name}", "f8", ("time",))
        var.units = units
        var.long_name = long_name
        var[:] = vals
ds_riv.title = "Theoretical Lake river data"
ds_riv.close()
print("  Done!")

# ============================================================
# 4. Generate fabm_init.nc (initial conditions)
# ============================================================
print("\n" + "=" * 70)
print("Step 4: Generating fabm_init.nc")
print("=" * 70)

# Macrophytes: 30% coverage in SE bay (11/35 = 31% ≈ 30%)
# SE bay cells: i>=2 (0-indexed) and j>=4 -> 3x3 = 9 cells, need 11, add 2 more
macrophyte_mask = np.zeros((NY, NX), dtype=bool)
# SE bay main area (3x3 = 9 cells)
for j in range(4, NY):  # j=4,5,6
    for i in range(2, NX):  # i=2,3,4
        macrophyte_mask[j, i] = True
# Add 2 more cells to reach 11 cells (31% ≈ 30%)
macrophyte_mask[3, 3] = True  # extend north
macrophyte_mask[3, 4] = True  # extend north
n_macro = macrophyte_mask.sum()
print(f"  Macrophyte cells: {n_macro}/{NX*NY} = {n_macro/(NX*NY)*100:.0f}%")

# Read Luomahu fabm_init.nc structure
luomahu_init = os.path.join(LUOMAHU_CASE, "fabm_init.nc")
if os.path.exists(luomahu_init):
    src_ds = nc.Dataset(luomahu_init)
    print(f"  Using Luomahu fabm_init.nc as template")

    fabm_init_path = os.path.join(CASE_DIR, "fabm_init.nc")
    ds = nc.Dataset(fabm_init_path, "w", format="NETCDF4")

    # Copy dimensions but resize to our grid
    for dname, dvar in src_ds.dimensions.items():
        if dname == "lon":
            ds.createDimension(dname, NX)
        elif dname == "lat":
            ds.createDimension(dname, NY)
        elif dname == "xc":
            ds.createDimension(dname, NX)
        elif dname == "yc":
            ds.createDimension(dname, NY)
        elif dname == "time":
            ds.createDimension(dname, 1)
        else:
            ds.createDimension(dname, len(dvar) if not dvar.isunlimited() else None)

    # Copy coordinate variables
    for vname, vvar in src_ds.variables.items():
        dims = vvar.dimensions
        vdata = vvar[:]

        # Handle dimension remapping
        new_dims = []
        for d in dims:
            if d == "lon" or d == "xc": new_dims.append(d)
            elif d == "lat" or d == "yc": new_dims.append(d)
            else: new_dims.append(d)

        new_var = ds.createVariable(vname, vvar.dtype, tuple(new_dims))
        new_var.setncatts({k: vvar.getncattr(k) for k in vvar.ncattrs()})

        # Fill with appropriate values
        if len(dims) == 2 and ("lon" in dims or "xc" in dims) and ("lat" in dims or "yc" in dims):
            # 2D spatial variable
            if "macrophytes" in vname.lower() or "sD" in vname and "macro" in vname.lower():
                # Macrophyte: 30 gDW/m² in SE bay
                data = np.zeros((NY, NX))
                data[macrophyte_mask] = 30.0
                new_var[:] = data
            elif vname in ["lonc", "lon", "xc"]:
                new_var[:] = lonc
            elif vname in ["latc", "lat", "yc"]:
                new_var[:] = latc
            else:
                # Default: fill with 0 or mean value
                if vdata.size > 0:
                    fill_val = np.nanmean(vdata)
                else:
                    fill_val = 0.0
                data = np.full((NY, NX), fill_val)
                new_var[:] = data
        elif len(dims) == 1:
            if vname in ["lon", "xc"]:
                new_var[:] = lon_1d
            elif vname in ["lat", "yc"]:
                new_var[:] = lat_1d
            elif vname == "time":
                new_var[:] = [0.0]
            else:
                new_var[:] = vdata[:]
        else:
            # Other variables: copy as is (with size adjustment)
            new_var[:] = vdata[:]

    src_ds.close()
    ds.close()
    print("  Done!")
else:
    print("  WARNING: Luomahu fabm_init.nc not found, skipping")

# ============================================================
# 5. Copy fabm.yaml, getm.inp, getm_fabm.inp from Luomahu and modify
# ============================================================
print("\n" + "=" * 70)
print("Step 5: Generating configuration files")
print("=" * 70)

# Copy fabm.yaml from Luomahu
luomahu_fabm = os.path.join(LUOMAHU_CASE, "fabm.yaml")
if os.path.exists(luomahu_fabm):
    with open(luomahu_fabm, "r", encoding="utf-8") as f:
        fabm_content = f.read()
    fabm_path = os.path.join(CASE_DIR, "fabm.yaml")
    with open(fabm_path, "w", encoding="utf-8") as f:
        f.write(fabm_content)
    print(f"  fabm.yaml: copied from Luomahu")

# Generate getm.inp
getm_inp = """! Theoretical Lake - GETM-FABM-WET configuration

&param
    dryrun       = .false.
    runid        = 'THEORETICAL_LAKE'
    title        = 'Theoretical Lake GETM-FABM-WET'
    parallel     = .false.
    runtype      = 4
    hotstart     = .false.
    use_epoch    = .false.
    save_initial = .false.
/

&time
    timestep     = 30.0
    timefmt      = 2
    start        = '2020-01-01 00:00:00'
    stop         = '2020-12-31 00:00:00'
/

&domain
    vert_cord    = 1
    maxdepth = 6.0
    bathy_format = 2
    bathymetry   = 'bathymetry.nc'
    f_plane      = .true.
    il = 1
    ih = 5
    jl = 1
    jh = 7
    crit_depth = 0.3
    min_depth = 0.1
    kdum         = 10
    z0_method    = 0
    z0_const     = 0.001
    check_cfl    = .false.
/

&meteo
    metforcing   = .true.
    on_grid      = .true.
    calc_met     = .true.
    met_method   = 2
    meteo_file   = 'meteo_input.txt'
    fwf_method   = 2
    tx           = 0.0
    ty           = 0.0
    swr_const    = -100.0
    shf_const    = 0.0
/

&rivers
    river_method = 1
/

&m2d
    elev_method = 1
    elev_const  = 0.0
    MM = 35
    vel2d_adv_split = 1
    vel2d_adv_hor   = 1
    Am          = 1.0
    An_method   = 0
    An_const    = 0.001
/

&m3d
    M = 10
    cnpar = 1.0
    cord_relax = 0.0
    adv_ver_iterations = 1
    vel3d_adv_split = 1
    vel3d_adv_hor = 1
    vel3d_adv_ver = 1
    turb_adv_split = 1
    turb_adv_hor = 1
    turb_adv_ver = 1
    calc_temp = .true.
    calc_salt = .false.
    avmback = 0.0
    avhback = 0.0
    ip_method = 1
    ip_ramp = -1
    vel_check = 0
    min_vel = 0.0
    max_vel = 0.0
    bdy3d = .false.
    bdyfmt_3d = 1
    bdy3d_ramp = 0
    bdyfile_3d = ' '
    bdy3d_tmrlx = .false.
    bdy3d_tmrlx_ucut = 0.0
    bdy3d_tmrlx_max = 0.0
    bdy3d_tmrlx_min = 0.0
/

&temp
    temp_method = 1
    temp_const = 5.0
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
    T0 = 10.0
    S0 = 35.0
    p0 = 0.0
    dtr0 = 0.0002
    dsr0 = 0.0008
/

&io_spec
    out_fmt = 2
    hotin_fmt = 2
    hotout_fmt = 2
    save_metrics = .false.
    save_masks = .false.
    save_2d = .true.
    save_3d = .true.
    save_vel = .true.
    destag = .false.
    save_strho = .true.
    save_s = .false.
    save_t = .true.
    save_rho = .false.
    save_rad = .false.
    save_turb = .true.
    save_tke = .true.
    save_eps = .true.
    save_num = .true.
    save_nuh = .true.
    save_ss_nn = .false.
    save_taub = .false.
    first_2d = 1
    step_2d = 1440
    sync_2d = 1440
    first_3d = 1
    step_3d = 1440
    sync_3d = 1440
    save_meteo = .false.
    save_numerical_analyses = .false.
/

&getm_fabm
    fabm_config = 'fabm.yaml'
    fabm = .true.
/
&diagnostics
    diagnostics = .false.
/
"""

getm_path = os.path.join(CASE_DIR, "getm.inp")
with open(getm_path, "w", encoding="utf-8") as f:
    f.write(getm_inp)
print(f"  getm.inp: generated")

# Generate getm_fabm.inp (YAML mode: only namelist-recognized variables;
# fabm_calc/repair_state/nsave are controlled by gotm_fabm.yaml)
getm_fabm_inp = """&getm_fabm_nml
 fabm_init_method   =  2,
 fabm_init_file    =  'fabm_init.nc',
 fabm_init_format  =  2,
 fabm_field_no     =  1,
 fabm_adv_hor      =  4,
 fabm_adv_ver      =  4,
 fabm_adv_split    =  1,
 fabm_AH           = -1.,
/
"""

getm_fabm_path = os.path.join(CASE_DIR, "getm_fabm.inp")
with open(getm_fabm_path, "w", encoding="utf-8") as f:
    f.write(getm_fabm_inp)
print(f"  getm_fabm.inp: generated")

# Create meteo_input.txt (placeholder, GETM reads from meteo.nc when on_grid=.true.)
meteo_txt_path = os.path.join(CASE_DIR, "meteo_input.txt")
with open(meteo_txt_path, "w", encoding="utf-8") as f:
    f.write("meteo.nc\n")
print(f"  meteo_input.txt: generated")

print("\n" + "=" * 70)
print("All input files generated successfully!")
print("=" * 70)
print(f"\nLake specifications:")
print(f"  Grid: {NX} x {NY} cells ({DX}m x {DY}m)")
print(f"  Area: {LAKE_AREA/1e6:.2f} km²")
print(f"  Volume: {lake_volume/1e6:.2f} Mm³")
print(f"  Average depth: {bathymetry.mean():.2f} m")
print(f"  Max depth: {bathymetry.max():.2f} m")
print(f"  Sigma layers: 10")
print(f"  Rivers: 2 inflows (NE, NW), 1 outflow (SW)")
print(f"  Macrophyte coverage: {n_macro}/{NX*NY} = {n_macro/(NX*NY)*100:.0f}% (SE bay)")
print(f"  Simulation: {N_DAYS} days (2020-01-01 to 2020-12-31)")
print(f"\nFiles in {CASE_DIR}:")
for f in os.listdir(CASE_DIR):
    fpath = os.path.join(CASE_DIR, f)
    if os.path.isfile(fpath):
        print(f"  {f}: {os.path.getsize(fpath)} bytes")
