import netCDF4
import numpy as np

nc = netCDF4.Dataset('rivers.nc')
print("Variables:", list(nc.variables.keys()))
print("Dimensions:", dict((k, len(v)) for k, v in nc.dimensions.items()))

for v in nc.variables:
    var = nc.variables[v]
    data = var[:]
    print(f"\n{v}:")
    print(f"  dims={var.dimensions}, shape={var.shape}")
    if data.size > 0:
        if np.issubdtype(data.dtype, np.number):
            print(f"  min={np.nanmin(data)}, max={np.nanmax(data)}")
            if data.ndim <= 2:
                print(f"  values={data}")
        else:
            print(f"  values={data}")

nc.close()
