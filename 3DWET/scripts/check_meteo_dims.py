"""Check meteo.nc variable dimensions and shapes."""
import netCDF4 as nc
import numpy as np
import os

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")
meteo_path = os.path.join(CASE_DIR, "meteo.nc")

ds = nc.Dataset(meteo_path, "r")
print("=" * 60)
print(f"File: {meteo_path}")
print("=" * 60)

print("\nDimensions:")
for name, dim in ds.dimensions.items():
    print(f"  {name}: size={len(dim)}, unlimited={dim.isunlimited()}")

print("\nVariables:")
for name, var in ds.variables.items():
    print(f"  {name}:")
    print(f"    dimensions: {var.dimensions}")
    print(f"    shape: {var.shape}")
    print(f"    dtype: {var.dtype}")
    if hasattr(var, "units"):
        print(f"    units: {var.units}")

print("\nCoordinate values:")
if "lon" in ds.variables:
    print(f"  lon: {ds.variables['lon'][:5]} ... (len={len(ds.variables['lon'])})")
if "lat" in ds.variables:
    print(f"  lat: {ds.variables['lat'][:5]} ... (len={len(ds.variables['lat'])})")
if "time" in ds.variables:
    t = ds.variables['time'][:]
    print(f"  time: first={t[0]}, last={t[-1]}, len={len(t)}")
    if hasattr(ds.variables['time'], "units"):
        print(f"  time units: {ds.variables['time'].units}")

print("\nSample data check (u10 at time=0):")
if "u10" in ds.variables:
    u10 = ds.variables["u10"]
    print(f"  u10 shape: {u10.shape}")
    print(f"  u10[:, :, 0] min/max: {u10[:, :, 0].min():.4f} / {u10[:, :, 0].max():.4f}")

ds.close()
