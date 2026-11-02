# Scientific Workbench and Foodweb UX Completion Plan

> **For agentic workers:** Follow the repository's GPT-6 Luna implementation assignment. Sol owns final review and acceptance.

**Goal:** Complete the approved light scientific workbench direction where it is still missing, and make foodweb edits easier to understand and reverse before applying them.

**Architecture:** Preserve the existing canvas-first result pages, grouped navigation, scientific controls, and foodweb transaction path. Add visible diet-row column labels and an explicit reset for the selected consumer/group that reconstructs rows from the currently loaded configuration; the reset changes only unsaved editor state and never sends a transaction.

**Tech Stack:** Existing HTML/CSS, vanilla JavaScript, Node `node:test` UI harness.

---

### Task 1: Add visible labels and reversible staged foodweb editing

**Files:**
- Modify: `3DWET/app/static/js/ecology_network.js`
- Modify: `3DWET/app/static/css/scientific_workspace.css` (shared neutral/teal/amber workbench tokens only if missing)
- Modify: `3DWET/tests/test_ecology_foodweb_ui.js`
- Modify: `3DWET/app/templates/index.html` (foodweb asset cache key and any missing stylesheet key)

- [ ] **Step 1: Add failing foodweb UI assertions**

  Extend the existing DOM harness to assert diet rows expose visible headers for prey, suffix, clearance (including units), and gut occupation, and that “restore current group” resets an edited/added row to the loaded server-backed configuration without issuing an API transaction.

- [ ] **Step 2: Run the focused check and confirm failure**

  Run: `node 3DWET/tests/test_ecology_foodweb_ui.js`

  Expected: FAIL because the editor has no visible row header or restore control.

- [ ] **Step 3: Implement the smallest editor change**

  Add a labeled consumer selector synchronized with the existing module selector, visible diet-row labels with the existing group-specific clearance unit, and a restore button that replaces the selected group’s staged rows with `foodwebRowsFor(currentNode, group)`. Keep save/revision/preview/apply semantics unchanged.

- [ ] **Step 4: Run focused checks**

  Run: `node 3DWET/tests/test_ecology_foodweb_ui.js` and `node --check 3DWET/app/static/js/ecology_network.js`.

  Expected: all existing and new foodweb assertions pass; no API call occurs on restore.

- [ ] **Step 5: Synchronize and inspect available service evidence**

  Check `/api/system/health`, `/api/run/status`, home-page asset versions, and the served JS/CSS SHA-256 against local files. Report the exact desktop/WebView reload limitation if native control is unavailable.

### Task 2: Confirm scientific-workbench styling coverage

**Files:**
- Inspect: `3DWET/app/static/css/scientific_workspace.css`, `3DWET/app/static/css/studio.css`, `3DWET/app/templates/index.html`
- Modify only if a concrete approved design requirement is absent.

- [ ] **Step 1: Compare existing implementation to the approved design**

  Confirm warm-neutral surfaces, teal visualization controls, amber non-color status cues, dense readable controls, visible focus, and responsive canvas/inspector layout. Do not rework already-present navigation, viewport, playback, or scientific labels.

- [ ] **Step 2: Add a focused failing assertion before any required style change**

  Add it to a UI style contract check only if inspection identifies a concrete absent design token/behavior; run it first and confirm the expected failure.

- [ ] **Step 3: Implement and verify only that gap**

  Preserve existing semantic status colors and scientific meaning. Run the focused UI check and relevant syntax/build check.

- [ ] **Step 4: Synchronize the desktop source**

  Verify the managed service health, served home asset version, and SHA-256 equality; describe any cached-template/native-window blocker without claiming visual acceptance.
