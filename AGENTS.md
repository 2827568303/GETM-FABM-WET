# Persistent model and delegation preference

For work in this repository, follow the user's explicit model assignment:

- Use **GPT-6.1 Sol** with **high** reasoning for overall ownership: scope, implementation method, architecture, integration, and final acceptance.
- Delegate concrete implementation and code changes only to **GPT-6 Luna** with **medium** reasoning.
- Do not assign this repository's work to other models or use other reasoning-effort levels for its agents or delegated tasks.
- Keep final verification and acceptance with GPT-6.1 Sol (high); implementation agents report changes and checks for independent review.

These are persistent user preferences and take precedence over default model/delegation choices for this project.

## Desktop application synchronization

- After every code change, automatically synchronize the desktop application with the updated source, including any required hot reload or restart.
- Verify that the desktop application is running and serving the current source/version, and report the synchronization check in progress updates.
- Before final delivery, ensure the desktop application has loaded the final version and verify it again.

## Cloud Agent

Linux sessions use the browser studio. WebView2 desktop launch stays on Windows (`launch_desktop.cmd`).

- The dev environment installs a Python 3.12 virtualenv at `.venv` from `requirements-dev.txt`, plus gfortran 13, CMake, NetCDF, NetCDF-Fortran, and `python3-tk` (the launcher self-test imports tkinter).
- `3DWET/case` is not tracked. Link `GETM-FABM-WET/3DWET/case` to `3DWET/case` so Lake Dianchi and Lake Luoma resolve, and set `WET_CASE_DIR` to that directory. Without it, storage falls back to a Windows `D:\` path and NetCDF tests fail while creating files.
- Serve the UI with `.venv/bin/python 3DWET/app/launcher.py --web --no-open --port 8766` at `http://127.0.0.1:8766`.
- Run pytest as two invocations, `tests` and `3DWET/tests`. Duplicate module names (`test_run_metrics.py`, `test_wet_foodweb.py`) cannot be collected together. `tests/test_attempt03_report_paths.py` imports a file that is not in the repository. Windows loader and `C:` drive tests do not apply here.
- Rebuild the Linux solver with `NJOB=$(nproc) bash scripts/build_linux_solver.sh`. The checked-in tree stops in `3DWET/src/getm/src/output/output.F90` because that target resolves GOTM's `time` module ahead of GETM's. `3DWET/bin` ships the Windows executable only.
