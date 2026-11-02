@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    py -3 -m venv .venv
    if errorlevel 1 goto fail
)
".venv\Scripts\python.exe" -m pip install -r requirements-dev.txt
if errorlevel 1 goto fail
echo Setup complete. Use launch_web.cmd or launch_desktop.cmd.
pause
exit /b 0
:fail
echo Setup failed. Install Python 3.10 or newer and try again.
pause
exit /b 1
