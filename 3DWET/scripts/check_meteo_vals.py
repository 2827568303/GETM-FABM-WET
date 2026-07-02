import netCDF4 as nc
import numpy as np
ds=nc.Dataset('/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/meteo.nc')
for v in ['u10','v10','slp','t2','rh','tcc','precip']:
    d=ds.variables[v][:]
    print(f'{v}: shape={d.shape}, min={np.nanmin(d):.4f}, max={np.nanmax(d):.4f}, mean={np.nanmean(d):.4f}')
ds.close()
