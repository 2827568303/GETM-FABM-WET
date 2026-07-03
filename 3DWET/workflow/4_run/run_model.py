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
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKFLOW_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(WORKFLOW_DIR)
sys.path.insert(0, os.path.join(WORKFLOW_DIR, '4_run'))

from validate_inputs import validate_case

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
    """Automatically patch numrecs in output NetCDF3 files after model run."""
    params = _parse_getm_inp(case_dir)
    if not params:
        print("  WARNING: Could not parse getm.inp for numrecs patching")
        return

    try:
        timestep = float(params.get('timestep', '30'))
        start = datetime.strptime(params['start'], '%Y-%m-%d %H:%M:%S')
        stop = datetime.strptime(params['stop'], '%Y-%m-%d %H:%M:%S')
        total_seconds = (stop - start).total_seconds()
        total_steps = int(total_seconds / timestep)
        step_2d = int(params.get('step_2d', '1440'))
        step_3d = int(params.get('step_3d', '1440'))
        n_2d = total_steps // step_2d
        n_3d = total_steps // step_3d
        n_fabm = int(total_seconds / 86400)  # FABM daily output
    except (KeyError, ValueError) as e:
        print(f"  WARNING: Could not calculate record counts: {e}")
        return

    patched = []
    for filename, n_recs in [
        (f'{run_id}.2d.nc', n_2d),
        (f'{run_id}.3d.nc', n_3d),
        ('output.nc', n_fabm),
    ]:
        path = os.path.join(case_dir, filename)
        if os.path.exists(path) and n_recs > 0:
            _patch_numrecs(path, n_recs)
            patched.append(f"{filename}({n_recs} records)")

    if patched:
        print(f"  Patched numrecs: {', '.join(patched)}")


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

    # Build command with optional warning filter
    if filter_warnings:
        # Filter Patankar "small pi" warnings and state variable errors
        cmd = f'cd "{case_dir}" && "{MODEL_EXE}" 2>&1 | grep -v -E "small pi|Error: state variable|Warning:" > run.log; echo "EXIT_CODE:$?" >> run.log'
    else:
        cmd = f'cd "{case_dir}" && "{MODEL_EXE}" > run.log 2>&1; echo "EXIT_CODE:$?" >> run.log'

    print(f"\nStarting model run ...")
    print(f"  Log file: {os.path.join(case_dir, 'run.log')}")
    print(f"  Warning filter: {'ON (small pi/Warning filtered)' if filter_warnings else 'OFF'}")
    print()

    start_time = time.time()

    # Run model
    result = subprocess.run(
        ['bash', '-c', cmd],
        env=env,
        capture_output=False,
    )

    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)

    # Check exit code from log
    log_path = os.path.join(case_dir, 'run.log')
    exit_code = -1
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            content = f.read()
            if 'EXIT_CODE:' in content:
                line = [l for l in content.split('\n') if 'EXIT_CODE:' in l][-1]
                exit_code = int(line.split('EXIT_CODE:')[1].strip())

    # Summary
    print("\n" + "=" * 70)
    print("Model Run Summary")
    print("=" * 70)
    print(f"  Elapsed time: {minutes}m {seconds}s")
    print(f"  Exit code: {exit_code}")

    if exit_code == 0:
        print(f"  Status: SUCCESS")
    else:
        print(f"  Status: FAILED (exit code {exit_code})")
        print(f"  Check run.log for details")

    # Get run_id from getm.inp
    run_id = None
    getm_inp = os.path.join(case_dir, 'getm.inp')
    if os.path.exists(getm_inp):
        with open(getm_inp, 'r') as f:
            for line in f:
                if 'runid' in line.lower() and '=' in line:
                    run_id = line.split('=')[1].strip().strip("'").strip()
                    break

    # Auto-patch numrecs (NetCDF3 bug: GETM exits on meteo EOF without flushing header)
    if run_id:
        print(f"\n  Patching NetCDF3 numrecs ...")
        _auto_patch_numrecs(case_dir, run_id)

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

    if exit_code == 0:
        print(f"\nNext step:")
        print(f"  python workflow/5_postprocess/extract_timeseries.py {case_dir}")
    else:
        print(f"\nTroubleshooting:")
        print(f"  1. Check run.log for error messages")
        print(f"  2. Common issues:")
        print(f"     - meteo EOF at end of simulation (expected, exit code may still be 0)")
        print(f"     - NaN in output (check initial conditions)")

    return exit_code == 0


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
