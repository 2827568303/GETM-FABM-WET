"""Deeper diagnosis - check coordinate system and river positions."""
import netCDF4 as nc
import numpy as np
import os

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")

bathy_ds = nc.Dataset(os.path.join(CASE_DIR, "bathymetry.nc"))
x = bathy_ds.variables['x'][:]
y = bathy_ds.variables['y'][:]
lonc = bathy_ds.variables['lonc'][:]
latc = bathy_ds.variables['latc'][:]
bathymetry = bathy_ds.variables['bathymetry'][:]

print("=" * 70)
print("CRITICAL: Coordinate system check")
print("=" * 70)

# y range: 3762500 - 3789000, span 26500m
# latc range: 33.9989 - 34.0029, span 0.004 deg ≈ 444m
# This is WRONG - should be ~0.24 deg for 26.5km
print(f"y range: {y.min():.1f} - {y.max():.1f}, span = {y.max()-y.min():.1f} m")
print(f"latc range: {latc.min():.6f} - {latc.max():.6f}, span = {latc.max()-latc.min():.6f} deg")
print(f"Expected lat span for {y.max()-y.min():.0f}m: {(y.max()-y.min())/111000:.4f} deg")
print(f"  -> latc span is WRONG by factor ~{((y.max()-y.min())/111000)/(latc.max()-latc.min()):.0f}x")

print()
print("=" * 70)
print("Check if x/y are UTM coordinates")
print("=" * 70)
# UTM zone 50N for 骆马湖 area
# Central meridian 117E, false easting 500000
print(f"x range: {x.min():.1f} - {x.max():.1f}")
print(f"  -> UTM easting (zone 50N central=500000, this looks correct for 118E)")
print(f"y range: {y.min():.1f} - {y.max():.1f}")
print(f"  -> UTM northing (34N ≈ 3763000m, this is correct)")

print()
print("=" * 70)
print("Convert UTM to lat/lon manually for verification")
print("=" * 70)
# Simple UTM to lat/lon conversion (approximate)
# UTM zone 50N, WGS84
import math

def utm_to_latlon(easting, northing, zone=50, northern=True):
    """Approximate UTM to lat/lon conversion (WGS84)."""
    # WGS84 parameters
    a = 6378137.0
    f = 1/298.257223563
    k0 = 0.9996
    e = math.sqrt(2*f - f*f)
    e2 = e*e
    e_prime2 = e2/(1-e2)

    x = easting - 500000.0
    y = northing
    if not northern:
        y -= 10000000.0

    M = y / k0
    mu = M / (a * (1 - e2/4 - 3*e2**2/64 - 5*e2**3/256))

    e1 = (1 - math.sqrt(1 - e2)) / (1 + math.sqrt(1 - e2))
    phi1 = mu + (3*e1/2 - 27*e1**3/32) * math.sin(2*mu)
    phi1 = phi1 + (21*e1**2/16 - 55*e1**4/32) * math.sin(4*mu)
    phi1 = phi1 + (151*e1**3/96) * math.sin(6*mu)

    N1 = a / math.sqrt(1 - e2 * math.sin(phi1)**2)
    T1 = math.tan(phi1)**2
    C1 = e_prime2 * math.cos(phi1)**2
    R1 = a * (1 - e2) / (1 - e2 * math.sin(phi1)**2)**1.5
    D = x / (N1 * k0)

    lat = phi1 - (N1 * math.tan(phi1) / R1) * (D**2/2
         - (5 + 3*T1 + 10*C1 - 4*C1**2 - 9*e_prime2) * D**4/24
         + (61 + 90*T1 + 298*C1 + 45*T1**2 - 252*e_prime2 - 3*C1**2) * D**6/720)

    lon = (D - (1 + 2*T1 + C1) * D**3/6
          + (5 - 2*C1 + 28*T1 - 3*C1**2 + 8*e_prime2 + 24*T1**2) * D**5/120) / math.cos(phi1)
    lon = lon * 180/math.pi
    lon += zone * 6 - 183  # Central meridian for zone

    lat = lat * 180/math.pi
    return lat, lon

# Test: convert corners of grid
print("Corner conversions (UTM zone 50N):")
for xi, yi in [(0,0), (43,0), (0,53), (43,53), (21,50), (28,2), (7,32), (42,27), (35,28)]:
    easting = x[xi] if xi < len(x) else x[-1]
    northing = y[yi] if yi < len(y) else y[-1]
    lat, lon = utm_to_latlon(easting, northing)
    print(f"  grid({xi},{yi}): E={easting:.0f}, N={northing:.0f} -> lat={lat:.6f}, lon={lon:.6f}")

print()
print("=" * 70)
print("River position verification")
print("=" * 70)
# Known approximate lat/lon for Luomahu rivers (from references):
# 骆马湖 is approximately at 34.0-34.4N, 118.0-118.5E
# YIHE (沂河) enters from north: ~34.3N, 118.2E
# LUONAN (骆南) - south end
# DAYUN (京杭大运河) - east side
# ZHANGSHAN (嶂山) - northeast
# YANGHE (洋河) - southeast

rivers_info = [
    ('YIHE', 21, 50, '沂河 - 入湖 from north'),
    ('LUONAN', 28, 2, '骆南 - south'),
    ('DAYUN', 7, 32, '京杭大运河 - east'),
    ('ZHANGSHAN', 42, 27, '嶂山 - northeast'),
    ('YANGHE', 35, 28, '洋河 - southeast'),
]
for name, i, j, desc in rivers_info:
    i0, j0 = i-1, j-1
    easting = x[i0]
    northing = y[j0]
    lat, lon = utm_to_latlon(easting, northing)
    bathy_val = bathymetry[j0, i0]
    print(f"  {name} ({desc}):")
    print(f"    grid (i={i}, j={j}), E={easting:.0f}, N={northing:.0f}")
    print(f"    -> lat={lat:.4f}, lon={lon:.4f}")
    print(f"    -> bathymetry={bathy_val:.2f}m")
    print(f"    -> stored lonc={lonc[j0,i0]:.4f}, latc={latc[j0,i0]:.4f}")

bathy_ds.close()
