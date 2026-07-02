#!/bin/bash
# Rebuild FABM and GETM after applying time_step patch

SETUP_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake"
BUILD_DIR="$SETUP_DIR/build"
FABM_SOURCE_DIR="$SETUP_DIR/fabm"
GOTM_SOURCE_DIR="$SETUP_DIR/gotm"

echo "=========================================="
echo "Rebuilding FABM and GETM after time_step patch"
echo "=========================================="

cd "$SETUP_DIR"
echo "Working directory: $(pwd)"

# Check if patch was applied
if grep -q "time_step_id" "$GOTM_SOURCE_DIR/src/fabm/gotm_fabm.F90"; then
    echo "[OK] time_step patch detected in gotm_fabm.F90"
else
    echo "[ERROR] time_step patch not found. Please run patch_time_step.sh first."
    exit 1
fi

# Clean previous build
echo ""
echo "Cleaning previous build..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# ============================================
# Step 1: Build FABM
# ============================================
echo ""
echo "=== Step 1: Building FABM ==="
cd "$BUILD_DIR"
cmake "$FABM_SOURCE_DIR" -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF
make -j$(nproc)

# Find and copy libfabm.a
FABM_LIB=$(find "$BUILD_DIR" -name "libfabm.a" 2>/dev/null | head -1)
TARGET_LIB_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/lib"
mkdir -p "$TARGET_LIB_DIR"
if [ -n "$FABM_LIB" ] && [ -f "$FABM_LIB" ]; then
    cp "$FABM_LIB" "$TARGET_LIB_DIR/"
    echo "[OK] Copied libfabm.a to $TARGET_LIB_DIR/"
    ls -la "$TARGET_LIB_DIR/libfabm.a"
else
    echo "[ERROR] libfabm.a not found"
    ls -la "$BUILD_DIR"
    exit 1
fi

# ============================================
# Step 2: Build GOTM with embedded FABM
# ============================================
echo ""
echo "=== Step 2: Building GOTM with embedded FABM ==="

# Create fresh build directory for GOTM
rm -rf "$BUILD_DIR"/*
mkdir -p "$BUILD_DIR/gotm_build"
cd "$BUILD_DIR/gotm_build"

# Configure GOTM - it will use FABM_BASE to find embedded FABM
cmake "$GOTM_SOURCE_DIR" \
    -DCMAKE_BUILD_TYPE=Release \
    -DGOTM_BUILD_FABM=ON \
    -DFABM_BASE="$FABM_SOURCE_DIR"

make -j$(nproc)

# Copy getm_cartesian to target
GOTM_BIN="$BUILD_DIR/gotm_build/gotm/getm_cartesian"
TARGET_BIN_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/bin"
mkdir -p "$TARGET_BIN_DIR"
if [ -f "$GOTM_BIN" ]; then
    cp "$GOTM_BIN" "$TARGET_BIN_DIR/"
    echo "[OK] Copied getm_cartesian to $TARGET_BIN_DIR/"
    ls -la "$TARGET_BIN_DIR/getm_cartesian"
else
    echo "[ERROR] getm_cartesian not found at $GOTM_BIN"
    find "$BUILD_DIR" -name "getm*" -type f 2>/dev/null
    exit 1
fi

echo ""
echo "=========================================="
echo "Build completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Test the fish module by running:"
echo "   cd /mnt/c/Users/dinod/Desktop/GETM-FABM-WET/luomahu_case && ./test_fish.sh"
echo "2. Or run the full food web test with:"
echo "   ./run_fullfoodweb_30d.sh"
