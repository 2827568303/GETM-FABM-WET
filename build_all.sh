#!/bin/bash
# ============================================================
# GETM-FABM-PCLake/WET 三维湖泊生态系统模型 编译脚本
# 适用环境: WSL2 + Ubuntu 24.04
# 文档版本: v2.0
# 更新日期: 2026-06-28
# ============================================================

set -e  # 遇到错误立即退出

# ============================================================
# 配置项
# ============================================================

# 项目根目录（Windows 路径在 WSL 中为 /mnt/c/...）
PROJECT_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake"

# 源码目录
GETM_SRC="${PROJECT_DIR}/getm/src"
GOTM_SRC="${PROJECT_DIR}/gotm"
FABM_SRC="${PROJECT_DIR}/fabm"
WET_SRC="${PROJECT_DIR}/wet"

# 构建目录
BUILD_DIR="${PROJECT_DIR}/build"
FABM_BUILD="${BUILD_DIR}/fabm"
GETM_BUILD="${BUILD_DIR}/getm"

# 安装目录
INSTALL_DIR="${PROJECT_DIR}/install"
FABM_INSTALL="${INSTALL_DIR}/fabm"

# 编译类型: Release / Debug
BUILD_TYPE="Release"

# 并行编译任务数（使用所有 CPU 核心）
NPROC=$(nproc)

# ============================================================
# 颜色输出
# ============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# ============================================================
# 步骤 0: 环境检查
# ============================================================

check_environment() {
    echo ""
    echo "=============================================="
    echo " 步骤 0: 环境检查"
    echo "=============================================="

    local missing_tools=()

    # 检查 gfortran
    if command -v gfortran &> /dev/null; then
        info "gfortran: $(gfortran --version | head -1)"
    else
        error "gfortran 未安装！请运行: sudo apt install gfortran"
        missing_tools+=("gfortran")
    fi

    # 检查 gcc
    if command -v gcc &> /dev/null; then
        info "gcc: $(gcc --version | head -1)"
    else
        missing_tools+=("gcc")
    fi

    # 检查 cmake
    if command -v cmake &> /dev/null; then
        info "cmake: $(cmake --version | head -1)"
    else
        missing_tools+=("cmake")
    fi

    # 检查 make
    if command -v make &> /dev/null; then
        info "make: $(make --version | head -1)"
    else
        missing_tools+=("make")
    fi

    # 检查 NetCDF
    if command -v nf-config &> /dev/null; then
        info "NetCDF-Fortran: $(nf-config --version)"
    else
        missing_tools+=("libnetcdff-dev")
    fi

    # 检查源码目录
    info "检查源代码目录..."
    [ -d "$GETM_SRC" ] || error "GETM 源码不存在: $GETM_SRC"
    [ -d "$GOTM_SRC" ] || error "GOTM 源码不存在: $GOTM_SRC"
    [ -d "$FABM_SRC" ] || error "FABM 源码不存在: $FABM_SRC"
    [ -d "$WET_SRC" ]  || error "WET 源码不存在: $WET_SRC"
    success "所有源代码目录存在"

    # 检查 flexout 子模块
    if [ ! -d "$GOTM_SRC/extern/flexout" ]; then
        warn "flexout 子模块不存在，将尝试初始化..."
        warn "如果失败，请手动执行: cd $GOTM_SRC/extern && git clone https://github.com/BoldingBruggeman/flexout.git"
    fi

    # 检查 yaml 子模块
    if [ ! -f "$GOTM_SRC/extern/flexout/extern/fortran-yaml/yaml.F90" ] && \
       [ ! -f "$GOTM_SRC/extern/flexout/extern/yaml/yaml.F90" ]; then
        warn "fortran-yaml 子模块可能缺失"
    fi

    if [ ${#missing_tools[@]} -gt 0 ]; then
        error "缺失工具: ${missing_tools[*]}"
    fi

    success "环境检查通过"
}

# ============================================================
# 步骤 1: 编译 FABM + WET/PCLake
# ============================================================

build_fabm() {
    echo ""
    echo "=============================================="
    echo " 步骤 1: 编译 FABM + WET/PCLake"
    echo "=============================================="

    info "创建构建目录..."
    mkdir -p "$FABM_BUILD"
    mkdir -p "$FABM_INSTALL"

    cd "$FABM_BUILD"

    info "配置 CMake..."
    cmake "$FABM_SRC" \
        -DCMAKE_INSTALL_PREFIX="$FABM_INSTALL" \
        -DGOTM_BASE="$GOTM_SRC" \
        -DFABM_EMBED_VERSION=ON \
        -DFABM_WET=ON \
        -DWET_BASE="$WET_SRC" \
        -DCMAKE_BUILD_TYPE="$BUILD_TYPE" \
        || error "FABM CMake 配置失败"

    success "FABM CMake 配置完成"

    info "编译 FABM (并行 ${NPROC} 任务)..."
    make -j$NPROC || error "FABM 编译失败"

    success "FABM 编译完成"

    info "安装 FABM..."
    make install || error "FABM 安装失败"

    success "FABM 安装完成"

    # 验证安装
    [ -f "$FABM_INSTALL/lib/libfabm.a" ] || error "FABM 库文件不存在: $FABM_INSTALL/lib/libfabm.a"
    info "FABM 库: $(ls -lh $FABM_INSTALL/lib/libfabm.a | awk '{print $5}')"
}

# ============================================================
# 步骤 2: 编译 GETM（耦合 FABM-WET）
# ============================================================

build_getm() {
    echo ""
    echo "=============================================="
    echo " 步骤 2: 编译 GETM（耦合 FABM-WET）"
    echo "=============================================="

    info "创建构建目录..."
    mkdir -p "$GETM_BUILD"

    cd "$GETM_BUILD"

    info "配置 CMake..."
    cmake "$GETM_SRC" \
        -DCMAKE_INSTALL_PREFIX="$INSTALL_DIR" \
        -DGOTM_BASE="$GOTM_SRC" \
        -DFABM_PREFIX="$FABM_INSTALL" \
        -DGETM_USE_FABM=ON \
        -DGETM_USE_CARTESIAN=ON \
        -DCMAKE_BUILD_TYPE="$BUILD_TYPE" \
        || error "GETM CMake 配置失败"

    success "GETM CMake 配置完成"

    info "编译 GETM (并行 ${NPROC} 任务)..."
    make -j$NPROC || error "GETM 编译失败"

    success "GETM 编译完成"

    info "安装 GETM..."
    make install || error "GETM 安装失败"

    success "GETM 安装完成"

    # 验证安装
    [ -f "$INSTALL_DIR/bin/getm_cartesian" ] || error "GETM 可执行文件不存在: $INSTALL_DIR/bin/getm_cartesian"
    info "getm_cartesian: $(ls -lh $INSTALL_DIR/bin/getm_cartesian | awk '{print $5}')"
}

# ============================================================
# 步骤 3: 验证编译结果
# ============================================================

verify_build() {
    echo ""
    echo "=============================================="
    echo " 步骤 3: 验证编译结果"
    echo "=============================================="

    info "检查 FABM 安装..."
    echo "  库文件:"
    ls -lh "$FABM_INSTALL/lib/" 2>/dev/null | grep -E '\.a$' || warn "未找到 .a 库文件"
    echo "  模块文件 (前10个):"
    ls "$FABM_INSTALL/include/" 2>/dev/null | head -10 || warn "未找到模块文件"

    info "检查 WET 模块..."
    local wet_modules=$(ls "$FABM_INSTALL/include/wet_"*.mod 2>/dev/null | wc -l)
    info "WET 模块数量: $wet_modules"
    if [ "$wet_modules" -gt 0 ]; then
        ls "$FABM_INSTALL/include/wet_"*.mod 2>/dev/null | xargs -n1 basename | head -10
    fi

    info "检查 GETM 可执行文件..."
    ls -lh "$INSTALL_DIR/bin/getm_cartesian" 2>/dev/null || error "getm_cartesian 不存在"

    echo ""
    success "=============================================="
    success "  编译完成！"
    success "=============================================="
    echo ""
    echo "  FABM 安装目录: $FABM_INSTALL"
    echo "  GETM 可执行文件: $INSTALL_DIR/bin/getm_cartesian"
    echo ""
    echo "  运行模型示例:"
    echo "    cd /mnt/c/Users/dinod/Desktop/GETM-FABM-WET/test_case"
    echo "    $INSTALL_DIR/bin/getm_cartesian"
    echo ""
}

# ============================================================
# 清理构建（可选）
# ============================================================

clean_build() {
    warn "清理所有构建文件..."
    rm -rf "$BUILD_DIR"
    rm -rf "$INSTALL_DIR"
    success "清理完成"
}

# ============================================================
# 主函数
# ============================================================

main() {
    echo ""
    echo "============================================================"
    echo "  GETM-FABM-PCLake/WET 三维湖泊生态系统模型 编译脚本"
    echo "============================================================"
    echo "  项目目录: $PROJECT_DIR"
    echo "  编译类型: $BUILD_TYPE"
    echo "  并行任务: $NPROC"
    echo "============================================================"

    # 解析命令行参数
    local action="all"
    if [ $# -ge 1 ]; then
        action="$1"
    fi

    case "$action" in
        check)
            check_environment
            ;;
        fabm)
            check_environment
            build_fabm
            ;;
        getm)
            check_environment
            build_getm
            ;;
        clean)
            clean_build
            ;;
        all)
            check_environment
            build_fabm
            build_getm
            verify_build
            ;;
        *)
            echo "用法: $0 [check|fabm|getm|clean|all]"
            echo ""
            echo "  check   - 仅检查环境"
            echo "  fabm    - 仅编译 FABM + WET"
            echo "  getm    - 仅编译 GETM（需要先编译 FABM）"
            echo "  clean   - 清理所有构建文件"
            echo "  all     - 完整编译（默认）"
            echo ""
            exit 1
            ;;
    esac
}

main "$@"
