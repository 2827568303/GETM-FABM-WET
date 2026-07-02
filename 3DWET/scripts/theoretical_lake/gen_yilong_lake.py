"""Generate all input files for Yilong-Lake-based theoretical test case.

Yilong Lake (异龙湖) - based on real lake parameters:
- Location: Yunnan, China (23.5°N, 102.5°E), elevation 1414m
- Shape: elongated east-west, 13.8km × 1.4-3.6km (avg 2.5km)
- Area: ~40 km², avg depth 3.5m, max depth 7m
- Volume: 1.149×10^8 m³ (114.9 Mm³)
- 7 inflow rivers, 1 outflow river (east)
- Water quality: eutrophic, TN/TP high, COD worse than Class V

Grid design (500m × 500m):
- NX=28 (east-west), NY=8 (north-south)
- Total cells: 224 (with lake shape mask, ~140 active)
- Lake shape: elongated oval, wider in middle, narrower at ends
- Bathymetry: deeper in center (5-7m), shallower at edges (1-3m)
- Outflow at east end, 2 main inflows (north + west)

Initial conditions (FIXED from previous cascade crash):
- Phytoplankton: raised to PCLake Turbid defaults (0.2-0.5)
- Zooplankton: raised to 0.3 (avoid starvation)
- Fish: lowered by 50% (reduce predation pressure)
- Nutrients: moderate eutrophic levels

Generated files (in case/Yilong/):
- bathymetry.nc, riverinfo.dat, rivers.nc, meteo.nc, fabm_init.nc
"""
import numpy as np
import netCDF4 as nc
from datetime import datetime, timedelta
import os
import math

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_GETM_ROOT = os.path.dirname(os.path.dirname(_SCRIPT_DIR))
CASE_DIR = os.path.join(_GETM_ROOT, "case", "Yilong")
os.makedirs(CASE_DIR, exist_ok=True)

# ============================================================
# Yilong Lake parameters
# ============================================================
NX, NY = 28, 8  # east-west × north-south
DX = DY = 500.0  # grid size (m)
AVG_DEPTH = 3.5  # m (real Yilong: 3.5-4m)
MAX_DEPTH = 7.0  # m (real Yilong max depth)
MIN_DEPTH = 1.0  # m
N_DAYS = 366  # 2020 leap year
START_DATE = datetime(2020, 1, 1)

# Yilong Lake location (Yunnan, ~23.5°N, 102.5°E, elevation 1414m)
LAT0, LON0 = 23.55, 102.50
X0_UTM, Y0_UTM = 660000.0, 2600000.0  # UTM zone 48N approx

# Lake area (real Yilong ~40 km²)
LAKE_AREA_FULL = NX * NY * DX * DY  # 28*8*500*500 = 56,000,000 m² = 56 km² (max possible)
# Actual lake area will be smaller due to land mask (target ~40 km²)

# ============================================================
# 1. Design lake shape mask (elongated east-west, oval)
# ============================================================
print("=" * 70)
print("Step 1: Generating Yilong-like lake bathymetry")
print("=" * 70)

# Create lake mask: elongated oval with width variation
# Yilong is widest in middle (~3.6km), narrower at ends (~1.4km)
lake_mask = np.zeros((NY, NX), dtype=bool)
cx = (NX - 1) / 2.0  # center x
for j in range(NY):
    cy = j - (NY - 1) / 2.0  # distance from center y
    for i in range(NX):
        dx = (i - cx) / cx  # normalized x distance (-1 to 1)
        # Lake half-width at this x position (narrower at ends, wider in middle)
        # Use cosine-shaped width profile
        half_width = 0.5 + 0.45 * math.cos(dx * math.pi * 0.8)  # 0.05 to 0.95
        half_width = max(0.05, min(1.0, half_width))
        if abs(cy / ((NY - 1) / 2.0)) <= half_width:
            lake_mask[j, i] = True

n_water = lake_mask.sum()
lake_area = n_water * DX * DY
print(f"Lake cells: {n_water}/{NX*NY} = {n_water/(NX*NY)*100:.1f}%")
print(f"Lake area: {lake_area/1e6:.2f} km² (target ~40 km², real Yilong ~40 km²)")

# ============================================================
# 2. Design bathymetry (deeper in center, shallower at edges)
# ============================================================
bathymetry = np.full((NY, NX), -9999.0)  # land = -9999
for j in range(NY):
    for i in range(NX):
        if not lake_mask[j, i]:
            continue
        # Distance from lake center, normalized
        dx_norm = (i - cx) / cx
        cy_lake = (NY - 1) / 2.0
        # Find the half-width at this x position
        half_width = 0.5 + 0.45 * math.cos(dx_norm * math.pi * 0.8)
        half_width = max(0.05, min(1.0, half_width))
        # Normalized distance from center y (0 = center, 1 = edge)
        dy_norm = abs(j - cy_lake) / (cy_lake * half_width)

        # Depth profile: deeper in center, shallower at edges
        # Use quadratic falloff
        depth_factor = 1.0 - 0.7 * dy_norm**2  # center=1.0, edge=0.3
        # Also slight east-west gradient (east end slightly deeper, real Yilong outflow area)
        ew_factor = 1.0 + 0.1 * dx_norm  # east deeper by 10%
        base_depth = MAX_DEPTH * depth_factor * ew_factor
        base_depth = max(MIN_DEPTH, min(MAX_DEPTH, base_depth))
        bathymetry[j, i] = base_depth

# Adjust to target average depth
water_depths = bathymetry[lake_mask]
current_avg = water_depths.mean()
scale = AVG_DEPTH / current_avg
bathymetry[lake_mask] = np.clip(bathymetry[lake_mask] * scale, MIN_DEPTH, MAX_DEPTH)

print(f"Bathymetry (water cells only): avg={bathymetry[lake_mask].mean():.2f}m, "
      f"min={bathymetry[lake_mask].min():.2f}m, max={bathymetry[lake_mask].max():.2f}m")
lake_volume = np.sum(bathymetry[lake_mask]) * DX * DY
print(f"Lake volume: {lake_volume:.0f} m³ = {lake_volume/1e6:.2f} Mm³ (real Yilong ~114.9 Mm³)")

# ============================================================
# 3. Write bathymetry.nc
# ============================================================
bathy_path = os.path.join(CASE_DIR, "bathymetry.nc")
print(f"Writing {bathy_path}...")

ds = nc.Dataset(bathy_path, "w", format="NETCDF4")
ds.createDimension("x", NX)
ds.createDimension("y", NY)
ds.createDimension("xq", NX + 1)
ds.createDimension("yq", NY + 1)

grid_type_var = ds.createVariable("grid_type", "i4")
grid_type_var[:] = 1

x_var = ds.createVariable("x", "f8", ("x",))
x_var.units = "m"
x_var.long_name = "x coordinate of cell centers"
x_var[:] = X0_UTM + np.arange(NX) * DX + DX / 2

y_var = ds.createVariable("y", "f8", ("y",))
y_var.units = "m"
y_var.long_name = "y coordinate of cell centers"
y_var[:] = Y0_UTM + np.arange(NY) * DY + DY / 2

lat_var = ds.createVariable("latc", "f8", ("y", "x"))
lat_var.units = "degrees_north"
lat_var.long_name = "latitude of cell centers"
for j in range(NY):
    lat_var[j, :] = LAT0 + ((NY - 1) / 2.0 - j) * (DY / 111000.0)

lon_var = ds.createVariable("lonc", "f8", ("y", "x"))
lon_var.units = "degrees_east"
lon_var.long_name = "longitude of cell centers"
cos_lat = math.cos(math.radians(LAT0))
for i in range(NX):
    lon_var[:, i] = LON0 + (i - (NX - 1) / 2.0) * (DX / (111000.0 * cos_lat))

bath_var = ds.createVariable("bathymetry", "f8", ("y", "x"))
bath_var.units = "m"
bath_var.long_name = "water depth"
bath_var.standard_name = "sea_floor_depth"
bath_var.coordinates = "lonc latc"
bath_var[:] = bathymetry

ds.title = "Yilong-like Lake Bathymetry"
ds.source = "Generated by gen_yilong_lake.py"
ds.history = f"Created {datetime.now()}"
ds.Conventions = "CF-1.0"
ds.close()
print("  Done!")

# ============================================================
# 4. River positions (3 inflows + 1 outflow)
# ============================================================
print("\n" + "=" * 70)
print("Step 2: Generating rivers")
print("=" * 70)

# Find river positions on lake edges
# Yilong Lake: 7 inflows, 1 outflow (east)
# Simplified: 3 inflows (north, west, south) + 1 outflow (east)
def find_edge_cell(side, lake_mask):
    """Find a water cell on the specified edge (or closest water row/col)."""
    NY_l, NX_l = lake_mask.shape
    if side == "north":  # j=min row with water
        for j in range(NY_l):
            for i in range(NX_l):
                if lake_mask[j, i]:
                    # Find middle i in this row
                    water_is = [ii for ii in range(NX_l) if lake_mask[j, ii]]
                    return water_is[len(water_is)//2], j
    elif side == "south":  # j=max row with water
        for j in range(NY_l - 1, -1, -1):
            for i in range(NX_l):
                if lake_mask[j, i]:
                    water_is = [ii for ii in range(NX_l) if lake_mask[j, ii]]
                    return water_is[len(water_is)//2], j
    elif side == "west":  # i=min col with water
        for i in range(NX_l):
            for j in range(NY_l):
                if lake_mask[j, i]:
                    water_js = [jj for jj in range(NY_l) if lake_mask[jj, i]]
                    return i, water_js[len(water_js)//2]
    elif side == "east":  # i=max col with water
        for i in range(NX_l - 1, -1, -1):
            for j in range(NY_l):
                if lake_mask[j, i]:
                    water_js = [jj for jj in range(NY_l) if lake_mask[jj, i]]
                    return i, water_js[len(water_js)//2]
    return None

# Place rivers
infl1_pos = find_edge_cell("north", lake_mask)  # North inflow
infl2_pos = find_edge_cell("west", lake_mask)   # West inflow (main)
infl3_pos = find_edge_cell("south", lake_mask)  # South inflow
outfl_pos = find_edge_cell("east", lake_mask)   # East outflow

# 1-indexed for GETM
RIVERS = {
    "INFL1": {"pos": [(infl1_pos[0]+1, infl1_pos[1]+1)], "type": "inflow",
              "base_flow": 1.5, "name": "北入流"},
    "INFL2": {"pos": [(infl2_pos[0]+1, infl2_pos[1]+1)], "type": "inflow",
              "base_flow": 3.0, "name": "西入流(主)"},
    "INFL3": {"pos": [(infl3_pos[0]+1, infl3_pos[1]+1)], "type": "inflow",
              "base_flow": 1.0, "name": "南入流"},
    "OUTFL": {"pos": [(outfl_pos[0]+1, outfl_pos[1]+1)], "type": "outflow",
              "base_flow": None, "name": "东出流"},
}

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
        print(f"    {name} ({info['name']}): ({i},{j}) - {info['type']}")

# ============================================================
# 5. Generate meteo.nc (Yunnan plateau climate)
# ============================================================
print("\n" + "=" * 70)
print("Step 3: Generating meteo.nc (Yunnan plateau climate)")
print("=" * 70)

# Yunnan plateau climate (23.5°N, 1414m elevation):
# - Mild year-round, small temperature range
# - Wet season: May-Oct, Dry season: Nov-Apr
# - Annual precip: ~900mm, evap: ~1100mm
# - Avg temp: 18°C (summer 22°C, winter 10°C)
# - Wind: moderate, SW monsoon in summer

# Generate synthetic but realistic Yunnan climate
days = np.arange(N_DAYS)
# Temperature: sinusoidal, peak in June (~day 170), avg 18°C, range 10-25°C
temp_annual = 18.0 + 7.5 * np.sin(2 * np.pi * (days - 110) / 365.0)
# Diurnal not modeled (daily avg)

# Precipitation: wet season May-Oct (days 120-300), dry season Nov-Apr
precip_daily_mm = np.zeros(N_DAYS)
for d in range(N_DAYS):
    if 120 <= d <= 300:  # wet season
        base = 4.0  # mm/day average in wet season
        # add stochastic variation
        np.random.seed(d)
        precip_daily_mm[d] = max(0, base + np.random.exponential(3.0))
    else:  # dry season
        precip_daily_mm[d] = max(0, np.random.exponential(0.5))
precip_mms = precip_daily_mm / 86400.0 / 1000.0  # m/s

# Evaporation: higher in dry season (sun + wind), lower in wet season (cloud)
evap_daily_mm = np.zeros(N_DAYS)
for d in range(N_DAYS):
    if 120 <= d <= 300:  # wet season, more clouds
        evap_daily_mm[d] = 2.5 + 1.0 * math.sin(2 * math.pi * (d - 150) / 365.0)
    else:  # dry season, more sun
        evap_daily_mm[d] = 4.0 + 1.5 * math.sin(2 * math.pi * (d - 60) / 365.0)
evap_daily_mm = np.maximum(evap_daily_mm, 0)
evap_mms = -evap_daily_mm / 86400.0 / 1000.0  # negative = water loss

# Wind: SW monsoon in summer (May-Oct), NE in winter
u10 = np.array([2.5 * math.sin(2 * math.pi * (d - 150) / 365.0) for d in range(N_DAYS)])
v10 = np.array([1.5 * math.cos(2 * math.pi * (d - 150) / 365.0) for d in range(N_DAYS)])

# Other meteo
slp = np.full(N_DAYS, 86000.0)  # low pressure at 1414m elevation (~86 kPa)
rh = np.array([70 + 15 * math.sin(2 * math.pi * (d - 200) / 365.0) for d in range(N_DAYS)])
rh = np.clip(rh, 30, 95)
tcc = np.array([0.4 + 0.3 * math.sin(2 * math.pi * (d - 200) / 365.0) for d in range(N_DAYS)])
tcc = np.clip(tcc, 0.1, 0.9)

meteo = {
    "t2": temp_annual, "slp": slp, "rh": rh, "tcc": tcc,
    "precip": precip_mms.astype(np.float64),
    "evap": evap_mms.astype(np.float64),
    "u10": u10, "v10": v10,
}

print(f"  Temperature: avg={meteo['t2'].mean():.1f}°C, range=[{meteo['t2'].min():.1f},{meteo['t2'].max():.1f}]")
print(f"  Precip: avg={precip_daily_mm.mean():.2f} mm/d, total={precip_daily_mm.sum():.0f} mm/yr")
print(f"  Evap:   avg={evap_daily_mm.mean():.2f} mm/d, total={evap_daily_mm.sum():.0f} mm/yr")
print(f"  P-E:    {(precip_daily_mm.sum()-evap_daily_mm.sum()):.0f} mm/yr")

# Write meteo.nc (C order: time, lat, lon)
meteo_path = os.path.join(CASE_DIR, "meteo.nc")
print(f"Writing {meteo_path}...")

# Re-read lon/lat from bathymetry file (since bathy dataset was closed)
bathy_ds2 = nc.Dataset(bathy_path, "r")
lonc_2d = bathy_ds2.variables["lonc"][:]
latc_2d = bathy_ds2.variables["latc"][:]
bathy_ds2.close()
lon_1d = lonc_2d[0, :]  # first row
lat_1d = latc_2d[:, 0]  # first column

ds_meteo = nc.Dataset(meteo_path, "w", format="NETCDF4")
ds_meteo.createDimension("lon", NX)
ds_meteo.createDimension("lat", NY)
ds_meteo.createDimension("time", N_DAYS)

lon_v = ds_meteo.createVariable("lon", "f8", ("lon",))
lon_v.units = "degrees_east"
lon_v[:] = lon_1d

lat_v = ds_meteo.createVariable("lat", "f8", ("lat",))
lat_v.units = "degrees_north"
lat_v[:] = lat_1d

time_v = ds_meteo.createVariable("time", "f8", ("time",))
time_v.units = "seconds since 2020-01-01 00:00:00"
time_v[:] = np.arange(N_DAYS) * 86400.0

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
    var = ds_meteo.createVariable(var_name, "f4", ("time", "lat", "lon"))
    var.units = units
    var.long_name = long_name
    data_1d = meteo[var_name]
    var[:] = np.broadcast_to(data_1d[:, np.newaxis, np.newaxis], (N_DAYS, NY, NX))

for var_name, units, long_name in var_specs_f64:
    var = ds_meteo.createVariable(var_name, "f8", ("time", "lat", "lon"))
    var.units = units
    var.long_name = long_name
    data_1d = meteo[var_name]
    var[:] = np.broadcast_to(data_1d[:, np.newaxis, np.newaxis], (N_DAYS, NY, NX))

ds_meteo.title = "Yilong Lake meteorology (Yunnan plateau climate)"
ds_meteo.close()
print("  Done!")

# ============================================================
# 6. Compute water-balanced outflow and write rivers.nc
# ============================================================
print("\n" + "=" * 70)
print("Step 4: Computing water balance and writing rivers.nc")
print("=" * 70)

SEASONAL_AMP = 0.4  # 40% seasonal variation (wet season higher inflow)
discharge = {}
for name in RIVERS:
    discharge[name] = np.zeros(N_DAYS)

for day in range(N_DAYS):
    # Wet season (May-Oct, days 120-300) higher inflow
    if 120 <= day <= 300:
        seasonal = 1.0 + SEASONAL_AMP * math.sin(2 * math.pi * (day - 120) / 180.0)
    else:
        seasonal = 1.0 - SEASONAL_AMP * 0.5
    discharge["INFL1"][day] = RIVERS["INFL1"]["base_flow"] * seasonal
    discharge["INFL2"][day] = RIVERS["INFL2"]["base_flow"] * seasonal
    discharge["INFL3"][day] = RIVERS["INFL3"]["base_flow"] * seasonal
    # Outflow = Inflow + Precip - Evap (water balance)
    inflow_total = discharge["INFL1"][day] + discharge["INFL2"][day] + discharge["INFL3"][day]
    precip_m3s = max(0, meteo["precip"][day]) * lake_area
    evap_m3s = max(0, -meteo["evap"][day]) * lake_area
    outflow_pos = inflow_total + precip_m3s - evap_m3s
    discharge["OUTFL"][day] = -max(0.1, outflow_pos)  # negative for outflow

# Water balance check
total_in = (discharge["INFL1"].sum() + discharge["INFL2"].sum() + discharge["INFL3"].sum()) * 86400
total_out = (-discharge["OUTFL"].sum()) * 86400
precip_vol = meteo["precip"].sum() * lake_area * 86400
evap_vol = (-meteo["evap"]).sum() * lake_area * 86400
balance = total_in + precip_vol - total_out - evap_vol
print(f"  Water balance (366 days):")
print(f"    Inflow:  {total_in/1e6:.2f} Mm³")
print(f"    Precip:  {precip_vol/1e6:.2f} Mm³")
print(f"    Outflow: {total_out/1e6:.2f} Mm³")
print(f"    Evap:    {evap_vol/1e6:.2f} Mm³")
print(f"    Balance (should ~0): {balance:.0f} m³ = {balance/lake_area*1000:.3f} mm")

# River water quality (Yilong eutrophic conditions)
# Inflow rivers: moderate-high nutrients (eutrophic lake)
# Outflow: use approximate lake WQ
RIVER_WQ = {
    "INFL1": {"temp": 15.0, "nh4": 0.20, "no3": 1.5, "po4": 0.05, "doc": 5.0, "poc": 2.0},
    "INFL2": {"temp": 15.0, "nh4": 0.30, "no3": 2.0, "po4": 0.08, "doc": 8.0, "poc": 3.0},
    "INFL3": {"temp": 15.0, "nh4": 0.15, "no3": 1.0, "po4": 0.04, "doc": 4.0, "poc": 1.5},
    "OUTFL": {"temp": 15.0, "nh4": 0.10, "no3": 1.2, "po4": 0.04, "doc": 5.0, "poc": 2.0},
}

rivers_path = os.path.join(CASE_DIR, "rivers.nc")
print(f"Writing {rivers_path}...")
ds_riv = nc.Dataset(rivers_path, "w", format="NETCDF4")
ds_riv.createDimension("time", None)
time_v = ds_riv.createVariable("time", "f8", ("time",))
time_v.units = "seconds since 2020-01-01 00:00:00"
time_v[:] = np.arange(N_DAYS) * 86400.0

for name in RIVERS:
    var = ds_riv.createVariable(name, "f8", ("time",))
    var.units = "m3/s"
    var[:] = discharge[name]
    wq = RIVER_WQ[name]
    # Temperature with seasonal variation
    temp_vals = np.array([wq["temp"] + 8 * math.sin(2 * math.pi * (d - 110) / 365.0) for d in range(N_DAYS)])
    var_t = ds_riv.createVariable(f"{name}_temp", "f8", ("time",))
    var_t.units = "degC"
    var_t[:] = temp_vals
    for wq_name in ["nh4", "no3", "po4", "doc", "poc"]:
        var_wq = ds_riv.createVariable(f"{name}_{wq_name}", "f8", ("time",))
        var_wq.units = "g/m3"
        var_wq[:] = np.full(N_DAYS, wq[wq_name])

ds_riv.title = "Yilong Lake river data"
ds_riv.close()
print("  Done!")

# ============================================================
# 7. Generate fabm_init.nc (initial conditions)
# ============================================================
print("\n" + "=" * 70)
print("Step 5: Generating fabm_init.nc")
print("=" * 70)

# Macrophytes: 25% coverage in shallow areas (depth < 2.5m)
# Yilong has submerged macrophytes in shallow littoral zones
macrophyte_mask = np.zeros((NY, NX), dtype=bool)
for j in range(NY):
    for i in range(NX):
        if lake_mask[j, i] and 1.0 <= bathymetry[j, i] <= 2.5:
            macrophyte_mask[j, i] = True
n_macro = macrophyte_mask.sum()
print(f"  Macrophyte cells: {n_macro} ({n_macro/n_water*100:.1f}% of lake)")

fabm_init_path = os.path.join(CASE_DIR, "fabm_init.nc")
ds_init = nc.Dataset(fabm_init_path, "w", format="NETCDF4")
ds_init.createDimension("x", NX)
ds_init.createDimension("y", NY)
ds_init.createDimension("z", 1)

lon_v = ds_init.createVariable("lon", "f8", ("x",))
lon_v[:] = lon_1d
lat_v = ds_init.createVariable("lat", "f8", ("y",))
lat_v[:] = lat_1d
z_v = ds_init.createVariable("z", "f8", ("z",))
z_v[:] = [0.0]

# Macrophytes initial field (gDW/m²)
macro_var = ds_init.createVariable("macrophytes_sD", "f8", ("z", "y", "x"))
macro_var.units = "gDW/m2"
macro_field = np.zeros((1, NY, NX))
macro_field[0, macrophyte_mask] = 30.0  # 30 gDW/m² initial
macro_var[:] = macro_field

ds_init.title = "Yilong Lake FABM initial conditions"
ds_init.close()
print(f"  Done! ({fabm_init_path})")

# ============================================================
# Summary
# ============================================================
print("\n" + "=" * 70)
print("Summary")
print("=" * 70)
print(f"Lake grid: {NX}×{NY} = {NX*NY} cells ({n_water} water, {n_water/(NX*NY)*100:.1f}%)")
print(f"Lake area: {lake_area/1e6:.2f} km²")
print(f"Avg depth: {bathymetry[lake_mask].mean():.2f} m")
print(f"Max depth: {bathymetry[lake_mask].max():.2f} m")
print(f"Lake volume: {lake_volume/1e6:.2f} Mm³")
print(f"Rivers: 3 inflows + 1 outflow")
print(f"  INFL1 (N): ({RIVERS['INFL1']['pos'][0]})")
print(f"  INFL2 (W): ({RIVERS['INFL2']['pos'][0]})")
print(f"  INFL3 (S): ({RIVERS['INFL3']['pos'][0]})")
print(f"  OUTFL (E): ({RIVERS['OUTFL']['pos'][0]})")
print(f"Macrophytes: {n_macro} cells ({n_macro/n_water*100:.1f}% coverage)")
print(f"\nGenerated files in: {CASE_DIR}")
print("  bathymetry.nc, riverinfo.dat, rivers.nc, meteo.nc, fabm_init.nc")
print("\nNext: update getm.inp, gotm_fabm.yaml, fabm.yaml, getm_fabm.inp")
