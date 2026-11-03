"""Generate all input files for the heart-shaped Theoretical Lake test case.

Theoretical Lake specifications (per user request):
- Shape: heart-shaped with slightly irregular boundary, point pointing south
- Grid: 500 m x 500 m,  i=24 (x, east-west) x j=25 (y, north-south)
- Wet cells: 280  ->  area = 70.0 km²
- Average depth: 5.3 m
- Maximum depth: 10.2 m, located at the lake centre towards the northwest
- 3 inflow rivers:
    * NW-near-middle boundary  : width ~1.2 km (2 cells)
    * NE side boundary         : width 0.5 km (1 cell)
    * West-middle boundary     : width 0.5 km (1 cell)
- 2 outflow rivers:
    * South-centre boundary    : width 0.5 km (1 cell)
    * East-middle boundary     : width ~1.2 km (2 cells)
- Vertical: k=10 sigma layers
- Simulation: 366 days (2020-01-01 to 2020-12-31)
- Strict water balance: inflow + precip = outflow + evap

Generated files (in ../case/):
- bathymetry.nc    : lake topography (heart shape + depth)
- riverinfo.dat    : river positions (7 river cells, 5 rivers)
- rivers.nc        : river discharge + WQ (366 days)
- meteo.nc         : meteorological forcing (366 days, synthetic Luomahu-like)
- fabm_init.nc     : initial conditions for biota
- fabm.yaml        : FABM configuration (copied from Luomahu)
- getm.inp         : GETM configuration
- getm_fabm.inp    : FABM-GETM coupling configuration
- gotm_fabm.yaml   : GOTM-FABM configuration
- gotmturb.nml     : GOTM turbulence configuration
- output.yaml      : output specification
- meteo_input.txt  : pointer to meteo.nc

A human-readable summary of the lake design is also written to ../case/lake_summary.txt
and the heart mask / river map is dumped to ../case/lake_mask.txt for inspection.
"""
import numpy as np
import netCDF4 as nc
from datetime import datetime
import os
import math

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LUOMAHU_CASE = os.path.join(PROJECT_ROOT, "3DWET", "case", "Lake Luoma")

# ------------------------------------------------------------------
# Lake parameters
# ------------------------------------------------------------------
DX = DY = 500.0                  # grid size in metres
NX, NY = 24, 20                  # i=24 (x, E-W), j=20 (y, N-S)
TARGET_WET = 280                 # 280 cells * 0.25 km² = 70.0 km²
AVG_DEPTH = 5.3                  # metres
MAX_DEPTH = 10.2                 # metres (at centre, towards NW)
MIN_DEPTH = 1.0                  # metres (minimum cell depth for stability)
N_SIGMA = 10                     # vertical sigma layers
N_DAYS = 366                     # 2020 is a leap year
START_DATE = datetime(2020, 1, 1)

LAKE_AREA = TARGET_WET * DX * DY  # 70,000,000 m² = 70.0 km²

# Heart-shape normalised coordinates (tuned so wet==280 exactly, fills grid)
Y_TOP, Y_BOT = 1.20, -1.05        # y: north(top/lobes)=1.20, south(point)=-1.05
X_LEFT, X_RIGHT = -1.27, 1.27     # x: west=-1.27, east=1.27
NOISE_AMP = 0.04                  # boundary irregularity amplitude
NOISE_SEED = 42


# ==================================================================
# 1.  Build the heart-shaped, slightly irregular lake mask
# ==================================================================
def heart_mask(nx, ny, y_top, y_bot, x_left, x_right, noise_amp, seed):
    """Return a (ny, nx) boolean mask. j=0 is north (lobes), j=ny-1 is south (point).

    Uses the classic heart curve  (x^2 + y^2 - 1)^3 - x^2 y^3 <= 0  (point down)
    and adds a deterministic low-amplitude perturbation so the shoreline is
    irregular rather than perfectly smooth.
    """
    rng = np.random.default_rng(seed)
    mask = np.zeros((ny, nx), dtype=bool)
    for j in range(ny):
        y = y_top - (y_top - y_bot) * j / (ny - 1)
        for i in range(nx):
            x = x_left + (x_right - x_left) * i / (nx - 1)
            val = (x * x + y * y - 1.0) ** 3 - x * x * y * y * y
            # deterministic multi-frequency perturbation -> irregular shoreline
            noise = (noise_amp * math.sin(5.0 * i / nx + 0.30) * math.cos(7.0 * j / ny + 0.50)
                     + noise_amp * 0.6 * math.sin(11.0 * i / nx) * math.cos(13.0 * j / ny)
                     + noise_amp * 0.3 * math.sin(17.0 * (i + j) / (nx + ny)))
            mask[j, i] = (val + noise) <= 0.0
    return mask


print("=" * 72)
print("Theoretical Lake - heart-shaped, 70 km², avg 5.3 m, max 10.2 m")
print("=" * 72)

mask = heart_mask(NX, NY, Y_TOP, Y_BOT, X_LEFT, X_RIGHT, NOISE_AMP, NOISE_SEED)
n_wet = int(mask.sum())
lake_area_km2 = n_wet * DX * DY / 1e6
print(f"Grid: {NX} x {NY}  |  wet cells: {n_wet}  |  area: {lake_area_km2:.2f} km²")
assert n_wet == TARGET_WET, f"Wet cell count {n_wet} != target {TARGET_WET}"

# 0-indexed wet-cell coordinates.
# np.where returns (row_indices, col_indices) = (j, i) for an (NY, NX) array.
wet_j, wet_i = np.where(mask)


# ==================================================================
# 2.  Locate river mouths on the shoreline
# ==================================================================
def find_boundary_cells(m):
    """A wet cell with at least one dry 4-neighbour (or on the grid edge)."""
    ny, nx = m.shape
    bdy = []
    for j in range(ny):
        for i in range(nx):
            if not m[j, i]:
                continue
            dry_neighbour = False
            for dj, di in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                jj, ii = j + dj, i + di
                if jj < 0 or jj >= ny or ii < 0 or ii >= nx or not m[jj, ii]:
                    dry_neighbour = True
                    break
            if dry_neighbour:
                bdy.append((i, j))
    return bdy


boundary_cells = find_boundary_cells(mask)
print(f"Shoreline cells: {len(boundary_cells)}")


def nearest_boundary(ti, tj, bdy):
    """Return the boundary cell nearest to target (ti, tj)."""
    best = None
    best_d = 1e9
    for (i, j) in bdy:
        d = (i - ti) ** 2 + (j - tj) ** 2
        if d < best_d:
            best_d = d
            best = (i, j)
    return best


def nearest_boundary_pair(ti, tj, bdy):
    """Return two adjacent boundary cells near target (for ~1 km wide rivers).

    Picks the nearest boundary cell, then the closest boundary cell that is
    a 4-neighbour of the first (so the two cells sit side-by-side on the shore).
    """
    first = nearest_boundary(ti, tj, bdy)
    if first is None:
        return None, None
    fi, fj = first
    # find adjacent boundary cell closest to target
    best = None
    best_d = 1e9
    for (i, j) in bdy:
        if (i, j) == first:
            continue
        adj = abs(i - fi) + abs(j - fj) == 1
        if not adj:
            continue
        d = (i - ti) ** 2 + (j - tj) ** 2
        if d < best_d:
            best_d = d
            best = (i, j)
    return first, best


# River target locations (0-indexed i, j) on the heart:
#   j=0  north (two lobes)        j=NY-1 south (point)
#   i=0  west                     i=NX-1 east
#
# 1. INFL_NW  - NW-near-middle, ~1.2 km wide (2 cells)  -> west side of NW lobe, mid-upper
# 2. INFL_NE  - NE side, 0.5 km (1 cell)                -> east side of NE lobe
# 3. INFL_W   - West-middle, 0.5 km (1 cell)            -> west shore at the equator
# 4. OUTFL_S  - South-centre, 0.5 km (1 cell)           -> southern tip (point)
# 5. OUTFL_E  - East-middle, ~1.2 km wide (2 cells)     -> east shore at the equator

RIVER_SPECS = [
    # name,        type,     ncells, target (i, j)   (0-indexed)
    ("INFL_NW", "inflow",  2, (4, 6)),     # NW-near-middle, west side of NW lobe
    ("INFL_NE", "inflow",  1, (19, 3)),    # NE side, east side of NE lobe
    ("INFL_W",  "inflow",  1, (1, 10)),    # West-middle, west shore at equator
    ("OUTFL_S", "outflow", 1, (12, 18)),   # South-centre, southern tip
    ("OUTFL_E", "outflow", 2, (22, 10)),   # East-middle, east shore at equator
]

rivers = {}                 # name -> list of (i, j)  (0-indexed)
for name, rtype, ncells, (ti, tj) in RIVER_SPECS:
    if ncells == 1:
        cell = nearest_boundary(ti, tj, boundary_cells)
        cells = [cell]
    else:
        c1, c2 = nearest_boundary_pair(ti, tj, boundary_cells)
        cells = [c for c in (c1, c2) if c is not None]
    rivers[name] = cells
    cells_str = ", ".join(f"({i+1},{j+1})" for (i, j) in cells)   # 1-indexed for display
    print(f"  {name:8s} ({rtype:7s}) {ncells} cell(s) -> {cells_str}")

# total river cells
total_river_cells = sum(len(c) for c in rivers.values())


# ==================================================================
# 3.  Design the bathymetry
#      max 10.2 m at centre-towards-NW,  average 5.3 m
# ==================================================================
print("\nDesigning bathymetry...")

# centroid of wet cells
cx = wet_i.mean()
cy = wet_j.mean()
# lake extent
i_min, i_max = wet_i.min(), wet_i.max()
j_min, j_max = wet_j.min(), wet_j.max()
ext_i = i_max - i_min
ext_j = j_max - j_min

# deepest point: centroid shifted toward NW (smaller i = west, smaller j = north)
DEEP_I = cx - 0.15 * ext_i
DEEP_J = cy - 0.15 * ext_j
print(f"  Centroid  (i, j) = ({cx:.2f}, {cy:.2f})")
print(f"  Deepest   (i, j) = ({DEEP_I:.2f}, {DEEP_J:.2f})  (centre -> NW)")

# normalised distance from deepest point for every wet cell
dist = np.sqrt(((wet_i - DEEP_I) / ext_i) ** 2 + ((wet_j - DEEP_J) / ext_j) ** 2)
d_max = dist.max()
d_norm = dist / d_max           # 0 at deepest point, 1 at farthest wet cell


def avg_depth_for_p(p):
    """depth = MAX_DEPTH * (1 - d_norm**p); return mean depth over wet cells."""
    return float(np.mean(MAX_DEPTH * (1.0 - d_norm ** p)))


# bisection on p so that the *unclamped* mean equals AVG_DEPTH.
# depth = MAX_DEPTH * (1 - d_norm**p);  larger p -> d_norm**p smaller -> deeper.
# So if avg < target we need LARGER p.
lo, hi = 0.3, 4.0
for _ in range(60):
    mid = 0.5 * (lo + hi)
    if avg_depth_for_p(mid) < AVG_DEPTH:
        lo = mid          # avg too small  -> increase p (deeper centre)
    else:
        hi = mid          # avg too large  -> decrease p
p_opt = 0.5 * (lo + hi)
print(f"  Profile exponent p = {p_opt:.4f}  (gives raw mean = {avg_depth_for_p(p_opt):.4f} m)")

# raw bathymetry
bathy_raw = np.full((NY, NX), np.nan)
for k in range(len(wet_i)):
    i, j = int(wet_i[k]), int(wet_j[k])
    bathy_raw[j, i] = MAX_DEPTH * (1.0 - d_norm[k] ** p_opt)

# add gentle realistic micro-relief (deterministic, ~3% of local depth)
rng = np.random.default_rng(7)
relief = rng.normal(0.0, 1.0, (NY, NX))
# smooth the relief a little so it is not pixel-noise (3x3 box average over wet cells)
def box_smooth(arr, wet):
    out = arr.copy()
    for j in range(arr.shape[0]):
        for i in range(arr.shape[1]):
            if not wet[j, i]:
                continue
            s, n = 0.0, 0
            for dj in (-1, 0, 1):
                for di in (-1, 0, 1):
                    jj, ii = j + dj, i + di
                    if 0 <= jj < arr.shape[0] and 0 <= ii < arr.shape[1] and wet[jj, ii]:
                        s += arr[jj, ii]
                        n += 1
            out[j, i] = s / n if n else arr[j, i]
    return out

relief_s = box_smooth(relief, mask)
relief_s = (relief_s - relief_s[mask].mean()) / relief_s[mask].std()
bathy = bathy_raw + 0.03 * bathy_raw * relief_s

# clamp to physical range and re-scale so the mean is exactly AVG_DEPTH
bathy = np.clip(bathy, MIN_DEPTH, MAX_DEPTH)
# final tiny linear rescale to hit AVG_DEPTH exactly (keeps max at MAX_DEPTH)
cur_avg = np.nanmean(bathy)
# adjust by adding a constant offset, then re-clamp max to MAX_DEPTH
offset = AVG_DEPTH - cur_avg
bathy = bathy + offset
bathy = np.clip(bathy, MIN_DEPTH, MAX_DEPTH)
# set the deepest cell exactly to MAX_DEPTH for fidelity
dj_deep = int(round(DEEP_J))
di_deep = int(round(DEEP_I))
if mask[dj_deep, di_deep]:
    bathy[dj_deep, di_deep] = MAX_DEPTH

avg_final = float(np.nanmean(bathy))
max_final = float(np.nanmax(bathy))
min_final = float(np.nanmin(bathy))
lake_volume = float(np.nansum(bathy) * DX * DY)
print(f"  Bathymetry: avg={avg_final:.3f} m  max={max_final:.3f} m  min={min_final:.3f} m")
print(f"  Volume: {lake_volume:.0f} m³ = {lake_volume/1e6:.3f} Mm³")


# ==================================================================
# 4.  Write bathymetry.nc  (GETM cartesian format)
# ==================================================================
print("\nWriting bathymetry.nc ...")
bathy_path = os.path.join(CASE_DIR, "bathymetry.nc")
ds = nc.Dataset(bathy_path, "w", format="NETCDF4")
ds.createDimension("x", NX)
ds.createDimension("y", NY)
ds.createDimension("xq", NX + 1)
ds.createDimension("yq", NY + 1)

grid_type_var = ds.createVariable("grid_type", "i4")
grid_type_var[:] = 1                       # 1 = cartesian

x0, y0 = 500000.0, 3800000.0              # arbitrary UTM-like origin
x_var = ds.createVariable("x", "f8", ("x",))
x_var.units = "m"; x_var.long_name = "x coordinate of cell centres"
x_var[:] = x0 + np.arange(NX) * DX + DX / 2.0
y_var = ds.createVariable("y", "f8", ("y",))
y_var.units = "m"; y_var.long_name = "y coordinate of cell centres"
y_var[:] = y0 + np.arange(NY) * DY + DY / 2.0

lat0, lon0 = 34.15, 118.20                # near Luomahu
lat_var = ds.createVariable("latc", "f8", ("y", "x"))
lat_var.units = "degrees_north"; lat_var.long_name = "latitude of cell centres"
for j in range(NY):
    lat_var[j, :] = lat0 + (NY / 2.0 - j) * (DY / 111000.0)
lon_var = ds.createVariable("lonc", "f8", ("y", "x"))
lon_var.units = "degrees_east"; lon_var.long_name = "longitude of cell centres"
for i in range(NX):
    lon_var[:, i] = lon0 + (i - NX / 2.0) * (DX / (111000.0 * math.cos(math.radians(lat0))))

# bathymetry: dry cells stored as 0.0 (GETM convention: <=0 means land)
bathy_out = np.where(mask, bathy, 0.0)
bath_var = ds.createVariable("bathymetry", "f8", ("y", "x"))
bath_var.units = "m"
bath_var.long_name = "water depth"
bath_var.standard_name = "sea_floor_depth"
bath_var.coordinates = "lonc latc"
bath_var[:] = bathy_out

ds.title = "Theoretical Lake Bathymetry (heart-shaped, 70 km²)"
ds.source = "Generated by gen_theoretical_lake.py"
ds.history = f"Created {datetime.now()}"
ds.Conventions = "CF-1.0"
ds.close()
print("  Done.")


# ==================================================================
# 5.  riverinfo.dat + rivers.nc  (with strict water balance)
# ==================================================================
print("\nWriting riverinfo.dat and rivers.nc ...")
riverinfo_path = os.path.join(CASE_DIR, "riverinfo.dat")
with open(riverinfo_path, "w") as f:
    f.write(f"{total_river_cells}\n")
    for name, _, _, _ in RIVER_SPECS:
        for (i, j) in rivers[name]:
            f.write(f"{i+1} {j+1} {name} -1 -1\n")    # 1-indexed for GETM
print(f"  riverinfo.dat: {total_river_cells} river cells, 5 rivers")

# --- synthetic but realistic meteorology (Luomahu-like climate) -----------
# annual precip ~900 mm, evap ~1000 mm; sinusoidal seasonal cycle
precip_mmd = np.array([2.46 + 1.6 * math.sin(2 * math.pi * (d - 120) / 365.0) for d in range(N_DAYS)])
precip_mmd = np.clip(precip_mmd, 0.0, None)
evap_mmd = np.array([2.74 + 1.9 * math.sin(2 * math.pi * (d - 150) / 365.0) for d in range(N_DAYS)])
evap_mmd = np.clip(evap_mmd, 0.0, None)
t2 = np.array([10.0 + 12.0 * math.sin(2 * math.pi * (d - 80) / 365.0) for d in range(N_DAYS)])
rh = np.array([72.0 + 8.0 * math.sin(2 * math.pi * d / 365.0) for d in range(N_DAYS)])
slp = np.full(N_DAYS, 101300.0)
tcc = np.full(N_DAYS, 0.5)
u10 = np.array([3.0 * math.sin(2 * math.pi * d / 365.0) + 0.5 * math.sin(2 * math.pi * d / 30.0) for d in range(N_DAYS)])
v10 = np.array([2.0 * math.cos(2 * math.pi * d / 365.0) + 0.4 * math.cos(2 * math.pi * d / 21.0) for d in range(N_DAYS)])

precip = precip_mmd / 1000.0 / 86400.0     # m/s
evap = -evap_mmd / 1000.0 / 86400.0        # m/s (negative = loss)

# --- river discharges (seasonal) + strict water balance ------------------
# Inflow design (m³/s, annual-mean):
#   INFL_NW : 4.0   (main inflow, 1.2 km wide)
#   INFL_NE : 1.5
#   INFL_W  : 1.5
# Total mean inflow = 7.0 m³/s = 221 Mm³/yr
SEASONAL_AMP = 0.5
BASE_IN = {"INFL_NW": 4.0, "INFL_NE": 1.5, "INFL_W": 1.5}

discharge = {name: np.zeros(N_DAYS) for name in rivers}
for day in range(N_DAYS):
    seasonal = 1.0 + SEASONAL_AMP * math.sin(2 * math.pi * (day - 120) / 365.0)
    for name in BASE_IN:
        discharge[name][day] = BASE_IN[name] * seasonal

# Outflow = Inflow + (Precip - Evap) * Area   (steady-state water balance)
for day in range(N_DAYS):
    inflow_total = sum(discharge[n][day] for n in BASE_IN)
    p_m3s = max(0.0, precip[day]) * LAKE_AREA
    e_m3s = max(0.0, -evap[day]) * LAKE_AREA
    outflow_pos = inflow_total + p_m3s - e_m3s
    # split outflow between OUTFL_S and OUTFL_E proportional to width (1 : 2)
    total = 3.0
    discharge["OUTFL_S"][day] = -outflow_pos * (1.0 / total)
    discharge["OUTFL_E"][day] = -outflow_pos * (2.0 / total)

# water-quality concentrations for inflow rivers (outflow uses dummy values)
RIVER_WQ = {
    "INFL_NW": {"temp": 12.0, "nh4": 0.15, "no3": 1.2, "po4": 0.025},
    "INFL_NE": {"temp": 12.0, "nh4": 0.12, "no3": 1.0, "po4": 0.022},
    "INFL_W":  {"temp": 12.0, "nh4": 0.10, "no3": 0.8, "po4": 0.020},
    "OUTFL_S": {"temp": 12.0, "nh4": 0.05, "no3": 1.0, "po4": 0.020},
    "OUTFL_E": {"temp": 12.0, "nh4": 0.05, "no3": 1.0, "po4": 0.020},
}

# --- write rivers.nc -----------------------------------------------------
rivers_path = os.path.join(CASE_DIR, "rivers.nc")
ds_riv = nc.Dataset(rivers_path, "w", format="NETCDF4")
ds_riv.createDimension("time", None)
tvar = ds_riv.createVariable("time", "f8", ("time",))
tvar.units = "seconds since 2020-01-01 00:00:00"
tvar.long_name = "time"
tvar[:] = np.arange(N_DAYS) * 86400.0

for name in rivers:
    v = ds_riv.createVariable(name, "f8", ("time",))
    v.units = "m3/s"
    v.long_name = f"{name} river discharge"
    v[:] = discharge[name]
    wq = RIVER_WQ[name]
    for wn, u, ln in [("temp", "degC", f"{name} temperature"),
                      ("nh4", "g/m3", f"{name} ammonium"),
                      ("no3", "g/m3", f"{name} nitrate"),
                      ("po4", "g/m3", f"{name} phosphate")]:
        if wn == "temp":
            vals = np.array([wq["temp"] + 10.0 * math.sin(2 * math.pi * (d - 80) / 365.0) for d in range(N_DAYS)])
        else:
            vals = np.full(N_DAYS, wq[wn])
        vv = ds_riv.createVariable(f"{name}_{wn}", "f8", ("time",))
        vv.units = u; vv.long_name = ln
        vv[:] = vals
ds_riv.title = "Theoretical Lake river data"
ds_riv.close()
print("  rivers.nc written.")

# water-balance report
in_vol = sum(discharge[n].sum() for n in BASE_IN) * 86400.0
out_vol = sum(-discharge[n].sum() for n in ["OUTFL_S", "OUTFL_E"]) * 86400.0
p_vol = precip.sum() * LAKE_AREA * 86400.0
e_vol = (-evap).sum() * LAKE_AREA * 86400.0
print(f"  Water balance (m³/yr):")
print(f"    inflow  = {in_vol/1e6:8.2f} Mm³")
print(f"    precip  = {p_vol/1e6:8.2f} Mm³")
print(f"    outflow = {out_vol/1e6:8.2f} Mm³")
print(f"    evap    = {e_vol/1e6:8.2f} Mm³")
print(f"    residual= {(in_vol+p_vol-out_vol-e_vol):.1f} m³")


# ==================================================================
# 6.  meteo.nc  (GETM on-grid format)
# ==================================================================
print("\nWriting meteo.nc ...")
meteo_path = os.path.join(CASE_DIR, "meteo.nc")
bathy_ds = nc.Dataset(bathy_path)
lonc = bathy_ds.variables["lonc"][:]
latc = bathy_ds.variables["latc"][:]
bathy_ds.close()
lon_1d = lonc[0, :]
lat_1d = latc[:, 0]

ds = nc.Dataset(meteo_path, "w", format="NETCDF4")
ds.createDimension("lon", NX)
ds.createDimension("lat", NY)
ds.createDimension("time", N_DAYS)
lv = ds.createVariable("lon", "f8", ("lon",)); lv.units = "degrees_east"; lv[:] = lon_1d
av = ds.createVariable("lat", "f8", ("lat",)); av.units = "degrees_north"; av[:] = lat_1d
tv = ds.createVariable("time", "f8", ("time",)); tv.units = "seconds since 2020-01-01 00:00:00"; tv[:] = np.arange(N_DAYS) * 86400.0

meteo_fields = [
    ("u10", "m s-1", "10m wind u-component", u10, "f4"),
    ("v10", "m s-1", "10m wind v-component", v10, "f4"),
    ("slp", "Pa", "sea level pressure", slp, "f4"),
    ("t2", "degC", "2m air temperature", t2, "f4"),
    ("rh", "1", "relative humidity", rh, "f4"),
    ("tcc", "1", "total cloud cover", tcc, "f4"),
    ("precip", "m s-1", "precipitation rate", precip, "f8"),
    ("evap", "m s-1", "evaporation rate (negative = loss)", evap, "f8"),
]
for vn, u, ln, data, dt in meteo_fields:
    v = ds.createVariable(vn, dt, ("time", "lat", "lon"))
    v.units = u; v.long_name = ln
    v[:] = np.broadcast_to(data[:, np.newaxis, np.newaxis], (N_DAYS, NY, NX))
ds.title = "Theoretical Lake meteorology (synthetic, Luomahu-like climate)"
ds.close()
print("  Done.")


# ==================================================================
# 7.  Configuration files (getm.inp, getm_fabm.inp, etc.)
# ==================================================================
print("\nWriting configuration files ...")

# copy fabm.yaml, gotmturb.nml, gotm_fabm.yaml, output.yaml from Luomahu
for fname in ["fabm.yaml", "gotmturb.nml", "gotm_fabm.yaml", "output.yaml"]:
    src = os.path.join(LUOMAHU_CASE, fname)
    dst = os.path.join(CASE_DIR, fname)
    if os.path.exists(src):
        with open(src, "r", encoding="utf-8") as f:
            content = f.read()
        with open(dst, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  {fname}: copied from Luomahu")
    else:
        print(f"  {fname}: Luomahu source not found - skipped")

# meteo_input.txt
with open(os.path.join(CASE_DIR, "meteo_input.txt"), "w") as f:
    f.write("meteo.nc\n")
print("  meteo_input.txt: written")

# getm.inp
getm_inp = f"""! Theoretical Lake (heart-shaped) - GETM-FABM-WET configuration
! Grid: {NX} x {NY} cells, 500 m x 500 m, 70 km², avg 5.3 m, max 10.2 m

&param
    dryrun       = .false.
    runid        = 'THEORETICAL_LAKE'
    title        = 'Theoretical Lake (heart) GETM-FABM-WET'
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
    maxdepth = {MAX_DEPTH + 1.0:.1f}
    bathy_format = 2
    bathymetry   = 'bathymetry.nc'
    f_plane      = .true.
    il = 1
    ih = {NX}
    jl = 1
    jh = {NY}
    crit_depth = 0.3
    min_depth = 0.1
    kdum         = {N_SIGMA}
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
    MM = {NX * NY}
    vel2d_adv_split = 1
    vel2d_adv_hor   = 1
    Am          = 1.0
    An_method   = 0
    An_const    = 0.001
/

&m3d
    M = {N_SIGMA}
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
with open(os.path.join(CASE_DIR, "getm.inp"), "w", encoding="utf-8") as f:
    f.write(getm_inp)
print("  getm.inp: written")

# getm_fabm.inp
getm_fabm_inp = """&getm_fabm_nml
 fabm_init_method   =  2,
 fabm_init_file     =  'fabm_init.nc',
 fabm_init_format   =  2,
 fabm_field_no      =  1,
 fabm_adv_hor       =  4,
 fabm_adv_ver       =  4,
 fabm_adv_split     =  1,
 fabm_AH            = -1.,
/
"""
with open(os.path.join(CASE_DIR, "getm_fabm.inp"), "w", encoding="utf-8") as f:
    f.write(getm_fabm_inp)
print("  getm_fabm.inp: written")


# ==================================================================
# 8.  fabm_init.nc  (minimal initial conditions on the new grid)
# ==================================================================
print("\nWriting fabm_init.nc ...")
luomahu_init = os.path.join(LUOMAHU_CASE, "fabm_init.nc")
if os.path.exists(luomahu_init):
    src_ds = nc.Dataset(luomahu_init)
    fabm_init_path = os.path.join(CASE_DIR, "fabm_init.nc")
    ds = nc.Dataset(fabm_init_path, "w", format="NETCDF4")
    for dname, dvar in src_ds.dimensions.items():
        if dname in ("lon", "xc"):
            ds.createDimension(dname, NX)
        elif dname in ("lat", "yc"):
            ds.createDimension(dname, NY)
        elif dname == "time":
            ds.createDimension(dname, 1)
        else:
            ds.createDimension(dname, len(dvar) if not dvar.isunlimited() else None)
    for vname, vvar in src_ds.variables.items():
        dims = vvar.dimensions
        new_var = ds.createVariable(vname, vvar.dtype, tuple(dims))
        new_var.setncatts({k: vvar.getncattr(k) for k in vvar.ncattrs()})
        vdata = vvar[:]
        if len(dims) == 2 and any(d in ("lon", "xc") for d in dims) and any(d in ("lat", "yc") for d in dims):
            if vname in ("lonc", "lon", "xc"):
                new_var[:] = lonc
            elif vname in ("latc", "lat", "yc"):
                new_var[:] = latc
            else:
                fill = float(np.nanmean(vdata)) if vdata.size else 0.0
                new_var[:] = np.full((NY, NX), fill)
        elif len(dims) == 1:
            if vname in ("lon", "xc"):
                new_var[:] = lon_1d
            elif vname in ("lat", "yc"):
                new_var[:] = lat_1d
            elif vname == "time":
                new_var[:] = [0.0]
            else:
                new_var[:] = vdata[:]
        else:
            new_var[:] = vdata[:]
    src_ds.close()
    ds.close()
    print("  fabm_init.nc: generated from Luomahu template")
else:
    # build a minimal fabm_init.nc with coordinates only
    fabm_init_path = os.path.join(CASE_DIR, "fabm_init.nc")
    ds = nc.Dataset(fabm_init_path, "w", format="NETCDF4")
    ds.createDimension("lon", NX)
    ds.createDimension("lat", NY)
    ds.createDimension("time", 1)
    lv = ds.createVariable("lon", "f8", ("lon",)); lv[:] = lon_1d
    av = ds.createVariable("lat", "f8", ("lat",)); av[:] = lat_1d
    tv = ds.createVariable("time", "f8", ("time",)); tv[:] = [0.0]
    lvc = ds.createVariable("lonc", "f8", ("lat", "lon")); lvc[:] = lonc
    lac = ds.createVariable("latc", "f8", ("lat", "lon")); lac[:] = latc
    ds.close()
    print("  fabm_init.nc: minimal (Luomahu template not found)")


# ==================================================================
# 9.  Human-readable summary + ASCII mask map
# ==================================================================
summary_path = os.path.join(CASE_DIR, "lake_summary.txt")
with open(summary_path, "w", encoding="utf-8") as f:
    f.write("Theoretical Lake - design summary\n")
    f.write("=" * 50 + "\n\n")
    f.write(f"Shape              : heart (point south), irregular shoreline\n")
    f.write(f"Grid               : {NX} x {NY} cells, {DX:.0f} m x {DY:.0f} m\n")
    f.write(f"Wet cells          : {n_wet}\n")
    f.write(f"Surface area       : {lake_area_km2:.2f} km²\n")
    f.write(f"Average depth      : {avg_final:.2f} m\n")
    f.write(f"Maximum depth      : {max_final:.2f} m\n")
    f.write(f"Minimum depth      : {min_final:.2f} m\n")
    f.write(f"Volume             : {lake_volume/1e6:.2f} Mm³\n")
    f.write(f"Sigma layers       : {N_SIGMA}\n")
    f.write(f"Deepest point (i,j): ({di_deep+1}, {dj_deep+1})  [centre -> NW]\n")
    f.write(f"Centroid    (i,j)  : ({cx+1:.1f}, {cy+1:.1f})\n\n")
    f.write("Rivers:\n")
    for name, rtype, ncells, _ in RIVER_SPECS:
        cells = rivers[name]
        cells_str = ", ".join(f"({i+1},{j+1})" for (i, j) in cells)
        width = ncells * DX / 1000.0
        mean_q = float(np.mean(discharge[name]))
        f.write(f"  {name:8s} {rtype:7s}  width~{width:.1f}km  cells={cells_str}  meanQ={mean_q:.2f} m³/s\n")
    f.write(f"\nTotal river cells  : {total_river_cells}\n")
    f.write(f"Simulation period  : 2020-01-01 to 2020-12-31 ({N_DAYS} days)\n")

# ASCII map of the lake mask with rivers marked
mask_path = os.path.join(CASE_DIR, "lake_mask.txt")
river_cell_map = {}
for name, _, _, _ in RIVER_SPECS:
    for (i, j) in rivers[name]:
        river_cell_map[(i, j)] = name

sym = {"INFL_NW": "1", "INFL_NE": "2", "INFL_W": "3", "OUTFL_S": "4", "OUTFL_E": "5"}
with open(mask_path, "w", encoding="utf-8") as f:
    f.write("Lake mask (j=1 north/top -> j=NY south/point; i=1 west -> i=NX east)\n")
    f.write("  # = water,  . = land,  1-5 = river mouths (see legend)\n")
    f.write("  Legend: 1=INFL_NW 2=INFL_NE 3=INFL_W 4=OUTFL_S 5=OUTFL_E\n\n")
    f.write("    " + "".join(f"{(i%10)}" for i in range(NX)) + "\n")
    for j in range(NY):
        row = f"{j+1:3d} "
        for i in range(NX):
            if (i, j) in river_cell_map:
                row += sym[river_cell_map[(i, j)]]
            elif mask[j, i]:
                row += "#"
            else:
                row += "."
        f.write(row + "\n")

print(f"\n  lake_summary.txt and lake_mask.txt written.")

print("\n" + "=" * 72)
print("All input files generated successfully!")
print("=" * 72)
print(f"\nFiles in {CASE_DIR}:")
for fn in sorted(os.listdir(CASE_DIR)):
    fp = os.path.join(CASE_DIR, fn)
    if os.path.isfile(fp):
        print(f"  {fn:20s}  {os.path.getsize(fp):>10d} bytes")
