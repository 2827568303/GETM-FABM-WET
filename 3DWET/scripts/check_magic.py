"""Check NetCDF file magic number and calculate numrecs from file size."""
import struct
import os
import netCDF4 as nc

CASE = '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case'

for fname in ['LUOMAHU_WET.2d.nc', 'LUOMAHU_WET.3d.nc', 'output.nc']:
    path = os.path.join(CASE, fname)
    if not os.path.exists(path):
        continue
    with open(path, 'rb') as fh:
        magic = fh.read(4)
        nr = struct.unpack('>I', fh.read(4))[0]
    fsize = os.path.getsize(path)
    print(f'{fname}: magic={magic!r} numrecs={nr} filesize={fsize}')
    print(f'  is CDF1 (Classic): {magic == b"CDF\x01"}')
    print(f'  is CDF2 (64-bit):  {magic == b"CDF\x02"}')

    # Get record variable info from ncdump-equivalent
    try:
        with nc.Dataset(path, 'r') as ds:
            unlim_dims = [d for d in ds.dimensions if ds.dimensions[d].unlimited]
            print(f'  unlimited dim: {unlim_dims}')
            print(f'  dims: {dict((d, len(ds.dimensions[d])) for d in ds.dimensions)}')
            rec_vars = []
            for vname, v in ds.variables.items():
                if v.dimensions and v.dimensions[0] in unlim_dims:
                    # Calculate per-record size
                    rec_shape = v.shape[1:]  # exclude time dim
                    type_size = v.dtype.itemsize
                    var_rec_size = type_size
                    for s in rec_shape:
                        var_rec_size *= s
                    rec_vars.append((vname, var_rec_size, v.dtype, v.shape))
            print(f'  record vars: {[(v[0], v[1]) for v in rec_vars]}')
            total_rec_size = sum(v[1] for v in rec_vars)
            print(f'  total record_size: {total_rec_size}')
    except Exception as e:
        print(f'  netCDF4 error: {e}')
    print()
