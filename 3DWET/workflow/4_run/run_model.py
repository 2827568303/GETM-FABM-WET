"""3DWET 模型运行模块 - 验证输入并执行模型

Usage:
    python run_model.py <case_dir> [--threads <n>] [--no-validate]

Features:
    1. Pre-run validation of all input files
    2. OpenMP multi-threading support
    3. Automatic Patankar warning filtering
    4. Exit code checking
    5. Automatic numrecs patching (NetCDF3 bug fix)
    6. Output file verification
"""
import os
import sys
import struct
import subprocess
import argparse
import time
import re
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKFLOW_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(WORKFLOW_DIR)
sys.path.insert(0, os.path.join(WORKFLOW_DIR, '4_run'))

from validate_inputs import validate_case

sys.path.insert(0, os.path.join(PROJECT_ROOT, 'app'))
from run_output_health import validate_current_run_outputs

# Default model executable
MODEL_EXE = os.path.join(PROJECT_ROOT, 'install', 'bin', 'getm_cartesian')


def _patch_numrecs(filepath, num_recs):
    """Patch NetCDF3 numrecs field at file offset 4 (big-endian uint32).

    GETM exits on meteo EOF without flushing the NetCDF3 header, leaving
    numrecs=0. This patch writes the correct record count so readers can
    access the data.
    """
    with open(filepath, 'r+b') as f:
        f.seek(4)
        f.write(struct.pack('>I', num_recs))


def _parse_getm_inp(case_dir):
    """Extract run parameters from getm.inp. Returns dict or None."""
    getm_inp = os.path.join(case_dir, 'getm.inp')
    if not os.path.exists(getm_inp):
        return None

    params = {}
    with open(getm_inp, 'r') as f:
        for line in f:
            line = line.split('#')[0].strip()
            if '=' not in line:
                continue
            key, _, val = line.partition('=')
            key = key.strip().lower()
            val = val.strip().strip("'").strip()
            if key in ('runid', 'timestep', 'start', 'stop', 'step_2d', 'step_3d', 'sync_2d', 'sync_3d'):
                params[key] = val
    return params


def _auto_patch_numrecs(case_dir, run_id):
    """Restore only physically complete records in classic NetCDF files.

    The simulation dates do not prove that output records were written. The
    count is derived from each file's record-variable layout and byte length.
    Unsupported or malformed headers are left untouched and reported.
    """
    patched = []
    for filename in (f'{run_id}.2d.nc', f'{run_id}.3d.nc', 'output.nc'):
        path = os.path.join(case_dir, filename)
        if not os.path.exists(path):
            continue
        try:
            n_recs = _physical_numrecs(path)
            if n_recs is None:
                print(f"  WARNING: Skipped numrecs patch for {filename}: unsupported or indeterminate NetCDF layout; header unchanged")
                continue
            with open(path, 'rb') as f:
                f.seek(4)
                old_recs = struct.unpack('>I', f.read(4))[0]
            if old_recs != n_recs:
                _patch_numrecs(path, n_recs)
                patched.append(f"{filename}({old_recs}->{n_recs} complete records)")
        except (OSError, ValueError, struct.error) as e:
            print(f"  WARNING: Skipped numrecs patch for {filename}: {e}; header unchanged")

    if patched:
        print(f"  Patched numrecs: {', '.join(patched)}")


def _physical_numrecs(filepath):
    """Return complete physical record count for a CDF-1/2 file, or None.

    Only classic NetCDF layouts are recognized. The last record variable's
    unpadded data size is used so a legal unpadded final record is retained;
    any trailing partial record is excluded.
    """
    def read_u32(f):
        raw = f.read(4)
        if len(raw) != 4:
            raise ValueError('truncated NetCDF header')
        return struct.unpack('>I', raw)[0]

    def read_name(f):
        length = read_u32(f)
        raw = f.read(length)
        if len(raw) != length:
            raise ValueError('truncated NetCDF name')
        f.seek((-length) % 4, 1)
        return raw.decode('utf-8', errors='strict')

    type_sizes = {1: 1, 2: 1, 3: 2, 4: 4, 5: 4, 6: 8}
    with open(filepath, 'rb') as f:
        magic = f.read(4)
        if magic not in (b'CDF\x01', b'CDF\x02'):
            return None
        begin_size = 8 if magic == b'CDF\x02' else 4
        read_u32(f)  # Header numrecs may be stale or zero.

        tag, count = read_u32(f), read_u32(f)
        dims = []
        if (tag, count) != (0, 0):
            if tag != 10:
                raise ValueError('invalid dimension list')
            for _ in range(count):
                read_name(f)
                dims.append(read_u32(f))
        unlimited = next((i for i, size in enumerate(dims) if size == 0), None)

        def skip_attributes():
            tag, count = read_u32(f), read_u32(f)
            if (tag, count) == (0, 0):
                return
            if tag != 12:
                raise ValueError('invalid attribute list')
            for _ in range(count):
                read_name(f)
                xtype, n = read_u32(f), read_u32(f)
                if xtype not in type_sizes:
                    raise ValueError('unsupported attribute type')
                size = type_sizes[xtype] * n
                f.seek(size + (-size) % 4, 1)

        skip_attributes()
        tag, count = read_u32(f), read_u32(f)
        if (tag, count) == (0, 0):
            return None
        if tag != 11:
            raise ValueError('invalid variable list')
        records = []
        for _ in range(count):
            read_name(f)
            ndims = read_u32(f)
            dimids = [read_u32(f) for _ in range(ndims)]
            skip_attributes()
            xtype = read_u32(f)
            vsize = read_u32(f)
            begin = struct.unpack('>Q' if begin_size == 8 else '>I', f.read(begin_size))[0]
            if len(dimids) and dimids[0] == unlimited:
                if xtype not in type_sizes or any(d >= len(dims) for d in dimids):
                    raise ValueError('unsupported record variable')
                elements = 1
                for dimid in dimids[1:]:
                    elements *= dims[dimid]
                raw_size = elements * type_sizes[xtype]
                if raw_size > vsize or vsize == 0:
                    raise ValueError('invalid record variable size')
                records.append((begin, vsize, raw_size))

        if not records:
            return None
        records.sort(key=lambda item: item[0])
        start = records[0][0]
        for previous, current in zip(records, records[1:]):
            if current[0] != previous[0] + previous[1]:
                raise ValueError('record variables are not contiguous')
        stride = sum(item[1] for item in records)
        final_size = sum(item[1] for item in records[:-1]) + records[-1][2]
        if stride <= 0 or final_size <= 0:
            raise ValueError('invalid record size')
        file_size = os.path.getsize(filepath)
        first_end = start + final_size
        if file_size < first_end:
            return 0
        return 1 + (file_size - first_end) // stride


def _eof_completion_status(case_dir, run_id, started_at):
    """Require stop-time coverage and healthy current outputs for meteo EOF."""
    params = _parse_getm_inp(case_dir) or {}
    try:
        stop = datetime.strptime(params['stop'], '%Y-%m-%d %H:%M:%S')
    except (KeyError, ValueError) as exc:
        return False, f'cannot determine configured stop time: {exc}'

    try:
        import netCDF4
        output_names = [f'{run_id}.2d.nc', f'{run_id}.3d.nc', 'output.nc']
        found = []
        for filename in output_names:
            path = os.path.join(case_dir, filename)
            if not os.path.isfile(path):
                continue
            physical = _physical_numrecs(path)
            if physical is None or physical <= 0:
                return False, f'{filename} has no verifiable complete physical records'
            with netCDF4.Dataset(path, 'r') as ds:
                time_name = next((name for name in ds.variables if name.lower() == 'time'), None)
                if time_name is None:
                    return False, f'{filename} has no time coordinate'
                time_var = ds.variables[time_name]
                if 'units' not in time_var.ncattrs():
                    return False, f'{filename} time coordinate has no units'
                time_axis = time_var.dimensions.index(time_name) if time_name in time_var.dimensions else 0
                if time_var.shape[time_axis] != physical:
                    return False, f'{filename} time coordinate does not match complete physical records'
                last_value = time_var[tuple(slice(None) if axis != time_axis else physical - 1
                                            for axis in range(time_var.ndim))]
                last_value = netCDF4.num2date(last_value, time_var.units,
                    getattr(time_var, 'calendar', 'standard'), only_use_cftime_datetimes=False)
                if hasattr(last_value, 'item'):
                    last_value = last_value.item()
                last_time = datetime.fromisoformat(str(last_value).replace(' ', 'T'))
                if last_time < stop:
                    return False, f'{filename} ends at {last_time}, before configured stop {stop}'
                found.append(filename)
        if not found:
            return False, 'no output files with verifiable time records were produced'

        health = validate_current_run_outputs(case_dir, netCDF4.Dataset, started_at=started_at)
        if not health.get('ready'):
            errors = health.get('errors', []) + [item.get('reason', '') for item in health.get('bad_variables', [])]
            return False, 'output health check failed: ' + '; '.join(errors[:4])
        return True, f'outputs cover {stop} and pass health checks'
    except Exception as exc:
        return False, f'could not verify output completion: {exc}'


def run_model(case_dir, threads=8, no_validate=False, filter_warnings=True):
    """Run the 3DWET model for a given case directory."""
    case_dir = os.path.abspath(case_dir)

    print("=" * 70)
    print("3DWET Model Run Module")
    print(f"Case directory: {case_dir}")
    print(f"Model executable: {MODEL_EXE}")
    print(f"Threads: {threads}")
    print("=" * 70)

    # Check model executable exists
    if not os.path.exists(MODEL_EXE):
        print(f"\nERROR: Model executable not found: {MODEL_EXE}")
        print("Please build the model first: bash scripts/build_model.sh")
        return False

    # Validate inputs
    if not no_validate:
        success, messages = validate_case(case_dir)
        if not success:
            print(f"\nValidation failed with {len(messages)} issues.")
            print("Fix the issues or use --no-validate to skip validation.")
            return False
    else:
        print("\nSkipping validation (--no-validate)")

    # Prepare run command
    env = os.environ.copy()
    env['OMP_NUM_THREADS'] = str(threads)
    env['OMP_SCHEDULE'] = 'dynamic'

    print(f"\nStarting model run ...")
    print(f"  Log file: {os.path.join(case_dir, 'run.log')}")
    print(f"  Warning filter: {'ON (small pi/Warning filtered)' if filter_warnings else 'OFF'}")
    print()

    start_time = time.time()

    # Filter output in Python so the reported status always comes from GETM,
    # never from the last command in a shell pipeline.
    log_path = os.path.join(case_dir, 'run.log')
    filter_pattern = re.compile(r'small pi|Warning:', re.IGNORECASE)
    with open(log_path, 'w', encoding='utf-8', errors='replace') as log:
        process = subprocess.Popen(
            [MODEL_EXE], cwd=case_dir, env=env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding='utf-8', errors='replace',
        )
        for line in process.stdout:
            if not filter_warnings or not filter_pattern.search(line):
                log.write(line)
                log.flush()
        exit_code = process.wait()
        log.write(f'EXIT_CODE:{exit_code}\n')

    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)

    with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    run_id = None
    getm_inp = os.path.join(case_dir, 'getm.inp')
    if os.path.exists(getm_inp):
        with open(getm_inp, 'r') as f:
            for line in f:
                if 'runid' in line.lower() and '=' in line:
                    run_id = line.split('=')[1].strip().strip("'").strip()
                    break
    if run_id:
        print(f"\n  Patching NetCDF3 numrecs from complete physical records ...")
        _auto_patch_numrecs(case_dir, run_id)

    eof_match = re.search(r'FATAL\s+ERROR\s*:\s*Reached\s+eof\s+in\s*:\s*meteo_input\.txt',
                          content, re.IGNORECASE)
    other_log = content
    if eof_match:
        other_log = content[:eof_match.start()] + content[eof_match.end():]
    fatal_match = re.search(
        r'\bFATAL(?:\s+ERROR)?\b|FATAL\s+GETM\s+ERROR|Reached\s+eof\s+in\s*:|'
        r'out-of-bound values encountered|IEEE_INVALID(?:_FLAG)?|'
        r'IEEE_DIVIDE_BY_ZERO(?:_FLAG)?|Floating invalid|forrtl:|'
        r'^\s*STOP\s+[1-9]\d*\b|'
        r'^\s*Error:\s*state variable\s+\d+\s+is zero and has negative derivative!|'
        r'\bNaN\s+(?:detected|found|at|in)\b|\b(?:is|contains)\s+NaN\b',
        other_log, re.IGNORECASE | re.MULTILINE)
    eof_valid = False
    eof_reason = ''
    if eof_match and exit_code == 0 and not fatal_match:
        eof_valid, eof_reason = _eof_completion_status(case_dir, run_id, start_time)
        if not eof_valid:
            print(f"  Meteo EOF completion rejected: {eof_reason}")
    fatal_detected = fatal_match is not None or (eof_match is not None and not eof_valid)

    # Summary
    print("\n" + "=" * 70)
    print("Model Run Summary")
    print("=" * 70)
    print(f"  Elapsed time: {minutes}m {seconds}s")
    print(f"  Exit code: {exit_code}")

    if exit_code == 0 and not fatal_detected:
        print(f"  Status: SUCCESS")
        if eof_valid:
            print(f"  Completion: {eof_reason}")
    else:
        reason = (f"fatal log signature: {fatal_match.group(0)}" if fatal_match else
                  f"incomplete meteo EOF: {eof_reason}" if eof_match else f"exit code {exit_code}")
        print(f"  Status: FAILED ({reason})")
        print(f"  Check run.log for details")

    # Check output files
    print(f"\n  Output files:")
    if run_id:
        for suffix in ['.2d.nc', '.3d.nc']:
            path = os.path.join(case_dir, f'{run_id}{suffix}')
            if os.path.exists(path):
                size = os.path.getsize(path)
                print(f"    {run_id}{suffix}: {size/1024/1024:.1f} MB")

    output_nc = os.path.join(case_dir, 'output.nc')
    if os.path.exists(output_nc):
        size = os.path.getsize(output_nc)
        print(f"    output.nc: {size/1024/1024:.1f} MB")

    print(f"\n  Log file: {log_path}")

    if exit_code == 0 and not fatal_detected:
        print(f"\nNext step:")
        print(f"  python workflow/5_postprocess/extract_timeseries.py {case_dir}")
    else:
        print(f"\nTroubleshooting:")
        print(f"  1. Check run.log for error messages")
        print(f"  2. Common issues:")
        print(f"     - meteo EOF is accepted only when output reaches stop time and passes health checks")
        print(f"     - NaN in output (check initial conditions)")

    return exit_code == 0 and not fatal_detected


def main():
    parser = argparse.ArgumentParser(description='3DWET Model Run Module')
    parser.add_argument('case_dir', help='Path to case directory')
    parser.add_argument('--threads', '-t', type=int, default=8,
                        help='Number of OpenMP threads (default: 8)')
    parser.add_argument('--no-validate', action='store_true',
                        help='Skip input validation')
    parser.add_argument('--no-filter', action='store_true',
                        help='Do not filter Patankar warnings (log will be huge)')
    args = parser.parse_args()

    success = run_model(
        args.case_dir,
        threads=args.threads,
        no_validate=args.no_validate,
        filter_warnings=not args.no_filter,
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
