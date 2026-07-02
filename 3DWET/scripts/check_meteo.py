"""Check meteo.nc variable names and structure."""
import netCDF4 as nc
import os

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")
ds = nc.Dataset(os.path.join(CASE_DIR, "meteo.nc"))
print("Variables:", list(ds.variables.keys()))
print("Dimensions:", {k: len(v) for k, v in ds.dimensions.items()})
for v in ds.variables:
    var = ds.variables[v]
    print(f"  {v}: dims={var.dimensions}, shape={var.shape}, units={getattr(var, 'units', 'N/A')}")
ds.close()
