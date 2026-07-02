#!/bin/bash
# 3DWET Model Build Script
# Build script for 3D Hydrodynamic-Water Quality-Food Web Model
# 
# This script builds the complete GETM-FABM-WET model with all fixes applied.
# 
# Fixes included:
#   1. gotm_fabm.F90: itime optional argument fix
#   2. fish.F90: check_state qStage conditional fix
#   3. getm_fabm.F90: v2 patch for improved coupling
#
# Usage: bash scripts/build_model.sh

# Determine the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"

SRC_DIR="${PROJECT_ROOT}/src"
WET_DIR="${SRC_DIR}/wet"
WET_SRC_DIR="${WET_DIR}/src"
FABM_SRC_DIR="${SRC_DIR}/fabm/src"
GOTM_FABM_DIR="${SRC_DIR}/gotm/src/fabm"
PATCH_DIR="${PROJECT_ROOT}/patches"
BUILD_DIR="${PROJECT_ROOT}/build"
INSTALL_DIR="${PROJECT_ROOT}/install"

# Compiler settings
# Support both versioned (gcc-13) and unversioned (gcc) compiler names
if command -v gcc-13 &>/dev/null; then
    export CC=gcc-13
    export CXX=g++-13
    export FC=gfortran-13
else
    export CC=gcc
    export CXX=g++
    export FC=gfortran
fi

echo "=========================================="
echo "  3DWET Model Build Script"
echo "  3D Hydrodynamic-Water Quality-Food Web"
echo "=========================================="
echo ""
echo "Project root: ${PROJECT_ROOT}"
echo "Source directory: ${SRC_DIR}"
echo "Build directory: ${BUILD_DIR}"
echo "Install directory: ${INSTALL_DIR}"
echo ""
echo "Using compilers: $CC / $FC"
$FC --version | head -1
echo ""

# Create directories
mkdir -p "$BUILD_DIR/fabm"
mkdir -p "$BUILD_DIR/getm"
mkdir -p "$INSTALL_DIR"

echo "=== Step 1: Backup current source files ==="
cp "$WET_SRC_DIR/fish.F90" "$WET_SRC_DIR/fish.F90.bak_build" 2>/dev/null || true
cp "$GOTM_FABM_DIR/gotm_fabm.F90" "$GOTM_FABM_DIR/gotm_fabm.F90.bak_build" 2>/dev/null || true
cp "$FABM_SRC_DIR/fabm.F90" "$FABM_SRC_DIR/fabm.F90.bak_build" 2>/dev/null || true
cp "$SRC_DIR/getm/src/3d/getm_fabm.F90" "$SRC_DIR/getm/src/3d/getm_fabm.F90.bak_build" 2>/dev/null || true
echo "Backup complete."
echo ""

echo "=== Step 1b: Remove DEBUG output from fabm.F90 ==="
python3 "${PROJECT_ROOT}/scripts/remove_debug.py" 2>/dev/null || true
echo "DEBUG output removed from fabm.F90."
echo ""

echo "=== Step 2: Apply WET fish module fix (check_state qStage) ==="
cp "$PATCH_DIR/fish_v2_patched.F90" "$WET_SRC_DIR/fish.F90"
echo "fish.F90: check_state qStage fix applied."
echo ""

echo "=== Step 3: Apply gotm_fabm.F90 itime fix ==="
cp "$PATCH_DIR/gotm_fabm_itime_fixed.F90" "$GOTM_FABM_DIR/gotm_fabm.F90"
echo "gotm_fabm.F90: itime optional argument fix applied."
echo ""

echo "=== Step 4: Building FABM with WET model (GCC 13, Release) ==="
cd "$BUILD_DIR/fabm"
cmake "$FABM_SRC_DIR" \
    -DCMAKE_INSTALL_PREFIX="$INSTALL_DIR/fabm" \
    -DFABM_HOST=gotm \
    -DFABM_EMBED_VERSION=OFF \
    -DFABM_WET_BASE="${WET_DIR}" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_Fortran_FLAGS_RELEASE="-O2" 2>&1 | tee fabm_cmake.log

echo "FABM CMake exit code: $?"

make -j4 2>&1 | tee fabm_build.log
echo "FABM make exit code: $?"

make install 2>&1 | tee -a fabm_build.log
echo "FABM install exit code: $?"
echo ""

echo "=== Step 5: Apply getm_fabm.F90 v2 patch ==="
cp "$PATCH_DIR/getm_fabm_v2_patched.F90" "$SRC_DIR/getm/src/3d/getm_fabm.F90"
echo "getm_fabm.F90 patched (v2)."
echo ""

echo "=== Step 6: Building GETM with FABM (GCC 13, Release, YAML mode, OpenMP) ==="
cd "$BUILD_DIR/getm"
# Enable OpenMP: -fopenmp activates !$OMP directives, -DGETM_OMP enables
# conditionally-compiled OpenMP sections (e.g. ip_shchepetkin_mcwilliams.F90).
cmake "$SRC_DIR/getm/src" \
    -DCMAKE_INSTALL_PREFIX="$INSTALL_DIR" \
    -DCMAKE_MODULE_PATH="${PROJECT_ROOT}/cmake" \
    -DGOTM_BASE="${SRC_DIR}/gotm" \
    -DFABM_PREFIX="$INSTALL_DIR/fabm" \
    -DGETM_USE_FABM=ON \
    -DGETM_USE_CARTESIAN=ON \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_Fortran_FLAGS_RELEASE="-O2 -U_GOTM_FABM_NML_ -fopenmp -DGETM_OMP" \
    -DCMAKE_EXE_LINKER_FLAGS="-fopenmp" 2>&1 | tee getm_cmake.log

echo "GETM CMake exit code: $?"

make -j4 2>&1 | tee getm_build.log
echo "GETM make exit code: $?"

make install 2>&1 | tee -a getm_build.log
echo "GETM install exit code: $?"
echo ""

echo "=== Step 7: Restore original source files ==="
cp "$WET_SRC_DIR/fish.F90.bak_build" "$WET_SRC_DIR/fish.F90" 2>/dev/null || true
cp "$GOTM_FABM_DIR/gotm_fabm.F90.bak_build" "$GOTM_FABM_DIR/gotm_fabm.F90" 2>/dev/null || true
cp "$FABM_SRC_DIR/fabm.F90.bak_build" "$FABM_SRC_DIR/fabm.F90" 2>/dev/null || true
cp "$SRC_DIR/getm/src/3d/getm_fabm.F90.bak_build" "$SRC_DIR/getm/src/3d/getm_fabm.F90" 2>/dev/null || true
echo "All original files restored."
echo ""

echo "=========================================="
echo "  Build Complete!"
echo "=========================================="
echo ""
echo "Executable: $INSTALL_DIR/bin/getm_cartesian"
ls -la "$INSTALL_DIR/bin/" 2>/dev/null || echo "No bin directory found"
echo ""
echo "To run the model:"
echo "  cd ${PROJECT_ROOT}/case"
echo "  ${INSTALL_DIR}/bin/getm_cartesian"
echo ""
