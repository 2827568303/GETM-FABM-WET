"""Compare bathymetry.nc structure between Luomahu and Theoretical Lake."""
import netCDF4 as nc
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def describe(path, label):
    print(f"=== {label}: {path} ===")
    ds = nc.Dataset(path)
    print(f"Dimensions: {dict((k, len(v)) for k, v in ds.dimensions.items())}")
    print(f"Global attrs: {dict(ds.__dict__)}")
    print("Variables:")
    for name, var in ds.variables.items():
        print(f"  {name}: dims={var.dimensions}, dtype={var.dtype}")
        for a in var.ncattrs():
            print(f"    {a} = {getattr(var, a)}")
    print()
    ds.close()

luomahu = os.path.join(PROJECT_ROOT, "3DWET", "case", "Lake Luoma", "bathymetry.nc")
theo = os.path.join(PROJECT_ROOT, "Theoretical lake", "case", "bathymetry.nc")

if os.path.exists(luomahu):
    describe(luomahu, "Luomahu")
else:
    print(f"Luomahu bathymetry not found: {luomahu}")

if os.path.exists(theo):
    describe(theo, "Theoretical Lake")
else:
    print(f"Theoretical Lake bathymetry not found: {theo}")
