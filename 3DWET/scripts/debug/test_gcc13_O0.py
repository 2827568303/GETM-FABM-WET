#!/usr/bin/env python3
"""Test if GCC 13 with -O0 can bypass the internal compiler error."""
import subprocess
import os
import sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(WORK_DIR, "run_logs")

def run_wsl(cmd, log_file=None):
    """Run command via WSL bash."""
    print(f"  Running: {cmd[:120]}...")
    result = subprocess.run(
        ["wsl", "-e", "bash", "-c", cmd],
        capture_output=True,
        text=True
    )
    if log_file:
        with open(log_file, 'w') as f:
            f.write("=== STDOUT ===\n")
            f.write(result.stdout)
            f.write("\n=== STDERR ===\n")
            f.write(result.stderr)
    if result.returncode != 0:
        print(f"  FAILED! Return code: {result.returncode}")
        print(f"  STDERR tail:\n{result.stderr[-2000:]}")
        return False
    print(f"  OK")
    return True

def main():
    os.makedirs(LOG_DIR, exist_ok=True)
    
    setup_dir = "/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake"
    build_dir = "/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_O0"
    install_dir = "/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/install_gcc13_O0"
    
    print("Testing GCC 13 with -O0 optimization...")
    
    # Clean
    run_wsl(f"rm -rf {build_dir} && mkdir -p {build_dir}/fabm {build_dir}/getm {install_dir}")
    
    # Build FABM first
    print("\n[1] Building FABM with GCC 13 -O0...")
    ok = run_wsl(
        f"cd {build_dir}/fabm && "
        f"export CC=gcc && export CXX=g++ && export FC=gfortran && "
        f"cmake {setup_dir}/fabm/src "
        f"-DCMAKE_INSTALL_PREFIX={install_dir}/fabm "
        f"-DFABM_HOST=gotm "
        f"-DCMAKE_BUILD_TYPE=Debug "
        f"-DCMAKE_Fortran_FLAGS_DEBUG='-O0 -g'",
        os.path.join(LOG_DIR, "fabm_cmake_gcc13_O0.log")
    )
    if not ok:
        print("  FABM CMake failed!")
        return 1
    print("  FABM CMake OK")
    
    ok = run_wsl(
        f"cd {build_dir}/fabm && make -j$(nproc)",
        os.path.join(LOG_DIR, "fabm_build_gcc13_O0.log")
    )
    if not ok:
        print("  FABM build failed!")
        return 1
    print("  FABM build OK")
    
    run_wsl(f"cd {build_dir}/fabm && make install")
    
    # Now try to compile the problematic file: gotm_fabm.F90
    print("\n[2] Testing gotm_fabm.F90 compilation with -O0...")
    
    # Configure GETM
    ok = run_wsl(
        f"cd {build_dir}/getm && "
        f"export CC=gcc && export CXX=g++ && export FC=gfortran && "
        f"cmake {setup_dir}/getm/src "
        f"-DCMAKE_INSTALL_PREFIX={install_dir} "
        f"-DGOTM_BASE={setup_dir}/gotm "
        f"-DFABM_PREFIX={install_dir}/fabm "
        f"-DGETM_USE_FABM=ON "
        f"-DGETM_USE_CARTESIAN=ON "
        f"-DCMAKE_BUILD_TYPE=Debug "
        f"-DCMAKE_Fortran_FLAGS_DEBUG='-O0 -g'",
        os.path.join(LOG_DIR, "getm_cmake_gcc13_O0.log")
    )
    if not ok:
        print("  GETM CMake failed!")
        return 1
    print("  GETM CMake OK")
    
    # Try to build just gotm_fabm
    ok = run_wsl(
        f"cd {build_dir}/getm && make gotm_fabm -j1",
        os.path.join(LOG_DIR, "gotm_fabm_build_gcc13_O0.log")
    )
    if not ok:
        print("  gotm_fabm build FAILED with -O0!")
        return 1
    
    print("  gotm_fabm build OK with -O0!")
    
    # Now try full build
    print("\n[3] Full GETM build with -O0...")
    ok = run_wsl(
        f"cd {build_dir}/getm && make -j$(nproc)",
        os.path.join(LOG_DIR, "getm_build_gcc13_O0.log")
    )
    if not ok:
        print("  GETM full build failed!")
        return 1
    
    print("  GETM full build OK!")
    
    run_wsl(f"cd {build_dir}/getm && make install")
    
    print("\n" + "="*60)
    print("SUCCESS: GCC 13 with -O0 works!")
    print("="*60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
