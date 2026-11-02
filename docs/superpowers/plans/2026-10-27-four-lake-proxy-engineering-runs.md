# Four-lake proxy engineering runs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Exercise the normal 3DWET 3D case workflow for Erken, Lake Ravn, Bryrup, and Arreskov using isolated, provenance-recorded proxy engineering cases while keeping each lake's scientific-validation status incomplete.

**Architecture:** Each isolated case carries a versioned `proxy_engineering.json` manifest listing input hashes and measured/derived/synthetic roles. The backend exposes that manifest as case status, and the UI keeps a visible proxy/non-validation badge from the case manager through dashboard, run, and result views. A case-preparation script copies only traceable available sources into a new attempt and uses existing grid/forcing conversion paths; it must stop with a precise blocker when required engineering inputs cannot be generated without inventing values. Final run acceptance uses the regular application journey, not a direct solver call alone.

**Tech Stack:** Python/Flask application, existing GETM case preparation and solver pipeline, JavaScript dashboard/case manager, pytest, Node test suite, Playwright/WebView manual verification.

---

### Task 1: Add manifest validation and provenance tests

**Files:**
- Create: `3DWET/app/proxy_engineering.py`
- Create: `3DWET/tests/test_proxy_engineering_manifest.py`

- [ ] Define schema version 1 with required `kind`, `target_lake`, `validation_status`, `geometry`, `forcing`, and `sources` fields. Accept only `kind="engineering_proxy"` and `validation_status="not_scientifically_validated"`.
- [ ] Validate source roles as `measured`, `derived`, `synthetic_proxy`, or `missing`; require path, byte count, and SHA-256 for present files. Do not allow a present source to use a missing digest or a missing source to claim measured.
- [ ] Add tests for a valid manifest, bad/unknown validation status, missing source digest, invalid role, and missing input representation.
- [ ] Run `python -m pytest 3DWET/tests/test_proxy_engineering_manifest.py -q`; confirm the tests fail before implementation and pass afterward.

### Task 2: Surface proxy status in case and active-case APIs

**Files:**
- Modify: `3DWET/app/server.py`
- Create: `3DWET/tests/test_proxy_engineering_api.py`

- [ ] In case metadata construction, read `proxy_engineering.json` with the validator from Task 1. Add `engineering_proxy`, `target_lake`, and `scientific_validation_status` response fields only when the manifest is valid.
- [ ] Keep invalid/missing manifests as ordinary cases and return a bounded warning field; do not infer science status from a case name.
- [ ] Add route tests proving a valid proxy case is labelled and a same-named case without the manifest is not labelled.
- [ ] Run `.venv/Scripts/python.exe -m pytest 3DWET/tests/test_proxy_engineering_api.py -q` and the case-storage/state-isolation tests.

### Task 3: Keep the proxy disclaimer visible across the UI

**Files:**
- Modify: `3DWET/app/templates/index.html`
- Modify: `3DWET/app/static/js/app.js`
- Modify: `3DWET/app/static/css/studio.css`
- Create or extend: `3DWET/tests/test_proxy_engineering_ui.js`

- [ ] Render a persistent `代理工程运行 · 非科学验证` status badge for valid proxy cases in the case manager, dashboard, run status, and result view. Use the manifest's target lake in the label.
- [ ] Show source categories and geometry/forcing provenance in a details panel without placing unsupported numeric claims in the headline.
- [ ] Preserve the badge when navigating between sections and refresh it when the active case changes. Do not infer proxy status from the display name.
- [ ] Add DOM tests for visible badge, status text, source roles, case switching, and normal-case behavior.
- [ ] Run the focused Node test and the UI localization/template tests; increment cache-busting versions for changed resources.

### Task 4: Prepare four isolated source-backed engineering attempts

**Files:**
- Create: `3DWET/scripts/prepare_proxy_engineering_cases.py`
- Create: `3DWET/tests/test_prepare_proxy_engineering_cases.py`
- Create outputs only under: `build/proxy-engineering-20261027/<lake>/`

- [ ] Inventory, without changing originals, the available Erken 3D proxy case, official Lake Ravn archive, WET Bryrup sources, and WET Arreskov sources. Record all source paths, sizes, hashes, licenses, and gaps before case creation.
- [ ] Build four independent copies in the attempt directory. Generate the manifest from actual copied bytes and label all derived grid geometry, spatially broadcast forcing, and any initialization surrogate explicitly.
- [ ] For each lake, stop preparation rather than creating a runnable case if a required field would need an unsupported or invented value. The report must state the exact source gap.
- [ ] Add tests that verify source hashes, no writes to source directories, explicit proxy roles, and no duplicate outputs under an existing attempt.
- [ ] Run focused preparation tests, then inspect all four manifests and source hashes.

### Task 5: Run each viable case through the application

**Files:**
- Update: `docs/audit/user-journey-20261021/full-goal-acceptance-20261027.md`
- Preserve raw logs and outputs under: `build/proxy-engineering-20261027/<lake>/`

- [ ] For every prepared case, use the standard application path: select/open case, inspect inputs, preflight/build, run, monitor progress/terminal state, inspect result files, and open dashboard/2D/3D views.
- [ ] Require successful solver exit plus readable nonempty expected output files. Record process exit code, solver SHA-256, result paths/sizes/hashes, and UI-resource version.
- [ ] Mark each successful case `代理` for the engineering run and `未完成` for scientific validation. Mark any unbuildable/unrunnable case `未完成` with its exact blocker.
- [ ] Run current-source backend and frontend suites. Then perform full application walk-through against the generated cases and the application's remaining feature list.
- [ ] Verify the native desktop window loaded the final resources after the user-confirmed restart; do not claim synchronization from the IAB browser alone.

## Self-review

- Each design requirement maps to Tasks 1–5.
- The attempt is append-only and isolated; originals are not overwritten or deleted.
- Missing sources stop a case from being presented as a successful engineering run.
- A successful proxy run never changes the scientific-validation state from incomplete.
- `（待补充：参考图的具体路径或链接）` remains untouched in the main acceptance report.
