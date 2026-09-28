@echo off
chcp 65001 >nul
title 3DWET Web 模型系统
cd /d "%~dp0"

set "PYTHON=C:\ProgramData\anaconda3\python.exe"
if not exist "%PYTHON%" set "PYTHON=python"

echo ============================================
echo   3DWET 生态水动力模型 Web 系统
echo ============================================
echo.
echo   服务地址: http://localhost:8766
echo   浏览器将自动打开...
echo   关闭此窗口将停止服务
echo ============================================
echo.

REM 延迟3秒后自动打开浏览器（在独立进程中执行，不阻塞服务器）
start /b "" cmd /c "timeout /t 3 /nobreak >nul 2>nul & start http://localhost:8766"

"%PYTHON%" server.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo 服务异常退出 (代码: %ERRORLEVEL%)
    echo 如缺少依赖: pip install flask pyyaml netCDF4 numpy waitress
    pause
)
