#!/bin/bash
# Build with lower optimization to avoid GCC internal compiler error

SETUP_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake"

echo "=========================================="
echo "Step 1: Building and installing FABM"
echo "=========================================="

cd "$SETUP_DIR"
mkdir -p build/fabm
cd build/fabm

cmake "$SETUP_DIR/fabm" \
    -DCMAKE_INSTALL_PREFIX="$SETUP_DIR/install/fabm" \
    -DGOTM_BASE="$SETUP_DIR/gotm" \
    -DFABM_WET=ON \
    -DWET_BASE="$SETUP_DIR/wet" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_Fortran_FLAGS_RELEASE="-O1" \
    2>&1

make -j1 2>&1 | tee fabm_build.log
make install 2>&1 | tee -a fabm_build.log

if [ ! -f "$SETUP_DIR/install/fabm/lib/libfabm.a" ]; then
    echo "[ERROR] FABM build failed!"
    tail -50 fabm_build.log
    exit 1
fi

echo ""
echo "=========================================="
echo "Step 2: Building GETM with lower optimization"
echo "=========================================="

cd "$SETUP_DIR"
mkdir -p build/getm
cd build/getm

cmake "$SETUP_DIR/getm/src" \
    -DCMAKE_INSTALL_PREFIX="$SETUP_DIR/install" \
    -DGOTM_BASE="$SETUP_DIR/gotm" \
    -DFABM_PREFIX="$SETUP_DIR/install/fabm" \
    -DGETM_USE_FABM=ON \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_Fortran_FLAGS_RELEASE="-O1 -fno-whole-file" \
    2>&1

echo ""
echo "Starting build with single thread..."
make -j1 2>&1 | tee getm_build.log

# Check if successful
if [ -f "$SETUP_DIR/install/bin/getm_cartesian" ]; then
    echo ""
    echo "[SUCCESS] Build completed!"
    ls -la "$SETUP_DIR/install/bin/getm_cartesian"
else
    echo ""
    echo "[ERROR] Build failed. Check getm_build.log for details."
    tail -100 getm_build.log
fi
