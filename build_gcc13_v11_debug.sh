#!/bin/bash
# Build script v11: GCC 13 + O0 + debug checks + time_step bulk variable patch + WET model + YAML mode
# Working directory: /mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake

SETUP_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake"
WET_DIR="${SETUP_DIR}/wet"
BUILD_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_v11_debug"
INSTALL_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/install_gcc13_v11_debug"
PATCH_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-WET"

export CC=gcc-13
export CXX=g++-13
export FC=gfortran-13

echo "Using compilers: $CC / $FC"
$FC --version | head -1

# Create build directories
mkdir -p "$BUILD_DIR/fabm"
mkdir -p "$BUILD_DIR/getm"
mkdir -p "$INSTALL_DIR"

# Apply getm_fabm.F90 patch
cp "$PATCH_DIR/getm_fabm_patched.F90" "$SETUP_DIR/getm/src/3d/getm_fabm.F90"
echo "Patch applied."

echo ""
echo "=== Step 1: Building FABM with WET model (GCC 13, Debug) ==="
cd "$BUILD_DIR/fabm"
cmake "$SETUP_DIR/fabm/src" \
    -DCMAKE_INSTALL_PREFIX="$INSTALL_DIR/fabm" \
    -DFABM_HOST=gotm \
    -DFABM_EMBED_VERSION=OFF \
    -DFABM_WET_BASE="${WET_DIR}" \
    -DCMAKE_BUILD_TYPE=Debug \
    -DCMAKE_Fortran_FLAGS_DEBUG="-O0 -g -fcheck=all -fbacktrace" 2>&1 | tee fabm_cmake.log

echo "FABM CMake exit code: $?"

make -j4 2>&1 | tee fabm_build.log
echo "FABM make exit code: $?"

make install 2>&1 | tee -a fabm_build.log
echo "FABM install exit code: $?"

echo ""
echo "=== Step 2: Building GETM with FABM (GCC 13, Debug, YAML mode) ==="
cd "$BUILD_DIR/getm"
cmake "$SETUP_DIR/getm/src" \
    -DCMAKE_INSTALL_PREFIX="$INSTALL_DIR" \
    -DGOTM_BASE="$SETUP_DIR/gotm" \
    -DFABM_PREFIX="$INSTALL_DIR/fabm" \
    -DGETM_USE_FABM=ON \
    -DGETM_USE_CARTESIAN=ON \
    -DCMAKE_BUILD_TYPE=Debug \
    -DCMAKE_Fortran_FLAGS_DEBUG="-O0 -g -fcheck=all -fbacktrace -U_GOTM_FABM_NML_" 2>&1 | tee getm_cmake.log

echo "GETM CMake exit code: $?"

make -j4 2>&1 | tee getm_build.log
echo "GETM make exit code: $?"

make install 2>&1 | tee -a getm_build.log
echo "GETM install exit code: $?"

echo ""
echo "=== Build complete ==="
ls -la "$INSTALL_DIR/bin/"
