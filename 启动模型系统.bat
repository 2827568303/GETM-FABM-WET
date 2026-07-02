@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo ============================================================
echo   GETM-FABM-WET 生态水动力模型系统
echo ============================================================
echo.
python run_app.py
if errorlevel 1 (
    echo.
    echo 启动失败，请检查 Python 环境是否正确安装
    pause
)
