@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Run setup_studio.cmd first.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" "3DWET\app\launcher.py" --web %*
if errorlevel 1 pause
