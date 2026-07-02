#!/bin/bash
# Build script with low optimization to avoid GCC 13.3.0 internal error

PROJECT_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake"
BUILD_DIR="${PROJECT_DIR}/build/getm"

cd "$BUILD_DIR"

# Single-threaded build with -O0 for gotm_fabm
echo "Building with single thread and low optimization..."
make -j1 CFLAGS="-O0" CXXFLAGS="-O0" FFLAGS="-O0" 2>&1 | tee build_low_opt.log