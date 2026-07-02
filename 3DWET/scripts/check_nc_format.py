"""Check NetCDF format versions of all input files."""
import netCDF4 as nc
import os

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")

files = ["bathymetry.nc", "rivers.nc", "meteo.nc"]
for fname in files:
    path = os.path.join(CASE_DIR, fname)
    if not os.path.exists(path):
        print(f"{fname}: NOT FOUND")
        continue
    ds = nc.Dataset(path, "r")
    print(f"\n{fname}:")
    print(f"  data_model: {ds.data_model}")
    print(f"  disk_format: {ds.disk_format}")
    print(f"  file_format: {ds.file_format}")
    print(f"  dimensions:")
    for name, dim in ds.dimensions.items():
        print(f"    {name}: size={len(dim)}, unlimited={dim.isunlimited()}")
    ds.close()
