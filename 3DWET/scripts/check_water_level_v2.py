"""Check water level from a copy of 2d.nc (to avoid interfering with running model).

Copies 2d.nc to /tmp, patches numrecs, reads elev, reports water level trend.
"""
import os
import shutil
import struct
import subprocess
import re
import sys
import numpy as np
import netCDF4 as nc

CASE = '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case'
SRC = os.path.join(CASE, 'LUOMAHU_WET.2d.nc')
TMP = '/tmp/2d_check.nc'

TYPE_MAP = {
    'char': 1, 'byte': 1, 'short': 2, 'int': 4,
    'float': 4, 'double': 8,
}


def get_record_size(path):
    result = subprocess.run(['ncdump', '-h', path], capture_output=True, text=True)
    output = result.stdout
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
    unlim_dim = None
    for name, size in dims.items():
        if size == 0:
            unlim_dim = name
            break
    if not unlim_dim:
        return 0, dims, unlim_dim, []
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
                type_size = TYPE_MAP.get(vtype, 4)
                rec_size = type_size
                for dn in dim_names[1:]:
                    rec_size *= dims.get(dn, 1)
                record_size += rec_size
                rec_vars.append((vname, rec_size))
    return record_size, dims, unlim_dim, rec_vars


def patch_numrecs(path, numrecs):
    with open(path, 'r+b') as f:
        f.seek(4)
        f.write(struct.pack('>I', numrecs))


def main():
    if not os.path.exists(SRC):
        print(f"Source not found: {SRC}")
        sys.exit(1)

    shutil.copy2(SRC, TMP)
    print(f"Copied {SRC} -> {TMP}")

    record_size, dims, unlim_dim, rec_vars = get_record_size(TMP)
    filesize = os.path.getsize(TMP)
    print(f"record_size: {record_size}, filesize: {filesize}")
    print(f"record variables: {rec_vars}")

    if record_size <= 0:
        print("ERROR: could not calculate record_size")
        sys.exit(1)

    max_possible = filesize // record_size
    print(f"max possible numrecs: {max_possible}")

    found = False
    for n in range(max_possible, -1, -1):
        header_size = filesize - n * record_size
        if header_size < 0 or header_size > 200000:
            continue
        patch_numrecs(TMP, n)
        try:
            with nc.Dataset(TMP, 'r') as ds:
                t = ds.variables.get('time')
                if t is None or len(t) != n:
                    continue
                if n > 0:
                    tvals = t[:]
                    if not np.all(np.diff(tvals) > 0):
                        continue
                    if 'elev' in ds.variables:
                        elev = ds.variables['elev']
                        d = np.ma.filled(elev[0], np.nan)
                        if np.all(np.isnan(d)):
                            continue
                        valid = d[~np.isnan(d)]
                        if len(valid) == 0 or np.all(np.abs(valid - (-9999.0)) < 0.1):
                            continue
                    print(f"SUCCESS: numrecs={n}, header_size={header_size}")
                    found = True
                    break
        except Exception:
            continue

    if not found:
        print("FAILED: could not find valid numrecs")
        sys.exit(1)

    with nc.Dataset(TMP, 'r') as ds:
        t = ds.variables['time'][:]
        elev = ds.variables['elev'][:]
        print(f"\nRecords: {len(t)}")
        print("Water level (elev) statistics:")
        for i in range(min(len(t), 20)):
            e = elev[i]
            mean_e = np.nanmean(e)
            print(f"  t={t[i]/86400:.2f}d: mean={mean_e:+.4f}m")
        if len(t) >= 2:
            delta = np.nanmean(elev[-1]) - np.nanmean(elev[0])
            days = (t[-1] - t[0]) / 86400.0
            rate = delta / days if days > 0 else 0
            print(f"\nDelta: {delta:+.4f}m over {days:.2f}d ({rate*1000:+.3f} mm/day)")
            print(f"Expected: fwf mean ~0.322 mm/day (from Excel precip-evap balance)")

    os.remove(TMP)
    print("\nCleaned up temp file.")


if __name__ == '__main__':
    main()
