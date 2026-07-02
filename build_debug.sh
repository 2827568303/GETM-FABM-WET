#!/bin/bash
# Build script with debug flags to diagnose segfault

SETUP_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake"
WET_DIR="${SETUP_DIR}/wet"
BUILD_DIR="${SETUP_DIR}/build_gcc9_debug"
INSTALL_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/install_gcc9_debug"

export CC=gcc-9
export CXX=g++-9
export FC=gfortran-9

echo "Building with debug flags (-O0 -g -fbacktrace)..."

# Clean build
rm -rf "$BUILD_DIR"
rm -rf "$INSTALL_DIR"

mkdir -p "$BUILD_DIR/fabm"
mkdir -p "$BUILD_DIR/getm"
mkdir -p "$INSTALL_DIR"

echo ""
echo "=== Step 1: Building FABM with WET model (debug) ==="
cd "$BUILD_DIR/fabm"
cmake "$SETUP_DIR/fabm/src" \
    -DCMAKE_INSTALL_PREFIX="$INSTALL_DIR/fabm" \
    -DFABM_HOST=gotm \
    -DFABM_EMBED_VERSION=OFF \
    -DFABM_WET_BASE="${WET_DIR}" \
    -DCMAKE_BUILD_TYPE=Debug \
    -DCMAKE_Fortran_FLAGS_DEBUG="-g -O0 -fbacktrace -finit-real=nan -fno-realloc-lhs -Wall" \
    2>&1 | tee fabm_cmake.log

make -j4 2>&1 | tee fabm_build.log
make install 2>&1 | tee -a fabm_build.log

echo ""
echo "=== Step 2: Building GETM with FABM (debug) ==="
cd "$BUILD_DIR/getm"
cmake "$SETUP_DIR/getm/src" \
    -DCMAKE_INSTALL_PREFIX="$INSTALL_DIR" \
    -DGOTM_BASE="$SETUP_DIR/gotm" \
    -DFABM_PREFIX="$INSTALL_DIR/fabm" \
    -DGETM_USE_FABM=ON \
    -DGETM_USE_CARTESIAN=ON \
    -DCMAKE_BUILD_TYPE=Debug \
    -DCMAKE_Fortran_FLAGS_DEBUG="-g -O0 -fbacktrace -finit-real=nan -fno-realloc-lhs -Wall" \
    2>&1 | tee getm_cmake.log

make -j4 2>&1 | tee getm_build.log
make install 2>&1 | tee -a getm_build.log

echo ""
echo "=== Build complete ==="
ls -la "$INSTALL_DIR/bin/"
