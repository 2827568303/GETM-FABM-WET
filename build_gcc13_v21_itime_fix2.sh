#!/bin/bash
# Build script v21_itime_fix2: Test itime fix with ORIGINAL om_pool (no om_pool patch)

SETUP_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake"
WET_DIR="${SETUP_DIR}/wet"
WET_SRC_DIR="${WET_DIR}/src"
FABM_SRC_DIR="${SETUP_DIR}/fabm/src"
GOTM_FABM_DIR="${SETUP_DIR}/gotm/src/fabm"
BUILD_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_v21_itime_fix2"
INSTALL_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/install_gcc13_v21_itime_fix2"
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
echo "=== Step 1: Apply WET model patches ==="
cp "$WET_SRC_DIR/fish.F90" "$WET_SRC_DIR/fish.F90.bak_v21" 2>/dev/null || true

cp "$PATCH_DIR/fish_v2_patched.F90" "$WET_SRC_DIR/fish.F90"
echo "fish.F90 patched (v2)."
echo "om_pool.F90: using ORIGINAL (no patch)."

echo ""
echo "=== Step 2: Apply fabm.F90 debug patch ==="
cp "$FABM_SRC_DIR/fabm.F90" "$FABM_SRC_DIR/fabm.F90.bak_v21" 2>/dev/null || true
cp "$PATCH_DIR/fabm_debug.F90" "$FABM_SRC_DIR/fabm.F90"
echo "fabm.F90 patched with debug output."

echo ""
echo "=== Step 3: Apply gotm_fabm.F90 itime fix ==="
cp "$GOTM_FABM_DIR/gotm_fabm.F90" "$GOTM_FABM_DIR/gotm_fabm.F90.bak_v21" 2>/dev/null || true
cp "$PATCH_DIR/gotm_fabm_itime_fixed.F90" "$GOTM_FABM_DIR/gotm_fabm.F90"
echo "gotm_fabm.F90 patched with itime fix."

echo ""
echo "=== Step 4: Building FABM with WET model (GCC 13, Debug) ==="
cd "$BUILD_DIR/fabm"
cmake "$SETUP_DIR/fabm/src" \
    -DCMAKE_INSTALL_PREFIX="$INSTALL_DIR/fabm" \
    -DFABM_HOST=gotm \
    -DFABM_EMBED_VERSION=OFF \
    -DFABM_WET_BASE="${WET_DIR}" \
    -DCMAKE_BUILD_TYPE=Debug \
    -DCMAKE_Fortran_FLAGS_DEBUG="-g -fcheck=all -fbacktrace" 2>&1 | tee fabm_cmake.log

echo "FABM CMake exit code: $?"

make -j4 2>&1 | tee fabm_build.log
echo "FABM make exit code: $?"

make install 2>&1 | tee -a fabm_build.log
echo "FABM install exit code: $?"

echo ""
echo "=== Step 5: Apply getm_fabm.F90 v2 patch ==="
cp "$PATCH_DIR/getm_fabm_v2_patched.F90" "$SETUP_DIR/getm/src/3d/getm_fabm.F90"
echo "getm_fabm.F90 patched (v2)."

echo ""
echo "=== Step 6: Building GETM with FABM (GCC 13, Debug, YAML mode) ==="
cd "$BUILD_DIR/getm"
cmake "$SETUP_DIR/getm/src" \
    -DCMAKE_INSTALL_PREFIX="$INSTALL_DIR" \
    -DGOTM_BASE="$SETUP_DIR/gotm" \
    -DFABM_PREFIX="$INSTALL_DIR/fabm" \
    -DGETM_USE_FABM=ON \
    -DGETM_USE_CARTESIAN=ON \
    -DCMAKE_BUILD_TYPE=Debug \
    -DCMAKE_Fortran_FLAGS_DEBUG="-g -fcheck=all -fbacktrace -U_GOTM_FABM_NML_" 2>&1 | tee getm_cmake.log

echo "GETM CMake exit code: $?"

make -j4 2>&1 | tee getm_build.log
echo "GETM make exit code: $?"

make install 2>&1 | tee -a getm_build.log
echo "GETM install exit code: $?"

echo ""
echo "=== Step 7: Restore original files ==="
cp "$WET_SRC_DIR/fish.F90.bak_v21" "$WET_SRC_DIR/fish.F90" 2>/dev/null || true
cp "$FABM_SRC_DIR/fabm.F90.bak_v21" "$FABM_SRC_DIR/fabm.F90" 2>/dev/null || true
cp "$GOTM_FABM_DIR/gotm_fabm.F90.bak_v21" "$GOTM_FABM_DIR/gotm_fabm.F90" 2>/dev/null || true
echo "Original files restored."

echo ""
echo "=== Build complete ==="
ls -la "$INSTALL_DIR/bin/"
