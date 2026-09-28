@echo off
chcp 65001 >nul
title 3DWET 网格编辑器
cd /d "%~dp0"

REM 优先使用 Anaconda Python（已安装 PyQt5/netCDF4/numpy/scipy/matplotlib）
set "PYTHON=C:\ProgramData\anaconda3\python.exe"

if not exist "%PYTHON%" (
    echo 未找到 Anaconda Python，尝试系统 Python...
    set "PYTHON=python"
)

echo ============================================
echo   3DWET 网格编辑器
echo ============================================
echo.
echo 正在启动...
echo.

"%PYTHON%" main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================
    echo  程序异常退出 (代码: %ERRORLEVEL%)
    echo ============================================
    echo.
    echo 如缺少依赖，请在 Anaconda Prompt 中执行:
    echo   pip install PyQt5 netCDF4 numpy scipy matplotlib
    echo.
    pause
)
