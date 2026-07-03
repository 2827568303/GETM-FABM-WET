"""Input validation for 3DWET case directory.

Checks all required files exist and are valid before running the model.
"""
import os
import sys
import struct
import netCDF4 as nc
import numpy as np


REQUIRED_FILES = [
    'getm.inp',
    'getm_fabm.inp',
    'fabm.yaml',
    'gotm_fabm.yaml',
    'gotmturb.nml',
    'output.yaml',
    'bathymetry.nc',
    'meteo.nc',
    'rivers.nc',
    'fabm_init.nc',
    'riverinfo.dat',
    'meteo_input.txt',
]


def validate_case(case_dir):
    """Validate all inputs in a case directory. Returns (success, messages)."""
    messages = []
    success = True

    print("=" * 70)
    print(f"Validating case: {case_dir}")
    print("=" * 70)

    # Check 1: All required files exist
    print("\n[1/5] Checking required files ...")
    for fname in REQUIRED_FILES:
        path = os.path.join(case_dir, fname)
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"  OK  {fname:25s} ({size/1024:.1f} KB)")
        else:
            print(f"  FAIL {fname:25s} - MISSING")
            messages.append(f"Missing: {fname}")
            success = False

    if not success:
        return False, messages

    # Check 2: bathymetry.nc
    print("\n[2/5] Checking bathymetry.nc ...")
    try:
        ds = nc.Dataset(os.path.join(case_dir, 'bathymetry.nc'), 'r')
        bathy = ds.variables['bathymetry'][:]
        latc = ds.variables['latc'][:]
        lonc = ds.variables['lonc'][:]
        water_cells = np.sum(bathy > 0)
        total_cells = bathy.size
        if water_cells == 0:
            print(f"  FAIL: No water cells (all bathymetry <= 0)")
            messages.append("bathymetry: no water cells")
            success = False
        else:
            avg_depth = np.mean(bathy[bathy > 0])
            max_depth = np.max(bathy[bathy > 0])
            print(f"  OK  Water cells: {water_cells}/{total_cells} ({water_cells/total_cells*100:.1f}%)")
            print(f"  OK  Avg depth: {avg_depth:.2f}m, Max depth: {max_depth:.2f}m")
        ds.close()
    except Exception as e:
        print(f"  FAIL: {e}")
        messages.append(f"bathymetry.nc: {e}")
        success = False

    # Check 3: meteo.nc
    print("\n[3/5] Checking meteo.nc ...")
    try:
        ds = nc.Dataset(os.path.join(case_dir, 'meteo.nc'), 'r')
        n_time = len(ds.variables['time'][:])
        required_vars = ['t2', 'u10', 'v10', 'slp', 'rh', 'tcc', 'precip', 'evap']
        for v in required_vars:
            if v not in ds.variables:
                print(f"  FAIL: Missing variable {v}")
                messages.append(f"meteo.nc: missing {v}")
                success = False
        # Check precip is float64
        precip_dtype = ds.variables['precip'].dtype
        if precip_dtype != np.float64:
            print(f"  WARNING: precip is {precip_dtype}, should be float64!")
            messages.append("meteo.nc: precip not float64")
        else:
            print(f"  OK  precip is float64")
        print(f"  OK  Time records: {n_time}")
        ds.close()
    except Exception as e:
        print(f"  FAIL: {e}")
        messages.append(f"meteo.nc: {e}")
        success = False

    # Check 4: riverinfo.dat and rivers.nc
    print("\n[4/5] Checking rivers ...")
    try:
        with open(os.path.join(case_dir, 'riverinfo.dat'), 'r') as f:
            n_rivers = int(f.readline().strip())
            river_names = []
            for line in f:
                parts = line.split()
                if len(parts) >= 3:
                    river_names.append(parts[2])
        print(f"  OK  {n_rivers} rivers: {river_names}")

        ds = nc.Dataset(os.path.join(case_dir, 'rivers.nc'), 'r')
        for name in river_names:
            if name not in ds.variables:
                print(f"  FAIL: River {name} not in rivers.nc")
                messages.append(f"rivers.nc: missing {name}")
                success = False
        ds.close()
    except Exception as e:
        print(f"  FAIL: {e}")
        messages.append(f"rivers: {e}")
        success = False

    # Check 5: Configuration files
    print("\n[5/5] Checking configuration files ...")
    try:
        # gotm_fabm.yaml
        import yaml
        with open(os.path.join(case_dir, 'gotm_fabm.yaml'), 'r') as f:
            gf = yaml.safe_load(f)
        if not gf.get('fabm', {}).get('use', False):
            print(f"  FAIL: gotm_fabm.yaml: fabm.use is not true")
            messages.append("gotm_fabm.yaml: fabm not enabled")
            success = False
        else:
            print(f"  OK  gotm_fabm.yaml: fabm.use=true")

        # Check fabm.yaml exists and has content
        with open(os.path.join(case_dir, 'fabm.yaml'), 'r') as f:
            fy = yaml.safe_load(f)
        n_instances = len(fy.get('instances', {}))
        print(f"  OK  fabm.yaml: {n_instances} instances")

        # Check getm.inp for critical params
        with open(os.path.join(case_dir, 'getm.inp'), 'r') as f:
            getm_content = f.read()
        if 'timestep     = 30.0' not in getm_content:
            print(f"  WARNING: timestep is not 30.0s (may cause instability)")
            messages.append("getm.inp: timestep not 30s")
        else:
            print(f"  OK  getm.inp: timestep=30s")
    except Exception as e:
        print(f"  FAIL: {e}")
        messages.append(f"config: {e}")
        success = False

    # Summary
    print("\n" + "=" * 70)
    if success:
        print("VALIDATION PASSED - Ready to run!")
    else:
        print("VALIDATION FAILED - Fix the issues above before running!")
    print("=" * 70)

    if messages:
        print("\nIssues:")
        for m in messages:
            print(f"  - {m}")

    return success, messages
