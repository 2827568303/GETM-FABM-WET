#!/usr/bin/env bash
# Linux build of FABM+WET and GETM (Cartesian, OpenMP, FABM).
# Writes 3DWET/bin/getm_cartesian. `mpi` also writes getm_cartesian_parallel.
# Safe to re-run. FABM always includes the WET institute.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)/3DWET"
BUILD="$ROOT/build-linux"
INSTALL="$ROOT/install-linux"
NJOB="${NJOB:-2}"
STAGE="${1:-openmp}"
FABM_INSTITUTES="au;bb;examples;gotm;jrc;pclake;pml;selma;ersem;su;niva;akvaplan;wet"

echo "===== FABM configure ====="
cmake -S "$ROOT/src/fabm/src" -B "$BUILD/fabm" \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="$INSTALL/fabm" \
  -DFABM_HOST=gotm \
  -DFABM_WET_BASE="$ROOT/src/wet" \
  -DFABM_INSTITUTES="$FABM_INSTITUTES"
echo "===== FABM build ====="
cmake --build "$BUILD/fabm" --parallel "$NJOB"
cmake --install "$BUILD/fabm"

echo "===== GETM configure (Cartesian + OpenMP + FABM) ====="
cmake -S "$ROOT/src/getm/src" -B "$BUILD/getm" \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="$INSTALL" \
  -DCMAKE_Fortran_FLAGS="-O2 -fopenmp -DGETM_OMP -ffree-line-length-none -I/usr/include" \
  -DGOTM_BASE="$ROOT/src/gotm" \
  -DGETM_USE_FABM=ON \
  -DFABM_PREFIX="$INSTALL/fabm" \
  -DGETM_COORDINATE_TYPE=Cartesian
echo "===== GETM build ====="
cmake --build "$BUILD/getm" --parallel "$NJOB"
mkdir -p "$ROOT/bin"
cp -f "$BUILD/getm/getm_cartesian" "$ROOT/bin/getm_cartesian"
cp -f "$BUILD/getm/getm_cartesian" "$INSTALL/bin/getm_cartesian" 2>/dev/null || \
  mkdir -p "$INSTALL/bin" && cp -f "$BUILD/getm/getm_cartesian" "$INSTALL/bin/getm_cartesian"
ls -lh "$ROOT/bin/getm_cartesian"
if [[ "$STAGE" == "mpi" || "$STAGE" == "all" ]]; then
  echo "===== GETM configure (Cartesian + MPI + OpenMP + FABM/WET) ====="
  cmake -S "$ROOT/src/getm/src" -B "$BUILD/getm-parallel" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_Fortran_FLAGS="-O2 -fopenmp -DGETM_OMP -ffree-line-length-none -I/usr/include" \
    -DGOTM_BASE="$ROOT/src/gotm" \
    -DGETM_USE_FABM=ON \
    -DGETM_USE_PARALLEL=ON \
    -DFABM_PREFIX="$INSTALL/fabm" \
    -DFABM_WET_BASE="$ROOT/src/wet" \
    -DFABM_INSTITUTES="$FABM_INSTITUTES" \
    -DGETM_COORDINATE_TYPE=Cartesian
  echo "===== GETM parallel build ====="
  cmake --build "$BUILD/getm-parallel" --parallel "$NJOB" --target getm_exe
  cp -f "$BUILD/getm-parallel/getm_cartesian_parallel" "$ROOT/bin/getm_cartesian_parallel"
  ls -lh "$ROOT/bin/getm_cartesian_parallel"
fi
echo BUILD_LINUX_SOLVER_OK
