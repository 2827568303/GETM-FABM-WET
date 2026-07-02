"""Calculate and patch numrecs from file size and ncdump -h output.

Strategy:
1. Run ncdump -h to get all record variables (those with 'time' as first dim)
2. Calculate record_size = sum of per-record sizes
3. Binary search for numrecs: patch header, try reading, verify data validity
"""
import os
import struct
import subprocess
import re
import netCDF4 as nc
import numpy as np

CASE = '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case'

# NetCDF3 type sizes (bytes)
TYPE_MAP = {
    'char': 1, 'byte': 1, 'short': 2, 'int': 4,
    'float': 4, 'double': 8, 'ubyte': 1, 'ushort': 2, 'uint': 4, 'int64': 8, 'uint64': 8,
}

def get_record_size_from_ncdump(path):
    """Parse ncdump -h output to calculate record_size."""
    result = subprocess.run(['ncdump', '-h', path], capture_output=True, text=True)
    output = result.stdout

    # Parse dimensions
    dims = {}
    in_dims = False
    for line in output.split('\n'):
        line = line.strip()
        if line.startswith('dimensions:'):
            in_dims = True
            continue
        if line.startswith('variables:'):
            in_dims = False
            continue
        if in_dims and '=' in line:
            m = re.match(r'(\w+)\s*=\s*(\w+)', line)
            if m:
                name, val = m.groups()
                dims[name] = 0 if val == 'UNLIMITED' else int(val)

    # Find unlimited dim
    unlim_dim = None
    for name, size in dims.items():
        if size == 0:
            unlim_dim = name
            break

    if not unlim_dim:
        return 0, dims, unlim_dim

    # Parse variables and find record variables
    record_size = 0
    rec_vars = []
    var_pattern = re.compile(
        r'^\s*(int|float|double|char|byte|short|ubyte|ushort|uint|int64|uint64)\s+(\w+)\(([^)]+)\)'
    )
    for line in output.split('\n'):
        m = var_pattern.match(line)
        if m:
            vtype, vname, dim_list = m.groups()
            dim_names = [d.strip() for d in dim_list.split(',')]
            if dim_names[0] == unlim_dim:
                # Record variable: calculate per-record size
                type_size = TYPE_MAP.get(vtype, 4)
                rec_size = type_size
                for dn in dim_names[1:]:
                    rec_size *= dims.get(dn, 1)
                record_size += rec_size
                rec_vars.append((vname, rec_size))

    return record_size, dims, unlim_dim, rec_vars


def verify_numrecs(path, numrecs):
    """Patch numrecs and verify data reads correctly."""
    # Patch
    with open(path, 'r+b') as f:
        f.seek(4)
        f.write(struct.pack('>I', numrecs))

    # Verify
    try:
        with nc.Dataset(path, 'r') as ds:
            t = ds.variables.get('time')
            if t is None or len(t) != numrecs:
                return False
            if numrecs > 0:
                # Check time values are monotonic
                tvals = t[:]
                if not np.all(np.diff(tvals) > 0):
                    return False
                # Check a data variable
                for vname in ['elev', 'temp', 'uu']:
                    if vname in ds.variables:
                        v = ds.variables[vname]
                        d = v[min(numrecs - 1, 0)]
                        if d.ndim == 2:
                            vals = np.ma.filled(d, np.nan)
                        elif d.ndim == 3:
                            vals = np.ma.filled(d[-1], np.nan)
                        else:
                            continue
                        # Check not all NaN
                        if np.all(np.isnan(vals)):
                            return False
                        # Check reasonable range (not all -9999)
                        valid = vals[~np.isnan(vals)]
                        if len(valid) == 0:
                            return False
                        if np.all(np.abs(valid - (-9999.0)) < 0.1):
                            return False
                        return True
            return True
    except Exception:
        return False


for fname in ['LUOMAHU_WET.2d.nc', 'LUOMAHU_WET.3d.nc', 'output.nc']:
    path = os.path.join(CASE, fname)
    if not os.path.exists(path):
        continue
    print(f'\n=== {fname} ===')

    result = get_record_size_from_ncdump(path)
    record_size, dims, unlim_dim, rec_vars = result
    filesize = os.path.getsize(path)

    print(f'  dims: {dims}')
    print(f'  unlimited dim: {unlim_dim}')
    print(f'  record variables: {len(rec_vars)}')
    print(f'  record_size: {record_size}')
    print(f'  filesize: {filesize}')

    if record_size <= 0:
        print('  ERROR: could not calculate record_size')
        continue

    # Calculate numrecs from file size
    # header_size is unknown, but should be small (< 100KB typically)
    # Try different numrecs values
    max_possible = (filesize - 0) // record_size
    min_possible = (filesize - 200000) // record_size  # assume header < 200KB
    if min_possible < 0:
        min_possible = 0

    print(f'  numrecs range: {min_possible} to {max_possible}')

    # Try from max downward (header should be small)
    found = False
    for n in range(max_possible, min_possible - 1, -1):
        header_size = filesize - n * record_size
        if header_size < 0:
            continue
        # Header should be > 0 and reasonably small
        if header_size > 200000:
            continue
        # Verify
        if verify_numrecs(path, n):
            print(f'  SUCCESS: numrecs={n}, header_size={header_size}')
            found = True
            break

    if not found:
        # Try a broader search
        print('  Trying broader search...')
        for n in range(max_possible, -1, -1):
            header_size = filesize - n * record_size
            if header_size < 0:
                continue
            if verify_numrecs(path, n):
                print(f'  SUCCESS: numrecs={n}, header_size={header_size}')
                found = True
                break

    if not found:
        print('  FAILED: could not find valid numrecs')
        # Reset to 0
        with open(path, 'r+b') as f:
            f.seek(4)
            f.write(struct.pack('>I', 0))

    # Final verification
    with nc.Dataset(path, 'r') as ds:
        t = ds.variables.get('time')
        if t is not None and len(t) > 0:
            tvals = t[:]
            print(f'  Final: time records={len(tvals)}, first={tvals[0]}, last={tvals[-1]}')
