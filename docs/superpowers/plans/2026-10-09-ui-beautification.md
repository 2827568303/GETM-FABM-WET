# 3DWET Studio UI Beautification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply the approved “湖泊工作台” visual system to the existing 3DWET Studio WebView and browser UI without changing model behavior or stable controls.

**Architecture:** Keep `style.css` as the structural/base stylesheet and extend the existing `studio.css` override layer. Use CSS variables and selectors already present in `index.html`; do not add a new component framework or duplicate page markup. Verify with DOM/screenshot checks at normal and zoomed interface scales.

**Tech Stack:** HTML templates, CSS, existing Plotly/Chart.js/Leaflet containers, Node syntax checks, Python regression tests, local browser smoke testing.

---

### Task 1: Establish the unified lake-workbench theme

**Files:**
- Modify: `3DWET/app/static/css/studio.css`
- Test: `3DWET/tests/test_ui_theme.py`

- [ ] **Step 1: Write the theme contract test**

Create a small text-level test that asserts the stylesheet defines the lake-workbench variables, sidebar/current navigation rules, focus states, graph host rules, and responsive breakpoint. The test must not depend on a browser engine.

- [ ] **Step 2: Run the test and verify it fails**

Run `.venv/Scripts/python.exe -m pytest 3DWET/tests/test_ui_theme.py -q`. It should fail until the new selectors are present.

- [ ] **Step 3: Implement the CSS override layer**

Add the approved palette and reusable rules to `studio.css`: deep-blue sidebar, glassy topbar, unified card surfaces, workflow strip, stat-card accents, button hover/focus, form focus, table hover, diagnostic status surfaces, log styling, graph host, and 760px/1150px responsive adjustments. Keep all changes under the existing file and preserve the existing selectors/IDs.

- [ ] **Step 4: Run the theme contract test**

Run `.venv/Scripts/python.exe -m pytest 3DWET/tests/test_ui_theme.py -q` and expect the test to pass.

### Task 2: Verify the visual result in the browser and WebView-compatible DOM

**Files:**
- Modify: `3DWET/app/templates/index.html` only if a selector hook is required
- Test: `3DWET/tests/test_ui_theme.py`

- [ ] **Step 1: Check DOM hooks**

Assert the existing page contains `.sidebar`, `.topbar`, `.workflow-strip`, `.stat-card`, `.card`, `#run-log`, `.vc-graphic-host`, and `.vc-app-scale`. Add no new markup unless a screenshot shows a real gap.

- [ ] **Step 2: Run the local browser smoke check**

Start the local service with the prepared model root, open the dashboard, cases, run control, grid editor, diagnostics, and 3D pages, and capture screenshots after each navigation. Confirm the current case badge, run status, chart toolbars, and action buttons remain visible.

- [ ] **Step 3: Check interface scaling**

Use the existing Ctrl+wheel control to test 80%, 120%, and 160%. Confirm the sidebar, topbar, workflow strip, forms, and graph toolbars remain reachable without horizontal clipping.

- [ ] **Step 4: Run regression and JavaScript checks**

Run `.venv/Scripts/python.exe -m pytest tests -q`, `node --check 3DWET/app/static/js/app.js`, and the existing view-control/lake-geometry/render Node tests. Expected result: all existing tests pass and no JS syntax error is introduced.

### Task 3: Package and validate the beautified UI

**Files:**
- Modify: `scripts/build_app.py` only if the new stylesheet is not already collected
- Test: `release/verification/installed-ui-smoke-20261009.json`

- [ ] **Step 1: Rebuild the portable app**

Run `.venv/Scripts/python.exe scripts/build_app.py` and verify the staged tree contains the updated `studio.css` and `index.html`.

- [ ] **Step 2: Run frozen UI smoke**

Run the frozen launcher UI smoke with a fresh report path. Confirm the report checks the absence of the old hero text, successful loading of `studio.css`, `view_controls.css`, `ecology_network.js`, `gridstudio.js`, Plotly, Chart.js, and Leaflet.

- [ ] **Step 3: Rebuild the Windows installer**

Run `scripts/build_installer.ps1` with the staged directory and a patch version. Record the installer hash in `release/installer-manifest.json`.

- [ ] **Step 4: Verify the installed shortcut targets**

Inspect the two desktop shortcuts and confirm they target the installed executable, with the Web shortcut retaining `--web`.
