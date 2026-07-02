#!/usr/bin/env python3
"""Build GETM-FABM with GCC 9 - use GOTM's yaml for FABM."""
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
    build_dir = "/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc9_v3"
    install_dir = "/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/install_gcc9_v3"
    
    print("=" * 60)
    print("Building GETM-FABM with GCC 9 (using GOTM's yaml for FABM)")
    print("=" * 60)
    
    # Step 0: Check GCC 9
    print("\n[0] Checking GCC 9...")
    result = subprocess.run(["wsl", "gcc-9", "--version"], capture_output=True, text=True)
    print(f"  {result.stdout.split(chr(10))[0]}")
    
    # Step 1: Clean and create dirs
    print("\n[1] Preparing build directories...")
    run_wsl(f"rm -rf {build_dir} && mkdir -p {build_dir}/fabm {build_dir}/getm {install_dir}")
    
    # Step 2: Replace FABM's yaml with GOTM's yaml
    print("\n[2] Replacing FABM yaml with GOTM yaml...")
    fabm_yaml = f"{setup_dir}/fabm/src/yaml"
    gotm_yaml = f"{setup_dir}/gotm/extern/flexout/extern/fortran-yaml"
    
    # Backup original FABM yaml (only if not already backed up)
    run_wsl(f"if [ ! -f {fabm_yaml}/yaml_types.F90.bak ]; then "
            f"cp {fabm_yaml}/yaml_types.F90 {fabm_yaml}/yaml_types.F90.bak; "
            f"cp {fabm_yaml}/yaml.F90 {fabm_yaml}/yaml.F90.bak 2>/dev/null || true; "
            f"echo 'Backup created'; "
            f"else echo 'Backup already exists'; fi")
    
    # Copy GOTM's yaml to FABM's yaml dir
    run_wsl(f"cp {gotm_yaml}/yaml_types.F90 {fabm_yaml}/yaml_types.F90")
    run_wsl(f"cp {gotm_yaml}/yaml.F90 {fabm_yaml}/yaml.F90")
    print("  Replaced FABM yaml with GOTM yaml")
    
    # Step 3: Build FABM
    print("\n[3] Building FABM...")
    cmake_cmd = (
        f"cd {build_dir}/fabm && "
        f"export CC=gcc-9 && export CXX=g++-9 && export FC=gfortran-9 && "
        f"cmake {setup_dir}/fabm/src "
        f"-DCMAKE_INSTALL_PREFIX={install_dir}/fabm "
        f"-DFABM_HOST=gotm "
        f"-DCMAKE_BUILD_TYPE=Release "
        f"-DCMAKE_Fortran_FLAGS_RELEASE='-O2'"
    )
    if not run_wsl(cmake_cmd, os.path.join(LOG_DIR, "fabm_cmake_gcc9_v3.log")):
        print("FABM CMake failed!")
        return 1
    
    if not run_wsl(f"cd {build_dir}/fabm && export CC=gcc-9 && export CXX=g++-9 && export FC=gfortran-9 && make -j$(nproc)",
                   os.path.join(LOG_DIR, "fabm_build_gcc9_v3.log")):
        print("FABM build failed!")
        return 1
    
    if not run_wsl(f"cd {build_dir}/fabm && make install",
                   os.path.join(LOG_DIR, "fabm_install_gcc9_v3.log")):
        print("FABM install failed!")
        return 1
    
    # Step 4: Build GETM
    print("\n[4] Building GETM...")
    cmake_cmd = (
        f"cd {build_dir}/getm && "
        f"export CC=gcc-9 && export CXX=g++-9 && export FC=gfortran-9 && "
        f"cmake {setup_dir}/getm/src "
        f"-DCMAKE_INSTALL_PREFIX={install_dir} "
        f"-DGOTM_BASE={setup_dir}/gotm "
        f"-DFABM_PREFIX={install_dir}/fabm "
        f"-DGETM_USE_FABM=ON "
        f"-DGETM_USE_CARTESIAN=ON "
        f"-DCMAKE_BUILD_TYPE=Release "
        f"-DCMAKE_Fortran_FLAGS_RELEASE='-O2'"
    )
    if not run_wsl(cmake_cmd, os.path.join(LOG_DIR, "getm_cmake_gcc9_v3.log")):
        print("GETM CMake failed!")
        return 1
    
    if not run_wsl(f"cd {build_dir}/getm && export CC=gcc-9 && export CXX=g++-9 && export FC=gfortran-9 && make -j$(nproc)",
                   os.path.join(LOG_DIR, "getm_build_gcc9_v3.log")):
        print("GETM build failed!")
        return 1
    
    if not run_wsl(f"cd {build_dir}/getm && make install",
                   os.path.join(LOG_DIR, "getm_install_gcc9_v3.log")):
        print("GETM install failed!")
        return 1
    
    print("\n" + "=" * 60)
    print("BUILD COMPLETE!")
    print(f"Installed to: {install_dir}")
    print("=" * 60)
    
    # Show installed files
    result = subprocess.run(
        ["wsl", "find", install_dir, "-name", "getm*", "-type", "f"],
        capture_output=True, text=True
    )
    print("Installed files:")
    print(result.stdout)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
