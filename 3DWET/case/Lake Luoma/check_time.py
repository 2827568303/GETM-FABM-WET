import netCDF4

for f in ['LUOMAHU_WET.2d.nc', 'LUOMAHU_WET.3d.nc', 'output.nc']:
    nc = netCDF4.Dataset(f)
    time_var = nc.variables['time']
    print(f"{f}: time length={len(time_var)}, units={getattr(time_var, 'units', 'N/A')}")
    if len(time_var) > 0:
        print(f"  first={time_var[0]}, last={time_var[-1]}")
    # Check a data variable
    for v in nc.variables:
        var = nc.variables[v]
        if 'time' in var.dimensions and len(var.shape) > 1:
            import numpy as np
            data = var[:]
            print(f"  {v}: shape={data.shape}, finite={np.isfinite(data).sum()}/{data.size}")
            if data.size > 0 and np.isfinite(data).any():
                print(f"    min={np.nanmin(data)}, max={np.nanmax(data)}")
            break
    nc.close()
