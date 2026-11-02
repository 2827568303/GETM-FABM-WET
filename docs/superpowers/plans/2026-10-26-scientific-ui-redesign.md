# Scientific Workbench UI and 3D Expression Implementation Plan

> **For agentic workers:** Execute the scoped changes with GPT-6 Luna (medium); keep integration and acceptance with Sol (high). Preserve unrelated dirty workspace changes.

**Goal:** Bring the 3DWET application shell, full icon family and triangular 3D display into a restrained, legible scientific workbench style while retaining the quantitative model palette and existing behavior.

**Architecture:** Keep the shell theme in `academic_ui.css`, all 58 stable SVG symbol IDs and their geometry in `studio_icons.js` plus the inline sprite in `index.html`, and numerical/model rendering semantics in `viz3d.js`. Do not change solver topology, input data or ecological configuration to achieve visual effects. Version the changed assets and validate with existing tests.

**Tech Stack:** HTML, CSS, vanilla JavaScript, inline SVG, Plotly.js, Node.js tests, Flask local source service.

---

## Files and responsibilities

- `docs/audit/user-journey-20261021/SCIENCE_UI_DESIGN_DIRECTION.md`: Sol's sourced visual direction and 3D rules.
- `3DWET/app/static/css/academic_ui.css`: application-shell palette, hierarchy, density, surface and component styling.
- `3DWET/app/static/js/studio_icons.js`: canonical drawings for the existing complete icon catalog; preserve the API and all 58 stable identifiers.
- `3DWET/app/templates/index.html`: inline sprite fallback definitions and cache-busting references only; preserve DOM IDs, navigation targets, copy and controls.
- `3DWET/app/static/js/viz3d.js`: display-only triangle network/depth cues; preserve scalar color mapping, model values, bed geometry and solver topology.
- Existing tests in `3DWET/tests/`: update brittle design assertions only when the new design deliberately changes the asserted stroke geometry; do not add tests unless required to cover a requested behavior.

## Task 1: Rework the application-shell finish

**Files:** Modify `3DWET/app/static/css/academic_ui.css`.

- [ ] Replace inconsistent/duplicated pale-green/ochre overrides with a compact token palette: mineral paper/stone surfaces, pale sage secondary panel, slate blue-green active accent, subdued ochre provenance/warning state, muted red error state, dark green-charcoal text.
- [ ] Remove decorative gradients, shadow stacks, excessive hero emphasis and pill-like treatments where current component rules reintroduce them; keep modest square corners, clear separators and consistent spacing.
- [ ] Keep selected/pressed/focus states distinguishable without relying on saturated color; keep high-chroma color limited to data/model rendering.
- [ ] Preserve readable contrast, focus outlines, narrow-screen rules and existing workflow/case semantics.
- [ ] Inspect the resulting stylesheet for duplicate selectors and check diff for unrelated changes.

## Task 2: Redraw every stable icon as one technical family

**Files:** Modify `3DWET/app/static/js/studio_icons.js`, `3DWET/app/templates/index.html`, `3DWET/app/static/css/academic_ui.css`.

- [ ] Redraw all 58 existing symbols with consistent 24-unit construction, optical size, line weight, square/precise terminals and scientific/tool semantics. Retain every ID and `StudioIcons` method; do not add a library/CDN dependency.
- [ ] Update inline sprite fallback paths to match the canonical JavaScript geometry, so icons remain coherent before/without dynamic path installation.
- [ ] Use one shell ink color; use the active slate accent only for selected navigation/tool state. Avoid emoji-like, playful, or filled toy imagery.
- [ ] Bump the icon script query version and update the existing icon contract test only if it asserts an intentionally changed style property.
- [ ] Run the existing icon and navigation compatibility tests.

## Task 3: Strengthen the triangular 3D display without changing scientific meaning

**Files:** Modify `3DWET/app/static/js/viz3d.js`; inspect current display trace construction before editing.

- [ ] Improve triangle/layer legibility at the normal viewport scale using controlled depth cues, continuous basin relief and restrained structural edge contrast; avoid dense decorative node clutter.
- [ ] Geometry lines may use muted neutral/slate luminance steps but must not encode model-variable values. Keep the selected variable's colorscale/colorbar as the only quantitative hue channel.
- [ ] Keep all display-only geometry out of solver/input topology. Preserve bathymetric data, per-vertex intensity, wet-mask handling and existing user caveats about visual offsets/shading.
- [ ] Do not claim a black-bed fix or modify bed rendering speculatively; the original black patch is not currently reproducible in the recorded frame-19 comparisons and its cause remains uncertain.
- [ ] Bump `viz3d.js` query version and run existing visualization regression tests.

## Task 4: Source synchronization and acceptance

**Files:** `3DWET/app/templates/index.html`, the live source service on `127.0.0.1:52812`.

- [ ] Confirm the service is still serving the repository's `3DWET` source and check the root HTML asset query versions plus served CSS/JS bytes against disk.
- [ ] Do not reopen the desktop app or start/clean any model cases. If the existing desktop window cannot be proven to have hot-reloaded, report that boundary separately; do not equate a live HTTP asset match with a native-window visual check.
- [ ] Sol runs the existing icon/navigation, food-web UI and 3D visualization regression suites and `git diff --check` after Luna's changes.
- [ ] Add a concise evidence entry to `docs/audit/user-journey-20261021/STATUS.md` recording which automated proxies passed and whether native desktop visual acceptance remains unverified.
- [ ] Do not commit: the repository already contains extensive unrelated uncommitted tracked and untracked changes.

## Acceptance evidence

The complete 58-symbol catalog remains referenced and rendered through the stable API; shell uses the agreed non-monochrome restrained palette; model color remains quantitative; triangle geometry reads clearly without asserting physical meaning; navigation and interaction contract tests pass; the running source service returns the changed source bytes. Black-bed repair, full end-to-end user flow, and all four lake science validations remain separate gates and must retain their current **未完成** status until stronger evidence is available.
