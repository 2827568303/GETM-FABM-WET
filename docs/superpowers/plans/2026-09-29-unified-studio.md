# Unified Studio Implementation Plan

> Execute with subagent-driven-development; keep original case data unchanged.

**Goal:** Deliver unified browser and Windows apps integrating project management, current model workflow and grid editing.

**Architecture:** Retain existing Flask routes and model algorithms. Add focused launcher, diagnostics and grid API modules; share HTML/CSS/JS across browser and pywebview desktop.

**Tech Stack:** Python, Flask/Waitress, NetCDF4, NumPy, existing Chart.js/Plotly/Leaflet, pywebview, PyInstaller.

## Tasks and checkpoints

- [ ] Startup: create `3DWET/app/runtime.py`, `launcher.py`, root dependency files and Web/desktop entry points. Tests in `tests/test_runtime.py` must prove identity health checks, runtime dependency reporting and readiness before browser opening. Run `.venv/Scripts/python -m pytest tests/test_runtime.py -q`.
- [ ] Grid integration: add `3DWET/app/grid_api.py`, shared editor JS and its page. Tests use temporary NetCDF and check undo/redo, nonfinite and invalid index rejection, unrelated-variable preservation, backup writes and running-case protection. Never invoke an existing test that writes original cases.
- [ ] Redesign: add `studio.css` and `studio.js`, update existing template without removing existing element IDs, hooks or pages. Expose all original views in grouped navigation. Browser-check all navigation and empty states, and editor operations on a copied case.
- [ ] Project migration: inspect old project.json format, implement import through validated existing case builder. Test conversion with a temporary project; surface unsupported fields and never run a fixed test_case.
- [ ] Packaging: build PyInstaller Windows app and portable distribution referencing included model tree, verify resources and runtime paths. Add launch documentation and software notices. Probe model DLL dependencies, install or package required runtime within project.
- [ ] End-to-end verification: execute temporary short model case, inspect finite water-cell outputs and run completion. Verify browser and desktop lifecycle, record failures and limitations separately from successful checks.

## Review

For each task inspect spec coverage, then code quality. Final review must check no loss of existing navigation, no writes to source cases, actual active-case execution, HTTP health identity and portable path handling. Release only after checks prove deliverables; keep unresolved items explicit.
