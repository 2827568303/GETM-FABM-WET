import netCDF4
import numpy as np
import os

os.chdir(r'c:\Users\dinod\Desktop\GETM-FABM-WET\test_case')

print("=== topo.nc ===")
nc = netCDF4.Dataset('topo.nc', 'r')
print("Variables:", list(nc.variables.keys()))
print("Dimensions:", dict(nc.dimensions))

for var in nc.variables:
    data = nc[var][:]
    print(f"\n{var}: shape={data.shape}")
    if data.ndim == 2:
        print(data)

nc.close()

print("\n=== riverinfo.dat ===")
with open('riverinfo.dat', 'r') as f:
    print(f.read())

print("\n=== getm_fabm.inp ===")
with open('getm_fabm.inp', 'r') as f:
    print(f.read())