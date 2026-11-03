import netCDF4
import numpy as np

nc = netCDF4.Dataset('output.nc')
print(f"time length: {len(nc.dimensions['time'])}")

# Check key variables
key_vars = ['temp', 'abiotic_water_sPO4W', 'abiotic_water_sNH4W', 'abiotic_water_sNO3W',
            'diatoms_sDW', 'greens_sDW', 'cyanobacteria_sDW', 'macrophytes_sD',
            'abiotic_water_sO2W']

for v in key_vars:
    if v in nc.variables:
        var = nc.variables[v]
        if len(var.shape) >= 1 and var.shape[0] > 0:
            data = var[:]
            finite = np.isfinite(data).sum()
            total = data.size
            if finite > 0:
                print(f"{v}: shape={data.shape}, finite={finite}/{total}, min={np.nanmin(data):.4f}, max={np.nanmax(data):.4f}")
            else:
                print(f"{v}: shape={data.shape}, NO FINITE VALUES")
        else:
            print(f"{v}: shape={var.shape}, no time records yet")
    else:
        print(f"{v}: NOT FOUND in output")

nc.close()
