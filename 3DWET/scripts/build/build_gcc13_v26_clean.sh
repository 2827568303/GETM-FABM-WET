#!/bin/bash
# Build script v26_clean_production: Clean production build with all fixes, NO debug output
# Uses ORIGINAL fabm.F90 (no debug output)
# Fixes included:
#   1. gotm_fabm.F90: itime optional argument fix
#   2. fish.F90: check_state qStage conditional fix

SETUP_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake"
WET_DIR="${SETUP_DIR}/wet"
WET_SRC_DIR="${WET_DIR}/src"
FABM_SRC_DIR="${SETUP_DIR}/fabm/src"
GOTM_FABM_DIR="${SETUP_DIR}/gotm/src/fabm"
BUILD_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_v26_clean"
INSTALL_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/install_gcc13_v26_clean"
PATCH_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-WET"

export CC=gcc-13
export CXX=g++-13
export FC=gfortran-13

echo "Using compilers: $CC / $FC"
$FC --version | head -1

mkdir -p "$BUILD_DIR/fabm"
mkdir -p "$BUILD_DIR/getm"
mkdir -p "$INSTALL_DIR"

echo ""
echo "=== Step 1: Backup all current files ==="
cp "$WET_SRC_DIR/fish.F90" "$WET_SRC_DIR/fish.F90.bak_v26" 2>/dev/null || true
cp "$GOTM_FABM_DIR/gotm_fabm.F90" "$GOTM_FABM_DIR/gotm_fabm.F90.bak_v26" 2>/dev/null || true
cp "$FABM_SRC_DIR/fabm.F90" "$FABM_SRC_DIR/fabm.F90.bak_v26" 2>/dev/null || true
echo "All current files backed up."

echo ""
echo "=== Step 2: Restore ORIGINAL fabm.F90 (no debug output) ==="
cp "$FABM_SRC_DIR/fabm.F90.bak_v13" "$FABM_SRC_DIR/fabm.F90"
echo "fabm.F90 restored to original (v13 backup, no debug output)."

echo ""
echo "=== Step 3: Apply WET fish module fix ==="
cp "$PATCH_DIR/fish_v2_patched.F90" "$WET_SRC_DIR/fish.F90"
echo "fish.F90: check_state qStage fix applied."

echo ""
echo "=== Step 4: Apply gotm_fabm.F90 itime fix ==="
cp "$PATCH_DIR/gotm_fabm_itime_fixed.F90" "$GOTM_FABM_DIR/gotm_fabm.F90"
echo "gotm_fabm.F90: itime optional argument fix applied."

echo ""
echo "=== Step 5: Building FABM with WET model (GCC 13, Release) ==="
cd "$BUILD_DIR/fabm"
cmake "$SETUP_DIR/fabm/src" \
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
echo "=== Step 6: Apply getm_fabm.F90 v2 patch ==="
cp "$PATCH_DIR/getm_fabm_v2_patched.F90" "$SETUP_DIR/getm/src/3d/getm_fabm.F90"
echo "getm_fabm.F90 patched (v2)."

echo ""
echo "=== Step 7: Building GETM with FABM (GCC 13, Release, YAML mode) ==="
cd "$BUILD_DIR/getm"
cmake "$SETUP_DIR/getm/src" \
    -DCMAKE_INSTALL_PREFIX="$INSTALL_DIR" \
    -DGOTM_BASE="$SETUP_DIR/gotm" \
    -DFABM_PREFIX="$INSTALL_DIR/fabm" \
    -DGETM_USE_FABM=ON \
    -DGETM_USE_CARTESIAN=ON \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_Fortran_FLAGS_RELEASE="-O2 -U_GOTM_FABM_NML_" 2>&1 | tee getm_cmake.log

echo "GETM CMake exit code: $?"

make -j4 2>&1 | tee getm_build.log
echo "GETM make exit code: $?"

make install 2>&1 | tee -a getm_build.log
echo "GETM install exit code: $?"

echo ""
echo "=== Step 8: Restore all original files ==="
cp "$WET_SRC_DIR/fish.F90.bak_v26" "$WET_SRC_DIR/fish.F90" 2>/dev/null || true
cp "$GOTM_FABM_DIR/gotm_fabm.F90.bak_v26" "$GOTM_FABM_DIR/gotm_fabm.F90" 2>/dev/null || true
cp "$FABM_SRC_DIR/fabm.F90.bak_v26" "$FABM_SRC_DIR/fabm.F90" 2>/dev/null || true
echo "All original files restored."

echo ""
echo "=== Build complete ==="
ls -la "$INSTALL_DIR/bin/"
