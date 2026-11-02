@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\pythonw.exe" (
    echo Run setup_studio.cmd first.
    pause
    exit /b 1
)
start "3DWET Studio" ".venv\Scripts\pythonw.exe" "3DWET\app\launcher.py" --desktop %*
