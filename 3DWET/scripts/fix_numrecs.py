"""Parse NetCDF3 Classic header and patch numrecs from file size.

Used when model is killed (no graceful shutdown) and numrecs=0 in header
but data was actually written.
"""
import struct
import os
import netCDF4 as nc
import numpy as np

TYPE_SIZES = {1: 1, 2: 1, 3: 2, 4: 4, 5: 4, 6: 8}


def _read_padded_name(f):
    name_len = struct.unpack('>I', f.read(4))[0]
    name = f.read(name_len).decode('ascii', errors='replace')
    pad = (4 - name_len % 4) % 4
    f.read(pad)
    return name


def _read_attrs(f):
    natts = struct.unpack('>I', f.read(4))[0]
    for _ in range(natts):
        _read_padded_name(f)
        att_type = struct.unpack('>I', f.read(4))[0]
        nelems = struct.unpack('>I', f.read(4))[0]
        val_size = nelems * TYPE_SIZES.get(att_type, 1)
        f.read(val_size)
        pad = (4 - val_size % 4) % 4
        f.read(pad)


def parse_nc3_header(path):
    """Return dict with numrecs, dims, header_size, record_size, vars."""
    with open(path, 'rb') as f:
        magic = f.read(4)
        if magic != b'CDF\x01':
            raise ValueError(f'Not NetCDF3 Classic: {magic!r}')
        numrecs = struct.unpack('>I', f.read(4))[0]

        # dim_list
        dims = []
        tag = struct.unpack('>I', f.read(4))[0]
        if tag == 0x0000000A:
            ndims = struct.unpack('>I', f.read(4))[0]
            for _ in range(ndims):
                name = _read_padded_name(f)
                dim_size = struct.unpack('>I', f.read(4))[0]
                dims.append((name, dim_size))

        # gatt_list
        tag = struct.unpack('>I', f.read(4))[0]
        if tag == 0x0000000C:
            _read_attrs(f)

        # var_list
        vars_info = []
        tag = struct.unpack('>I', f.read(4))[0]
        if tag == 0x0000000B:
            nvars = struct.unpack('>I', f.read(4))[0]
            for _ in range(nvars):
                name = _read_padded_name(f)
                ndims = struct.unpack('>I', f.read(4))[0]
                dim_ids = [struct.unpack('>I', f.read(4))[0] for _ in range(ndims)]
                vtype = struct.unpack('>I', f.read(4))[0]
                vsize = struct.unpack('>I', f.read(4))[0]
                _read_attrs(f)
                offset = struct.unpack('>I', f.read(4))[0]
                vars_info.append({'name': name, 'dim_ids': dim_ids,
                                  'vsize': vsize, 'offset': offset})

        header_size = f.tell()

    unlim_dim_idx = None
    for i, (name, size) in enumerate(dims):
        if size == 0:
            unlim_dim_idx = i
            break

    record_size = 0
    if unlim_dim_idx is not None:
        for v in vars_info:
            if v['dim_ids'] and v['dim_ids'][0] == unlim_dim_idx:
                record_size += v['vsize']

    return {
        'numrecs': numrecs,
        'dims': dims,
        'header_size': header_size,
        'record_size': record_size,
        'vars': vars_info,
        'unlim_dim_idx': unlim_dim_idx,
    }


CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")

for fname in ['LUOMAHU_WET.2d.nc', 'LUOMAHU_WET.3d.nc', 'output.nc']:
    path = os.path.join(CASE_DIR, fname)
    if not os.path.exists(path):
        continue
    print(f'\n=== {fname} ===')
    info = parse_nc3_header(path)
    filesize = os.path.getsize(path)
    print(f'  current numrecs: {info["numrecs"]}')
    print(f'  header_size: {info["header_size"]}')
    print(f'  record_size: {info["record_size"]}')

    if info['record_size'] <= 0:
        print('  no record variables, skipping')
        continue

    calc_numrecs = (filesize - info['header_size']) // info['record_size']
    remainder = (filesize - info['header_size']) % info['record_size']
    print(f'  filesize: {filesize}')
    print(f'  calculated numrecs: {calc_numrecs} (remainder={remainder})')

    if info['numrecs'] == 0 and calc_numrecs > 0:
        with open(path, 'r+b') as f:
            f.seek(4)
            f.write(struct.pack('>I', calc_numrecs))
        print(f'  PATCHED: 0 -> {calc_numrecs}')

    # Verify
    with nc.Dataset(path, 'r') as ds:
        t = ds.variables.get('time')
        if t is not None:
            tdata = t[:]
            print(f'  verify: time dim len={len(tdata)}')
            if len(tdata) > 0:
                print(f'  time first={tdata[0]}, last={tdata[-1]}')
                for vname in ['elev', 'temp', 'uu']:
                    if vname in ds.variables:
                        v = ds.variables[vname]
                        try:
                            d_last = v[-1]
                            if d_last.ndim == 2:
                                print(f'  {vname} last: min={np.nanmin(d_last):.4f}, '
                                      f'max={np.nanmax(d_last):.4f}')
                            elif d_last.ndim == 3:
                                print(f'  {vname} last surf: min={np.nanmin(d_last[-1]):.4f}, '
                                      f'max={np.nanmax(d_last[-1]):.4f}')
                        except Exception as e:
                            print(f'  {vname} read error: {e}')
                        break
