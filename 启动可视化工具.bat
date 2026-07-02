@echo off
chcp 65001 >nul
title GETM-FABM-WET 结果可视化工具
echo ============================================================
echo   GETM-FABM-WET 结果可视化工具
echo ============================================================
echo.
echo 正在启动...
echo.

cd /d "%~dp0"
python run_viewer.py

if errorlevel 1 (
    echo.
    echo 运行出错，请检查 Python 是否已安装
    pause
)
