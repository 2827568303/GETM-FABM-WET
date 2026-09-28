#!/bin/bash
# Windows-native build of FABM + GETM (getm_cartesian.exe) with MSYS2 UCRT64 toolchain.
# Replicates the WSL/Linux configure from 3DWET/build/{fabm,getm}/CMakeCache.txt.
# Usage: C:\Users\dinod\.local\share\msys64\usr\bin\bash.exe <this-script> [fabm|getm|all]
set -u
export PATH="/ucrt64/bin:/usr/bin:$PATH"

ROOT=/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET
BUILD=$ROOT/build-win
INSTALL=$ROOT/install-win
STAGE="${1:-all}"

COMMON_OPTS="-DCMAKE_BUILD_TYPE=Release -DCMAKE_POLICY_VERSION_MINIMUM=3.5"

build_fabm() {
  echo "===== FABM configure (pass 1, seeds default institutes) ====="
  cmake -S "$ROOT/src/fabm/src" -B "$BUILD/fabm" -G Ninja $COMMON_OPTS \
    -DCMAKE_INSTALL_PREFIX="$INSTALL/fabm" \
    -DFABM_HOST=gotm \
    -DFABM_WET_BASE="$ROOT/src/wet" \
    -DFABM_USE_DO_CONCURRENT=ON || return 1
  echo "===== FABM configure (pass 2, apply Linux institute list) ====="
  cmake -S "$ROOT/src/fabm/src" -B "$BUILD/fabm" $COMMON_OPTS \
    -DFABM_INSTITUTES="au;bb;examples;gotm;jrc;pclake;pml;selma;ersem;su;niva;akvaplan;wet" || return 1
  grep "^FABM_INSTITUTES" "$BUILD/fabm/CMakeCache.txt"
  echo "===== FABM build (serial: Fortran module deps + ninja dyndep race) ====="
  cmake --build "$BUILD/fabm" --parallel 1 || return 1
  echo "===== FABM install ====="
  cmake --install "$BUILD/fabm" || return 1
}

build_getm() {
  echo "===== GETM configure ====="
  # nf-config is a shell script -> not executable by native CMake; pass NetCDF
  # paths explicitly as cache vars (respected by both GETM and flexout FindNetCDF).
  # Generator: MSYS Makefiles (ninja schedules 2d before domain because GETM's
  # CMakeLists lacks add_dependencies(2d domain); make follows listing order like
  # the working Linux build).
  UCRT=C:/Users/dinod/.local/share/msys64/ucrt64
  # No -fopenmp/-DGETM_OMP: with MinGW libgomp (winpthreads) the exe hangs in
  # clean_input at exit (verified: Linux ELF with OpenMP exits fine, Windows
  # exe freezes after "Cleaning up"; stdout buffer also never flushes).
  cmake -S "$ROOT/src/getm/src" -B "$BUILD/getm" -G "MSYS Makefiles" $COMMON_OPTS \
    -DCMAKE_Fortran_FLAGS="-O2 -U_GOTM_FABM_NML_" \
    -DGOTM_BASE="$ROOT/src/gotm" \
    -DGETM_USE_FABM=ON \
    -DFABM_PREFIX="$INSTALL/fabm" \
    -DGETM_COORDINATE_TYPE=Cartesian \
    -DNetCDF_INCLUDE_DIRS="$UCRT/include" \
    -DNetCDF_LIBRARIES="-L$UCRT/lib -lnetcdff -lnetcdf" || return 1
  echo "===== GETM build (serial) ====="
  cmake --build "$BUILD/getm" --parallel 1 || return 1
  ls -la "$BUILD/getm/getm_cartesian.exe" 2>/dev/null && echo "GETM_EXE_OK"
}

case "$STAGE" in
  fabm) build_fabm ;;
  getm) build_getm ;;
  all)  build_fabm && build_getm ;;
  *) echo "usage: $0 [fabm|getm|all]"; exit 1 ;;
esac
echo "BUILD_SCRIPT_DONE stage=$STAGE"
