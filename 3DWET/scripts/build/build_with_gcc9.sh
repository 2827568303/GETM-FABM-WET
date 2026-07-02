#!/bin/bash
# Build script using GCC 9 to avoid GCC 13 internal compiler error
# Working directory: /mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake

SETUP_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake"
BUILD_DIR="${SETUP_DIR}/build_gcc9"
INSTALL_DIR="${SETUP_DIR}/install_gcc9"

export CC=gcc-9
export CXX=g++-9
export FC=gfortran-9

echo "Using compilers: $CC / $FC"
$FC --version | head -1

# Create build directories
mkdir -p "$BUILD_DIR/fabm"
mkdir -p "$BUILD_DIR/getm"
mkdir -p "$INSTALL_DIR"

echo ""
echo "=== Step 1: Building FABM ==="
cd "$BUILD_DIR/fabm"
cmake "$SETUP_DIR/fabm/src" \
    -DCMAKE_INSTALL_PREFIX="$INSTALL_DIR/fabm" \
    -DFABM_HOST=gotm \
    -DFABM_EMBED_VERSION=OFF \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_Fortran_FLAGS_RELEASE="-O2" 2>&1 | tee fabm_cmake.log

make -j4 2>&1 | tee fabm_build.log
make install 2>&1 | tee -a fabm_build.log

echo ""
echo "=== Step 2: Building GETM with FABM ==="
cd "$BUILD_DIR/getm"
cmake "$SETUP_DIR/getm/src" \
    -DCMAKE_INSTALL_PREFIX="$INSTALL_DIR" \
    -DGOTM_BASE="$SETUP_DIR/gotm" \
    -DFABM_PREFIX="$INSTALL_DIR/fabm" \
    -DGETM_USE_FABM=ON \
    -DGETM_USE_CARTESIAN=ON \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_Fortran_FLAGS_RELEASE="-O2" 2>&1 | tee getm_cmake.log

make -j4 2>&1 | tee getm_build.log
make install 2>&1 | tee -a getm_build.log

echo ""
echo "=== Build complete ==="
ls -la "$INSTALL_DIR/bin/"